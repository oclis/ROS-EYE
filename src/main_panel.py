import bpy

from bpy.types import Operator

from bl_ui_label import * 
from bl_ui_button import *
from bl_ui_checkbox import *
from bl_ui_slider import *
from bl_ui_up_down import *
from bl_ui_drag_panel import *
from bl_ui_draw_op import *
from bl_urx import *

#from class_py_serial import py3_serial
#ser = py3_serial() #10/30
#ser.run_rx()       #10/30

lMotions = []  # basic motion location
rMotions = []  # motion roation euler
mListCount = 0  # motion list count

class main_panel(BL_UI_OT_draw_operator):
    
    bl_idname = "object.main_panel"
    bl_label = "Robot control panel"
    bl_description = "Demo operator for bl ui widgets" 
    bl_options = {'REGISTER'}
    	
    def __init__(self):    
        print('main_panel __init__')
            
        self.panel = BL_UI_Drag_Panel(100, 100, 300, 300) #10/30580)#450
        self.panel.bg_color = (0.2, 0.2, 0.2, 0.9)

        self.label = BL_UI_Label(60, 10, 140, 25)
        self.label.text = "Robot::Controller "
        self.label.text_size = 24
        self.label.text_color = (0.6, 0.9, 0.3, 1.0)

        self.runBT = BL_UI_Button(20, 50, 150, 30)
        self.runBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.runBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.runBT.text = "Robot Run"
        self.runBT.set_image("//img/scale.png")
        self.runBT.set_image_size((24,24))
        self.runBT.set_image_position((4,2))
        self.runBT.set_mouse_down(self.runBT_press)
         
        self.simBT = BL_UI_Button(20, 90, 150, 30)
        self.simBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.simBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.simBT.text = "Simulation"
        self.simBT.set_image("//img/rotate.png")
        self.simBT.set_image_size((24,24))
        self.simBT.set_image_position((4,2))
        self.simBT.set_mouse_down(self.simBT_press)

        self.label_poseList = BL_UI_Label(20, 140, 200, 15)
        self.label_poseList.text = "Pose Count [ 0 ]"
        self.label_poseList.text_size = 16

        self.label_poseNo = BL_UI_Label(20, 162, 40, 15)
        self.label_poseNo.text = "Pose NO:"
        self.label_poseNo.text_size = 16

        self.up_down = BL_UI_Up_Down(120, 165)
        self.up_down.color = (0.2, 0.8, 0.8, 0.8)
        self.up_down.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.up_down.min = 1.0
        self.up_down.max = 5.0
        self.up_down.decimals = 0
        self.up_down.set_value(mListCount)
        self.up_down.set_value_change(self.on_up_down_value_change)

        self.originBT = BL_UI_Button(200, 90, 80, 30)
        self.originBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.originBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.originBT.text = "origin"
        self.originBT.set_mouse_down(self.originBT_press)  

        self.setPoseBT = BL_UI_Button(200, 160, 80, 30)
        self.setPoseBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.setPoseBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setPoseBT.text = "set"
        self.setPoseBT.set_image("//img/rotate.png")
        self.setPoseBT.set_image_size((24,24))
        self.setPoseBT.set_image_position((4,2))
        self.setPoseBT.set_mouse_down(self.setPoseBT_press)      

        self.chb_visibility = BL_UI_Checkbox(20, 210, 100, 15)
        self.chb_visibility.text = "Active visible"
        self.chb_visibility.text_size = 14
        self.chb_visibility.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_visibility.is_checked = True
        self.chb_visibility.set_state_changed(self.on_chb_visibility_state_change)

        self.chb_1 = BL_UI_Checkbox(20, 235, 100, 15)
        self.chb_1.text = "Pose View"
        self.chb_1.text_size = 14
        self.chb_1.text_color = (0.2, 0.9, 0.9, 1.0)

        self.chb_2 = BL_UI_Checkbox(20, 260, 100, 15)
        self.chb_2.text = "Path View"
        self.chb_2.text_size = 14
        self.chb_2.text_color = (0.2, 0.9, 0.9, 1.0)
        #10/30
        #Serial object
#        global ser
#        self.ser = ser
        #Run Deamon for Serial-rx
        
#        if self.ser.isRunning() == True:
#            print("serial-port: Normal operation")
#        else:
#            print("serial-port: closed")
#            print("serial-port: try to create new connection")
#            self.ser.run_rx()    
        
        #UI for Serial-tx
        self.line = BL_UI_Label(20, 310, 260, 10)
        self.line.color = (0.2, 0.8, 0.8, 0.8)
        self.line.text = "Griper Control"
        self.line.text_size = 16
        #grip-massage RUN
        self.setGripRunBT = BL_UI_Button(20, 330, 120, 30)
        self.setGripRunBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.setGripRunBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setGripRunBT.text = "Run"#"Open"
        self.setGripRunBT.set_image("//img/rotate.png")
        self.setGripRunBT.set_image_size((24,24))
        self.setGripRunBT.set_image_position((4,2))
        self.setGripRunBT.set_mouse_down(self.setGripRun_press)   
        #grip-massage STOP
        self.setGripStopBT = BL_UI_Button(160, 330, 120, 30)
        self.setGripStopBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.setGripStopBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setGripStopBT.text = "Stop"#"Close"
        self.setGripStopBT.set_image("//img/rotate.png")
        self.setGripStopBT.set_image_size((24,24))
        self.setGripStopBT.set_image_position((4,2))
        self.setGripStopBT.set_mouse_down(self.setGripStop_press)   
        #grip-massage LIST
        self.label_gripList = BL_UI_Label(20, 380, 200, 15)
        self.label_gripList.text = "Massage Program"#"Colum Lift"
        self.label_gripList.text_size = 16
        #grip-massage SELECT
        self.label_gripNo = BL_UI_Label(20, 402, 40, 15)#
        self.label_gripNo.text = "Program:"#
        self.label_gripNo.text_size = 16#
        #grip-massage MIN
        self.chb_select_1 = BL_UI_Checkbox(20, 405, 100, 15)
        self.chb_select_1.text = "MIN"#"Stop"
        self.chb_select_1.text_size = 14
        self.chb_select_1.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_1.is_checked = True
        self.chb_select_1.set_mode(1)
        self.chb_select_1.set_mouse_down(self.mode_select_1)
        #grip-massage MID
        self.chb_select_2 = BL_UI_Checkbox(120, 405, 100, 15)
        self.chb_select_2.text = "MID"#"Up"
        self.chb_select_2.text_size = 14
        self.chb_select_2.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_2.is_checked = False
        self.chb_select_2.set_mode(2)
        self.chb_select_2.set_mouse_down(self.mode_select_2)
        #grip-massage MAX
        self.chb_select_3 = BL_UI_Checkbox(220, 405, 100, 15)
        self.chb_select_3.text = "MAX"#"Down"
        self.chb_select_3.text_size = 14
        self.chb_select_3.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_3.is_checked = False
        self.chb_select_3.set_mode(3)
        self.chb_select_3.set_mouse_down(self.mode_select_3)

        #grip-massage SELECT-up
        self.up_down_2 = BL_UI_Up_Down(120, 405)#
        self.up_down_2.color = (0.2, 0.8, 0.8, 0.8)#
        self.up_down_2.hover_color = (0.2, 0.9, 0.9, 1.0)#
        self.up_down_2.min = 1.0#
        self.up_down_2.max = 3.0#
        self.up_down_2.decimals = 0#
        #grip-massage SELECT-down
        self.up_down_2.set_value(3.0)#
        self.up_down_2.set_value_change(self.on_up_down_value_change)#

        #grip-torque ON/OFF
        self.setTorqueBT = BL_UI_Button(20, 440, 120, 30)
        self.setTorqueBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.setTorqueBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setTorqueBT.text = "Torque On/Off"
        self.setTorqueBT.set_image("//img/rotate.png")
        self.setTorqueBT.set_image_size((24,24))
        self.setTorqueBT.set_image_position((4,2))
        self.setTorqueBT.set_mouse_down(self.setTorque_press)
        #grip-torque STATE
        self.label_torqueState = BL_UI_Label(160, 445, 200, 15)
        self.label_torqueState.text = "Torque On"
        self.label_torqueState.text_size = 15
 #10/30        self.ser.set_torqueState(self.print_torqueState)
        #grip-board RESET
        self.setBoardResetBT = BL_UI_Button(20, 480, 120, 30)
        self.setBoardResetBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.setBoardResetBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setBoardResetBT.text = "Reset"
        self.setBoardResetBT.set_image("//img/rotate.png")
        self.setBoardResetBT.set_image_size((24,24))
        self.setBoardResetBT.set_image_position((4,2))
        self.setBoardResetBT.set_mouse_down(self.setBoardReset_press)
        #grip-board STATE
        self.label_boardState = BL_UI_Label(160, 485, 200, 15)
        self.label_boardState.text = "connect succes"
        self.label_boardState.text_size = 15
 #10/30        self.ser.set_boardState(self.print_boardState)
        #grip-pose INIT
        self.setGripInitBT = BL_UI_Button(20, 520, 120, 30)
        self.setGripInitBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.setGripInitBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setGripInitBT.text = "HOME"
        self.setGripInitBT.set_image("//img/rotate.png")
        self.setGripInitBT.set_image_size((24,24))
        self.setGripInitBT.set_image_position((4,2))
        self.setGripInitBT.set_mouse_down(self.setGripInit_press)
        #grip-pose STATE
        self.label_poseState = BL_UI_Label(160, 525, 200, 15)
        self.label_poseState.text = "pose"
        self.label_poseState.text_size = 15
 #10/30        self.ser.set_poseState(self.print_poseState)

    def set_widget_events(self, event):
        result = False
        for widget in self.widgets:
            if widget.handle_event(event):
                result = True
        return result    

    def on_invoke(self, context, event):
        print('main_panel on invoke')
        # Add new widgets here (TODO: perhaps a better, more automated solution?)
        widgets_panel  = [self.label, self.label_poseNo, self.label_poseList, self.runBT, self.simBT, self.setPoseBT,self.originBT, self.up_down, self.chb_visibility, self.chb_1, self.chb_2]
        widgets        = [self.panel]

        widgets += widgets_panel
        self.init_widgets(context, widgets)
        self.panel.add_widgets(widgets_panel)
        # Open the panel at the mouse location
        self.panel.set_location(event.mouse_x, 
                                context.area.height - event.mouse_y + 20)
       

    def on_chb_visibility_state_change(self, checkbox, state):
        active_obj = bpy.context.view_layer.objects.active
        if active_obj is not None:
            active_obj.hide_viewport = not state
   

    def on_up_down_value_change(self, up_down, value):
#        setPoseState(value)
        print("change value")

    # robot run   
    def runBT_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(0)

    def simBT_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(1)
#.........#.........#.........#.........#.........#.........#.........
    def originBT_press(self, widget):
        print(" '{0}' is pressed".format(widget.text))
        angles = (0, -90, 0, -90, 0, 0)
        URxMoveToPoseAngle(angles)       
                
    def addCurPose2ML(self, count_v):
        pass
        # print("Motion count ".append(count_v))
        # ev[0] = bpy.data.objects['IK Target'].location[0]
        # ev[1] = bpy.data.objects['IK Target'].location[1]
        # ev[2] = bpy.data.objects['IK Target'].location[2]
        # lMotions.append(ev)
        # rv[0] = bpy.data.objects['IK Target'].rotation_euler[0]
        # rv[1] = bpy.data.objects['IK Target'].rotation_euler[1]
        # rv[2] = bpy.data.objects['IK Target'].rotation_euler[2]       
        # rMotions.append(rv)
        # count_v += 1

    def setPoseState(self, state):
        print("state '{0}' is pressed".format(state))
        bpy.data.objects['IK Target'].location = lMotions[state]
        bpy.data.objects['IK Target'].rotation_euler = rMotions[state]

#.........#.........#.........#.........#.........#.........#.........

    def setPoseBT_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.label_poseList.text = "Pose Count [ '{0}']".format(mListCount)
        #addCurPose2ML(1)

    def setGripRun_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        #self.ser.run_CMD('g',0)#self.ser.run_CMD('s',0)

    def setGripStop_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        #self.ser.run_CMD('g',1)#self.ser.run_CMD('e')

    def setTorque_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        # if self.label_torqueState.text == "Torque On":
        #     self.ser.run_CMD('t', 0)    
        # elif self.label_torqueState.text == "Torque Off":
        #     self.ser.run_CMD('t', 1)    

    def setBoardReset_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        # self.ser.run_CMD('r')

    def setGripInit_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        # self.ser.run_CMD('h')

    def print_torqueState(self, ser):
        # if self.ser._torqueState == True:
        #     self.label_torqueState.text = "Torque On"
        # else:
        #     self.label_torqueState.text = "Torque Off"
        pass
        

    def print_boardState(self, ser):
        # if self.ser._boardState == True:
        #     self.label_boardState.text = "connect succes"
        # else:
        #     self.label_boardState.text = "connecting"
        pass

    def print_poseState(self, ser):
        # if self.ser._poseState == True:
        #     self.label_poseState.text = "home"
        # else:
        #     self.label_poseState.text = "pose"
        pass

    def mode_select_1(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_1.is_checked == False:
            self.chb_select_1.is_checked = True
            self.chb_select_2.is_checked = False
            self.chb_select_3.is_checked = False
            print("send_1")
            #self.ser.run_CMD('h',0)#self.ser.run_CMD('p',1)

    def mode_select_2(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_2.is_checked == False:
            self.chb_select_1.is_checked = False
            self.chb_select_2.is_checked = True
            self.chb_select_3.is_checked = False
            print("send_2")
            #self.ser.run_CMD('h',2)#self.ser.run_CMD('p',2)

    def mode_select_3(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_3.is_checked == False:
            self.chb_select_1.is_checked = False
            self.chb_select_2.is_checked = False
            self.chb_select_3.is_checked = True
            print("send_3")
            #self.ser.run_CMD('h',1)#self.ser.run_CMD('p',3)