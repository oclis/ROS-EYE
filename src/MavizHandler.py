import bpy
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(('~')))+'/src')

from maviz import *
from RealSense import *

from bl_ui_load import *
from bl_ui_save import *
from bl_ui_draw_pose import Bl_Ui_Draw_Pose_Operator
from bl_ui_draw_panel_menu import Bl_Ui_Draw_Panel_Menu as budpm
from bl_ui_ctl_armature import Bl_Ui_Ctl_Armature as buca

from bl_op_server import *
from bl_op_flag import Bl_Op_Flag as bof
from bl_op_data import Bl_Op_Data as bod


# Thread #################################################
class MavizHandler(bpy.types.Operator):

    bl_idname = "wm.maviz_handler"
    bl_label = "Maviz Handler"
    update_rate = 1 / 30
    _loading_screen_obj = bpy.data.objects['loading']
    _waiting_timer = 1
    _motion_timer = 0
    _delay_time = 40
    _modal_action = None
    _timer = None
    instance = None
    sensor_cam = None
    mpanel = None

    # -------ur-variables-----------
    ur_Pose_Lists = []
    ur_Locations = []
    ur_Rotations = []
    ur_Move_Times = []
    ur_Move_Radius = []
    ur_Gripper_Motions = []

    # -------mode-variables---------
    sensor_cam_mode = False
    robot_tcp_mode = False
    shutdown_call = False
    # -------------------------------

    def __init__(self):
        self.modeAuto = False
        self.modeManu = False
        self.stateUrRun = False

    def init_widgets(self, context, widgets):
        self.widgets = widgets
        for widget in self.widgets:
            widget.init(context)

    def init_widgets2(self, context, widgets):
        self.widgets2 = widgets
        for widget in self.widgets2:
            widget.init(context)

    def draw_callback_px(self, op, context):
        for widget in self.widgets:
            widget.draw()
        for widget in self.widgets2:
            widget.draw()

    def execute(self, context):
        self.draw_handle = None
        self.draw_event = None
        self.widgets = []
        self.widgets2 = []

        wm = context.window_manager
        args = (self, context)
        self.register_handlers(args, context)
        self._timer = wm.event_timer_add(self.update_rate, window=context.window)
        wm.modal_handler_add(self)
        self._modal_action = self._update_waiting

        self.panel = BL_UI_Drag_Panel(0, 0, 320, 800)
        self.panel.bg_color = (0.2, 0.2, 0.2, 0.9)

        widgets = [self.panel]
        self.widgets_panel = budpm()
        widgets_Panel_Left = self.widgets_panel.draw_Menu_Left()
        widgets += widgets_Panel_Left
        self.init_widgets(context, widgets)
        self.panel.add_widgets(widgets_Panel_Left)
        self.panel.set_location(100, 100)

        self.panel2 = BL_UI_Drag_Panel(0, 0, 320, 600)
        self.panel2.bg_color = (0.2, 0.2, 0.2, 0.9)

        widgets2 = [self.panel2]
        widgets_Panel_Right = self.widgets_panel.draw_Menu_Right()
        widgets2 += widgets_Panel_Right

        self.init_widgets2(context, widgets2)
        self.panel2.add_widgets(widgets_Panel_Right)
        self.panel2.set_location(1500, 100)

        return {'RUNNING_MODAL'}

    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None
        self.draw_event = None

    def modal(self, context, event):
        if event.type == 'ESC':
            if self.widgets_panel.RobotConCHK.is_checked == False:
                self.ur_Locations = []
                self.ur_Rotations = []
                self.ur_Move_Times = []
                self.ur_Move_Radius = []
                self.ur_Gripper_Motions = []
                URxMoveToPoseOperator(6)
                Bl_Ui_Draw_Pose_Operator(0)
                self.stateUrRun = False
                bof.FLAG_OP_SHUTDOWN = True

        self._run()
        # buca.draw_Curr_Ur_FK() # Use UR5 in simulator

        if bof.FLAG_OP_SHUTDOWN:
            self._cancel(context)
            self.unregister_handlers(context)
            cleanup_and_quit()
            return {'CANCELLED'}

        elif event.type == 'TIMER':
            self._modal_action()

        for widget in self.widgets:
            rtn = widget.handle_event(event)

        for widget in self.widgets2:
            rtn = widget.handle_event(event)
        
        if self.instance is not None:
           self.instance.set_event(event, context)
        
        if self.sensor_cam is not None and self.sensor_cam_mode:
            self.sensor_cam.processing()

        if "ROBOT" in bod.data_Tcp_Clinet_List:
            self.widgets_panel.RobotConCHK.is_checked = True
        else:
            self.widgets_panel.RobotConCHK.is_checked = False
            
        bpy.context.view_layer.update()
        if rtn:
            print('redraw')

        return {'RUNNING_MODAL'}


    def _cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        if self.sensor_cam is not None:
            self.sensor_cam.closeSense()

    def _update_waiting(self):
        self._waiting_timer -= self.update_rate
        if self._waiting_timer <= 0:
            self._initialize()
            bpy.ops.screen.animation_play()
            self._modal_action = self._update_running

    def _run(self):
        self._check_Robot_Job()
        if self._motion_timer > 0:
            self._motion_timer -= 1

        leftCnt = len(self.ur_Locations)
        if self.ur_Locations and self._motion_timer == 0:
            self.instance.setMover(self.ur_Locations.pop(),self.ur_Rotations.pop())
            if self.widgets_panel.RobotConCHK.is_checked == True:
                bpy.context.view_layer.update()
                try:
                    pop_Move_Time = self.ur_Move_Times.pop()
                    pop_Move_Radius = self.ur_Move_Radius.pop()
                    pop_Gripper_Motion = self.ur_Gripper_Motions.pop()
                except Exception as e:
                    print(e)
                    pop_Move_Time = 0
                    pop_Move_Radius = 0
                    pop_Gripper_Motion = 0
                URxMoveToPoseOperator(1, pop_Move_Time, pop_Move_Radius, pop_Gripper_Motion)
            else:
                print("Check Robot conn")

            if len(self.ur_Locations) == 0 and len(self.ur_Gripper_Motions) == 0:
                URxStateCheck(0)
                self.stateUrRun = False
                Bl_Ui_Draw_Pose_Operator(0)
                if self.widgets_panel.RobotConCHK.is_checked == True:
                    URxMoveToPoseOperator(0)

            if leftCnt > 0:
                self._motion_timer = int(self._delay_time * self.widgets_panel.SpeedUD.get_value())

    def _check_Robot_Job(self):
        try:
            if (bod.robot1.robot_Job.empty() == False):
                job_Data = bod.robot1.robot_Job.get()
                self.ur_Pose_Lists = job_Data.job_Pose_List
                self.ur_Move_Times = job_Data.job_Move_Times
                self.ur_Move_Radius = job_Data.job_Move_Radius
                self.ur_Gripper_Motions = job_Data.job_Gripper_Motions

                for i in range(0, len(self.ur_Pose_Lists), 1):
                    loc = self.ur_Pose_Lists[i].location
                    rot = self.ur_Pose_Lists[i].rotation_euler
                    self.ur_Locations.append(loc)
                    self.ur_Rotations.append(rot)
                self._motion_timer = 10
        except Exception as e:
            print("_check_Robot_Job : ",e)

    def _initialize(self):
        print('init')
        instance = Maviz(
            item=Maviz.setup_item("Area1"),
            mover=Maviz.setup_ik_mover("Area2", "ik_control")
        )
        self.instance = instance
        self._loading_screen_obj.hide_viewport = True

    def _realsenseInit(self):
        print('realsense start')
        try:
            senser = RealSense()
            self.sensor_cam = senser
            self.sensor_cam.calibaration()
            self.sensor_cam.setEmitter()
        except:
            if self.sensor_cam is not None:
                self.sensor_cam.closeSense()
            self.sensor_cam = None
            print('realsense error')

    def _update_running(self):
        self.instance.update(self.update_rate)

##################################################
def cleanup_and_quit():
    unregister()
    bpy.ops.wm.quit_blender()


def register():
    bpy.utils.register_class(LoadEnumOperator)
    bpy.utils.register_class(DialogOperator)
    bpy.utils.register_class(MavizHandler)


def unregister():
    bpy.utils.unregister_class(LoadEnumOperator)
    bpy.utils.unregister_class(DialogOperator)
    bpy.utils.unregister_class(MavizHandler)


def setup_workspace():
    print('setup workspace')
    window = bpy.context.window_manager.windows[0]
    screen = window.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            space.shading.type = 'RENDERED'
            override = {'window': window, 'screen': screen, 'area': area}
            bpy.ops.screen.screen_full_area(override, use_hide_panels=True)
            break

def main():
    setup_workspace()
    register()
    bpy.ops.wm.maviz_handler()

if __name__ == "__main__":
    main()

# 민경철
