import pathlib
import random
import tempfile

import bpy
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from bpy.types import Operator

from bl_ui_label import *
from bl_ui_button import *
from bl_ui_checkbox import *
from bl_ui_slider import *
from bl_ui_up_down import *
from bl_ui_drag_panel import *
from bl_ui_draw_op import *
from maviz import *
from bl_urx import *
from bl_urx_server import *
from main_panel import *
from RealSense import *
from bl_ui_Search import * # =============================================================> bl_ui_Search / sw
from bl_ui_Save import * # =============================================================> bl_ui_Save / sw

mListCount = 0  # motion list count
pListCount = 0  # 데이터 폴더에 있는 데이터 리스트 중 로드할 넘버 카운트
urAccel = 0     # ur 가속 값 저장
urVelo = 0      # ur 속도 값 저장
urMoveTime = 0
urMoveRadius = 0

# Thread #################################################3
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
    lMotions = []
    gMotions = []
    urMoveTimes = []
    urMoveRadius = []
    # -------mode-variables---------
    sensor_cam_mode = False
    robot_tcp_mode = False
    shutdown_call = False
    # -------------------------------

    def __init__(self):
        self.modeAuto = False
        self.modeManual = False
        self.stateUrRun = False
        self.Language_FLAG = False
        self.Admin_MENU_FLAG = False

    def init_widgets(self, context, widgets):
        self.widgets = widgets
        for widget in self.widgets:
            widget.init(context)

    def init_widgets2(self, context, widgets):
        self.widgets2 = widgets
        for widget in self.widgets2:
            widget.init(context)

# ============================================================================================================================== #

    def init_widgets3(self, context, widgets): # =======================================> Slider / sw
        self.widgets3 = widgets
        for widget in self.widgets3:
            widget.init(context)

    def draw_callback_px(self, op, context):
        for widget in self.widgets:
            widget.draw()
        for widget in self.widgets2:
            widget.draw()
        if (self.Admin_MENU_FLAG == True):
            for widget in self.widgets3: # =======================================> Slider / sw
                widget.draw()

    def execute(self, context):
        self.draw_handle = None
        self.draw_event = None
        self.widgets = []  # widget group 1
        self.widgets2 = []  # widget group 2
        self.widgets3 = []  # widget group 3 # =======================================> Slider / sw

        wm = context.window_manager
        args = (self, context)
        self.register_handlers(args, context)
        self._timer = wm.event_timer_add(self.update_rate, window=context.window)
        wm.modal_handler_add(self)
        self._modal_action = self._update_waiting

        self.panel3 = BL_UI_Drag_Panel(0, 0, 200, 200)
        self.panel3.bg_color = (0.2, 0.2, 0.2, 0.9)

        self.WinLable3 = BL_UI_Label(10, 10, 200, 25)
        self.WinLable3.text = "Slider Position"
        self.WinLable3.text_size = 24
        self.WinLable3.text_color = (0.6, 0.9, 0.3, 1.0)

        # self.Choice = SearchEnumOperator(bpy.types.Operator)

        # self.bl_ui_slider = BL_UI_Slider(20, 70, 165, 15)
        # self.bl_ui_slider.color = (0.2, 0.8, 0.8, 0.8)
        # self.bl_ui_slider.hover_color = (0.2, 0.9, 0.9, 1.0)
        # self.bl_ui_slider.min = 1.0
        # self.bl_ui_slider.max = 10.0
        # self.bl_ui_slider.decimals = 0 # =========================> 소수점 아래 몇 번째까지 출력할 것인지
        # self.bl_ui_slider.set_value(3)

        self.label_urMoveTimeNum = BL_UI_Label(20, 45, 40, 15)
        self.label_urMoveTimeNum.text = "Time :"
        self.label_urMoveTimeNum.text_size = 16

        self.bl_ui_slider_Time = BL_UI_Slider(25, 80, 140, 15)  # =================================> Time_slider
        self.bl_ui_slider_Time.color = (0.2, 0.8, 0.8, 0.8)
        self.bl_ui_slider_Time.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.bl_ui_slider_Time.min = 0.0
        self.bl_ui_slider_Time.max = 10.0
        self.bl_ui_slider_Time.decimals = 0
        self.bl_ui_slider_Time.set_value(1)
        self.bl_ui_slider_Time.set_value(urMoveTime)
        self.bl_ui_slider_Time.set_value_change(self.Time_Sliding_value_Change)

        self.label_urMoveRadiusNum = BL_UI_Label(20, 110, 40, 15)
        self.label_urMoveRadiusNum.text = "Radius :"
        self.label_urMoveRadiusNum.text_size = 16

        self.bl_ui_slider_Radius = BL_UI_Slider(25, 145, 140, 15)  # =================================> Radius_slider
        self.bl_ui_slider_Radius.color = (0.2, 0.8, 0.8, 0.8)
        self.bl_ui_slider_Radius.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.bl_ui_slider_Radius.min = 0.0
        self.bl_ui_slider_Radius.max = 10.0
        self.bl_ui_slider_Radius.decimals = 0
        self.bl_ui_slider_Radius.set_value(1)
        self.bl_ui_slider_Radius.set_value(urMoveRadius)
        self.bl_ui_slider_Radius.set_value_change(self.Radius_Sliding_value_Change)

        widgets_panel3 = [self.WinLable3, self.label_urMoveTimeNum, self.bl_ui_slider_Time, self.label_urMoveRadiusNum,
                          self.bl_ui_slider_Radius]  # , self.bl_ui_slider

        widgets3 = [self.panel3]
        widgets3 += widgets_panel3

        self.init_widgets3(context, widgets3)
        self.panel3.add_widgets(widgets_panel3)
        self.panel3.set_location(430, 100)

# ============================================================================================================================== #

        # left panel
        self.panel = BL_UI_Drag_Panel(0, 0, 320, 800)
        self.panel.bg_color = (0.2, 0.2, 0.2, 0.9)

        self.WinLable = BL_UI_Label(10, 10, 200, 25)
        self.WinLable.text = "MAVIZ | UR5 "
        self.WinLable.text_size = 24
        self.WinLable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Switch_Kor = BL_UI_Button(230, 15, 30, 30)  # ===========> 적용됨
        self.Switch_Kor.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Switch_Kor.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Switch_Kor.text = "한"
        # self.Auto_Button.set_image("//img/gray_play.png")
        self.Switch_Kor.set_image_size((24, 24))
        self.Switch_Kor.set_image_position((4, 2))
        self.Switch_Kor.set_mouse_down(self.Eng_to_Kor)

        self.Switch_Eng = BL_UI_Button(270, 15, 30, 30)  # ===========> 적용됨
        self.Switch_Eng.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Switch_Eng.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Switch_Eng.text = "영"
        # self.Auto_Button.set_image("//img/gray_play.png")
        self.Switch_Eng.set_image_size((24, 24))
        self.Switch_Eng.set_image_position((4, 2))
        self.Switch_Eng.set_mouse_down(self.Kor_to_Eng)

        self.Auto_Button = BL_UI_Button(20, 55, 135, 50)  # ===========> 적용됨
        self.Auto_Button.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Auto_Button.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Auto_Button.text = "Auto"
        # self.Auto_Button.set_image("//img/gray_play.png")
        self.Auto_Button.set_image_size((24, 24))
        self.Auto_Button.set_image_position((4, 2))
        self.Auto_Button.set_mouse_down(self.modeChangeAuto)

        self.Manual_Button = BL_UI_Button(165, 55, 135, 50)
        self.Manual_Button.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Manual_Button.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Manual_Button.text = "Manual"
        # self.Manual_Button.set_image("//img/gray_play.png")
        self.Manual_Button.set_image_size((24, 24))
        self.Manual_Button.set_image_position((4, 2))
        self.Manual_Button.set_mouse_down(self.modeChangeManu)

        self.SpeedText = BL_UI_Label(20, 125, 150, 15)
        self.SpeedText.text = "Take Time"
        self.SpeedText.text_size = 16

        self.SpeedUD = BL_UI_Up_Down(35, 175)
        self.SpeedUD.color = (0.2, 0.8, 0.8, 0.8)
        self.SpeedUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.SpeedUD.min = 1.0
        self.SpeedUD.max = 10.0
        self.SpeedUD.decimals = 0
        self.SpeedUD.set_value(mListCount)
        # self.SpeedUD.set_value_change(self.speedValue_change)

        self.MotionRunA = BL_UI_Button(120, 120, 180, 80)
        self.MotionRunA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.MotionRunA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.MotionRunA.text = "Run"
        self.MotionRunA.text_size = 32
        # self.MotionRunB.set_image("//img/gray_r.png")
        self.MotionRunA.set_image_size((24, 24))
        self.MotionRunA.set_image_position((4, 2))
        self.MotionRunA.set_mouse_down(self.motionRunB_call)

        self.RobotHomePA = BL_UI_Button(20, 220, 280, 50)
        self.RobotHomePA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.RobotHomePA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.RobotHomePA.text = "Home Position"
        # self.RobotHomePA.set_image("//img/gray_play.png")
        self.RobotHomePA.set_image_size((24, 24))
        self.RobotHomePA.set_image_position((4, 2))
        self.RobotHomePA.set_mouse_down(self.moveHomeB_call)

        self.Motionremv = BL_UI_Button(20, 280, 280, 50)
        self.Motionremv.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Motionremv.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Motionremv.text = "Motion Delete"
        # self.Motionremv.set_image("//img/gray_play.png")
        self.Motionremv.set_image_size((24, 24))
        self.Motionremv.set_image_position((4, 2))
        self.Motionremv.set_mouse_down(self.motionDelB_call)

        self.Gripper_ON = BL_UI_Button(20, 340, 135, 35)
        self.Gripper_ON.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Gripper_ON.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Gripper_ON.text = "Gripper On"
        self.Gripper_ON.set_image_position((4, 2))
        self.Gripper_ON.set_mouse_down(self.gripperOn)

        self.Gripper_OFF = BL_UI_Button(165, 340, 135, 35)
        self.Gripper_OFF.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Gripper_OFF.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Gripper_OFF.text = "Gripper Off"
        self.Gripper_OFF.set_image_position((4, 2))
        self.Gripper_OFF.set_mouse_down(self.gripperOff)

        self.Teach_ModeA = BL_UI_Button(20, 385, 135, 35)
        self.Teach_ModeA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Teach_ModeA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Teach_ModeA.text = "Teach On"
        self.Teach_ModeA.set_image_position((4, 2))
        self.Teach_ModeA.set_mouse_down(self.setTeachModeB_call)

        self.Off_Teach_ModeA = BL_UI_Button(165, 385, 135, 35)
        self.Off_Teach_ModeA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Off_Teach_ModeA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Off_Teach_ModeA.text = "Teach Off"
        self.Off_Teach_ModeA.set_image_position((4, 2))
        self.Off_Teach_ModeA.set_mouse_down(self.setOffTeachModeB_call)

        self.VeloText_Left_Panel = BL_UI_Label(20, 435, 60, 20)
        self.VeloText_Left_Panel.color = (0.2, 0.8, 0.8, 0.8)
        self.VeloText_Left_Panel.text = "Velo"
        self.VeloText_Left_Panel.text_size = 20

        self.AccelText_Left_Panel = BL_UI_Label(20, 470, 60, 20)
        self.AccelText_Left_Panel.color = (0.2, 0.8, 0.8, 0.8)
        self.AccelText_Left_Panel.text = "Accel"
        self.AccelText_Left_Panel.text_size = 20

        self.veloUD = BL_UI_Up_Down(90, 440)
        self.veloUD.color = (0.2, 0.8, 0.8, 0.8)
        self.veloUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.veloUD.min = 1.0
        self.veloUD.max = 10.0
        self.veloUD.decimals = 0
        self.veloUD.set_value(1)  #
        self.veloUD.set_value(pListCount)
        self.veloUD.set_value_change(self.on_ur_velo_up_down_value_change)

        self.accelUD = BL_UI_Up_Down(90, 475)
        self.accelUD.color = (0.2, 0.8, 0.8, 0.8)
        self.accelUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.accelUD.min = 1.0
        self.accelUD.max = 10.0
        self.accelUD.decimals = 0
        self.accelUD.set_value(1)  #
        self.accelUD.set_value(pListCount)
        self.accelUD.set_value_change(self.on_ur_accel_up_down_value_change)

        self.Set_Ur_Velo_AccelA = BL_UI_Button(165, 435, 135, 60)
        self.Set_Ur_Velo_AccelA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Set_Ur_Velo_AccelA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Set_Ur_Velo_AccelA.text = "Set UR Speed"
        self.Set_Ur_Velo_AccelA.set_image_size((24, 24))
        self.Set_Ur_Velo_AccelA.set_image_position((4, 2))
        self.Set_Ur_Velo_AccelA.set_mouse_down(self.setVeloAccel)

        # grip-massage MIN
        self.chb_select_1 = BL_UI_Checkbox(20, 540, 100, 15)
        self.chb_select_1.text = "MIN"  # "Stop"
        self.chb_select_1.text_size = 14
        self.chb_select_1.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_1.is_checked = True
        self.chb_select_1.set_mode(1)
        self.chb_select_1.set_mouse_down(self.mode_select_1)
        # grip-massage MID
        self.chb_select_2 = BL_UI_Checkbox(130, 540, 100, 15)
        self.chb_select_2.text = "MID"  # "Up"
        self.chb_select_2.text_size = 14
        self.chb_select_2.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_2.is_checked = False
        self.chb_select_2.set_mode(2)
        self.chb_select_2.set_mouse_down(self.mode_select_2)
        # grip-massage MAX
        self.chb_select_3 = BL_UI_Checkbox(240, 540, 100, 15)
        self.chb_select_3.text = "MAX"  # "Down"
        self.chb_select_3.text_size = 14
        self.chb_select_3.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_3.is_checked = False
        self.chb_select_3.set_mode(3)
        self.chb_select_3.set_mouse_down(self.mode_select_3)

        # self.PoseDelA = BL_UI_Button(160, 590, 140, 30)
        # self.PoseDelA.bg_color = (0.2, 0.8, 0.8, 0.8)
        # self.PoseDelA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        # self.PoseDelA.text = "Del"
        # # self.PoseSetA2.set_image("//img/gray_r.png")
        # self.PoseDelA.set_image_size((24, 24))
        # self.PoseDelA.set_image_position((4, 2))

        self.addPoseA = BL_UI_Button(160, 590, 140, 30)  # =============================================================> 수정 / sw
        self.addPoseA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.addPoseA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.addPoseA.text = "Add"
        self.addPoseA.set_image_size((24, 24))
        self.addPoseA.set_image_position((4, 2))
        self.addPoseA.set_mouse_down(self.addCurrUrJointAngle)

        self.PoseSaveA = BL_UI_Button(160, 625, 140, 30)
        self.PoseSaveA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.PoseSaveA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.PoseSaveA.text = "Save"
        self.PoseSaveA.set_image_size((24, 24))
        self.PoseSaveA.set_image_position((4, 2))
        self.PoseSaveA.set_mouse_down(self.saveTPoseLists) # =============================================================> 수정 / sw
        # self.PoseSaveA.set_mouse_down(self.saveCurrUrJointAngle)

        self.PoseLoadA = BL_UI_Button(160, 660, 140, 30)
        self.PoseLoadA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.PoseLoadA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.PoseLoadA.text = "Load"
        self.PoseLoadA.set_image_size((24, 24))
        self.PoseLoadA.set_image_position((4, 2))
        # self.PoseLoadA.set_mouse_down(self.loadUrPoseLists) # =============================================================> 수정 / panel수정 요망 / sw
        self.PoseLoadA.set_mouse_down(self.loadUrPoseLists)

        self.AdminMenu = BL_UI_Button(20, 660, 120, 30)
        self.AdminMenu.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.AdminMenu.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.AdminMenu.text = "Admin"
        self.AdminMenu.set_image_size((24, 24))
        self.AdminMenu.set_image_position((4, 2))
        self.AdminMenu.set_mouse_down(self.CallAdminMenu)

        # self.label_ProgramNum = BL_UI_Label(20, 670, 40, 15)
        # self.label_ProgramNum.text = "Program :"
        # self.label_ProgramNum.text_size = 16
        #
        # self.programUD = BL_UI_Up_Down(100, 670)
        # self.programUD.color = (0.2, 0.8, 0.8, 0.8)
        # self.programUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        # self.programUD.min = 0.0
        # self.programUD.max = 100.0
        # self.programUD.decimals = 0
        # self.programUD.set_value(0)
        # self.programUD.set_value(pListCount)
        # self.programUD.set_value_change(self.on_program_up_down_value_change)

        # self.urMoveTimeUD = BL_UI_Up_Down(100, 610)
        # self.urMoveTimeUD.color = (0.2, 0.8, 0.8, 0.8)
        # self.urMoveTimeUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        # self.urMoveTimeUD.min = 0.0
        # self.urMoveTimeUD.max = 10.0
        # self.urMoveTimeUD.decimals = 0
        # self.urMoveTimeUD.set_value(0)  #
        # self.urMoveTimeUD.set_value(urMoveTime)
        # self.urMoveTimeUD.set_value_change(self.on_ur_move_time_up_down_value_change)
        #
        # self.label_urMoveTimeNum = BL_UI_Label(20, 610, 40, 15)
        # self.label_urMoveTimeNum.text = "Time :"
        # self.label_urMoveTimeNum.text_size = 16
        #
        # self.urMoveRadiusUD = BL_UI_Up_Down(100, 640)
        # self.urMoveRadiusUD.color = (0.2, 0.8, 0.8, 0.8)
        # self.urMoveRadiusUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        # self.urMoveRadiusUD.min = 0.0
        # self.urMoveRadiusUD.max = 10.0
        # self.urMoveRadiusUD.decimals = 0
        # self.urMoveRadiusUD.set_value(0)
        # self.urMoveRadiusUD.set_value(urMoveRadius)
        # self.urMoveRadiusUD.set_value_change(self.on_ur_move_radius_up_down_value_change)
        #
        # self.label_urMoveRadiusNum = BL_UI_Label(20, 640, 40, 15)
        # self.label_urMoveRadiusNum.text = "Radius :"
        # self.label_urMoveRadiusNum.text_size = 16



        self.setBoardResetBT = BL_UI_Button(20, 700, 280, 80)
        self.setBoardResetBT.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.setBoardResetBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setBoardResetBT.text = "STOP"
        self.setBoardResetBT.text_color = (1.0, 1.0, 1.0, 1.0)
        self.setBoardResetBT.text_size = 36
        # self.setBoardResetBT.set_image("//img/rotate.png")
        self.setBoardResetBT.set_image_size((24, 24))
        self.setBoardResetBT.set_image_position((4, 2))
        self.setBoardResetBT.set_mouse_down(self.emcStop_call)

        widgets_panel = [self.MotionRunA, self.WinLable, self.SpeedText, self.SpeedUD, self.RobotHomePA, self.Motionremv, self.Teach_ModeA, self.Off_Teach_ModeA, self.Gripper_ON, self.Gripper_OFF,
                         self.VeloText_Left_Panel, self.AccelText_Left_Panel, self.veloUD, self.accelUD, self.Set_Ur_Velo_AccelA, self.chb_select_1, self.chb_select_2, self.chb_select_3, self.addPoseA,
                          self.PoseSaveA, self.PoseLoadA, self.setBoardResetBT, self.Auto_Button, self.Manual_Button,
                         self.Switch_Eng, self.Switch_Kor, self.AdminMenu] # self.urMoveTimeUD, self.label_urMoveTimeNum, self.urMoveRadiusUD, self.label_urMoveRadiusNum, self.label_ProgramNum, self.programUD

        widgets = [self.panel]

        widgets += widgets_panel
        self.init_widgets(context, widgets)
        self.panel.add_widgets(widgets_panel)
        self.panel.set_location(100, 100)

        # righit 두번째 판넬
        self.panel2 = BL_UI_Drag_Panel(0, 0, 320, 600)
        self.panel2.bg_color = (0.2, 0.2, 0.2, 0.9)

        self.WinLable2 = BL_UI_Label(10, 10, 200, 25)
        self.WinLable2.text = "Information"
        self.WinLable2.text_size = 26
        self.WinLable2.text_color = (0.6, 0.9, 0.3, 1.0)

        self.CommLabel = BL_UI_Label(25, 50, 200, 25)
        self.CommLabel.text_color = (1.0, 1.0, 1.0, 1.0)
        self.CommLabel.text = "Communication "
        self.CommLabel.text_size = 20

        self.RobotText = BL_UI_Label(25, 90, 200, 25)
        self.RobotText.text = "Robot"
        self.RobotText.text_size = 20
        self.RobotText.text_color = (0.6, 0.9, 0.3, 1.0)

        self.CameraText = BL_UI_Label(220, 90, 200, 25)
        self.CameraText.text = "Camera"
        self.CameraText.text_size = 20
        self.CameraText.text_color = (0.6, 0.9, 0.3, 1.0)

        self.RobotConCHK = BL_UI_Checkbox(45, 130, 100, 15)
        self.RobotConCHK.text = ""
        self.RobotConCHK.text_size = 14
        self.RobotConCHK.text_color = (0.2, 0.9, 0.9, 1.0)
        self.RobotConCHK.is_checked = False


        self.CameraConCHK = BL_UI_Checkbox(250, 130, 100, 15)
        self.CameraConCHK.text = ""
        self.CameraConCHK.text_size = 14
        self.CameraConCHK.text_color = (0.2, 0.9, 0.9, 1.0)
        self.CameraConCHK.is_checked = False


        self.GripperText = BL_UI_Label(25, 200, 60, 20)
        self.GripperText.color = (0.2, 0.8, 0.8, 0.8)
        self.GripperText.text = "Gripper"
        self.GripperText.text_size = 20

        self.GripperText_ON = BL_UI_Label(165, 175, 60, 20)
        self.GripperText_ON.color = (0.2, 0.8, 0.8, 0.8)
        self.GripperText_ON.text = "ON"
        self.GripperText_ON.text_size = 16

        self.GripperText_OFF = BL_UI_Label(245, 175, 60, 20)
        self.GripperText_OFF.color = (0.2, 0.8, 0.8, 0.8)
        self.GripperText_OFF.text = "OFF"
        self.GripperText_OFF.text_size = 16

        self.GripperCHK_ON = BL_UI_Checkbox(170, 205, 100, 15)
        self.GripperCHK_ON.text = ""
        self.GripperCHK_ON.text_size = 14
        self.GripperCHK_ON.text_color = (0.2, 0.9, 0.9, 1.0)
        self.GripperCHK_ON.is_checked = False

        self.GripperCHK_OFF = BL_UI_Checkbox(250, 205, 100, 15)
        self.GripperCHK_OFF.text = ""
        self.GripperCHK_OFF.text_size = 14
        self.GripperCHK_OFF.text_color = (0.2, 0.9, 0.9, 1.0)
        self.GripperCHK_OFF.is_checked = True

        self.TeachModeText = BL_UI_Label(25, 265, 60, 20)
        self.TeachModeText.color = (0.2, 0.8, 0.8, 0.8)
        self.TeachModeText.text = "Teach Mode"
        self.TeachModeText.text_size = 20

        self.TeachModeText_ON = BL_UI_Label(165, 240, 60, 20)
        self.TeachModeText_ON.color = (0.2, 0.8, 0.8, 0.8)
        self.TeachModeText_ON.text = "ON"
        self.TeachModeText_ON.text_size = 16

        self.TeachModeText_OFF = BL_UI_Label(245, 240, 60, 20)
        self.TeachModeText_OFF.color = (0.2, 0.8, 0.8, 0.8)
        self.TeachModeText_OFF.text = "OFF"
        self.TeachModeText_OFF.text_size = 16

        self.TeachModeCHK_ON = BL_UI_Checkbox(170, 270, 100, 15)
        self.TeachModeCHK_ON.text = ""
        self.TeachModeCHK_ON.text_size = 14
        self.TeachModeCHK_ON.text_color = (0.2, 0.9, 0.9, 1.0)
        self.TeachModeCHK_ON.is_checked = False


        self.TeachModeCHK_OFF = BL_UI_Checkbox(250, 270, 100, 15)
        self.TeachModeCHK_OFF.text = ""
        self.TeachModeCHK_OFF.text_size = 14
        self.TeachModeCHK_OFF.text_color = (0.2, 0.9, 0.9, 1.0)
        self.TeachModeCHK_OFF.is_checked = True


        self.ModeStatusText = BL_UI_Label(25, 330, 60, 20)
        self.ModeStatusText.color = (0.2, 0.8, 0.8, 0.8)
        self.ModeStatusText.text = "Mode Status"
        self.ModeStatusText.text_size = 20

        self.ModeStatusText_Auto = BL_UI_Label(162, 310, 60, 20)
        self.ModeStatusText_Auto.color = (0.2, 0.8, 0.8, 0.8)
        self.ModeStatusText_Auto.text = "Auto"
        self.ModeStatusText_Auto.text_size = 14

        self.ModeStatusText_Manual = BL_UI_Label(232, 310, 60, 20)
        self.ModeStatusText_Manual.color = (0.2, 0.8, 0.8, 0.8)
        self.ModeStatusText_Manual.text = "Manual"
        self.ModeStatusText_Manual.text_size = 14

        self.ModeStatusCHK_Auto = BL_UI_Checkbox(170, 335, 100, 15)
        self.ModeStatusCHK_Auto.text = ""
        self.ModeStatusCHK_Auto.text_size = 14
        self.ModeStatusCHK_Auto.text_color = (0.2, 0.9, 0.9, 1.0)
        self.ModeStatusCHK_Auto.is_checked = False

        self.ModeStatusCHK_Manual = BL_UI_Checkbox(250, 335, 100, 15)
        self.ModeStatusCHK_Manual.text = ""
        self.ModeStatusCHK_Manual.text_size = 14
        self.ModeStatusCHK_Manual.text_color = (0.2, 0.9, 0.9, 1.0)
        self.ModeStatusCHK_Manual.is_checked = True

        self.VeloText = BL_UI_Label(25, 375, 60, 20)
        self.VeloText.color = (0.2, 0.8, 0.8, 0.8)
        self.VeloText.text = "Velo   :  0"
        self.VeloText.text_size = 20

        self.AccelText = BL_UI_Label(170, 375, 60, 20)
        self.AccelText.color = (0.2, 0.8, 0.8, 0.8)
        self.AccelText.text = "Accel  :  0"
        self.AccelText.text_size = 20

        self.PoseCountText = BL_UI_Label(25, 415, 160, 15)
        self.PoseCountText.text = f'Pose Count: 0 t=[0]'
        self.PoseCountText.text_size = 20

        self.JobCountText = BL_UI_Label(25, 445, 60, 20)
        self.JobCountText.color = (0.2, 0.8, 0.8, 0.8)
        self.JobCountText.text = "Job Reserve Count  : 0"
        self.JobCountText.text_size = 20

        self.ShutdownB = BL_UI_Button(20, 510, 280, 60)
        self.ShutdownB.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.ShutdownB.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.ShutdownB.text = "PROGRAM SHUTDOWN"
        self.ShutdownB.text_size = 22
        # self.ShutdownB.set_image("//img/rotate.png")
        self.ShutdownB.set_image_size((24, 24))
        self.ShutdownB.set_image_position((4, 2))
        self.ShutdownB.set_mouse_down(self.shutDownB_call)

        widgets_panel2 = [self.WinLable2, self.CommLabel, self.RobotText, self.CameraText, self.RobotConCHK, self.CameraConCHK, self.GripperText, self.GripperCHK_ON, self.GripperCHK_OFF, self.GripperText_ON,
                          self.GripperText_OFF, self.TeachModeText, self.TeachModeText_ON, self.TeachModeText_OFF, self.TeachModeCHK_ON, self.TeachModeCHK_OFF, self.VeloText, self.AccelText,self.JobCountText, self.ShutdownB,
                          self.PoseCountText, self.ModeStatusText, self.ModeStatusText_Auto, self.ModeStatusText_Manual, self.ModeStatusCHK_Auto, self.ModeStatusCHK_Manual, self.ModeStatusText_Manual] # self.Velo_Value, self.Accel_Value

        widgets2 = [self.panel2]
        widgets2 += widgets_panel2

        self.init_widgets2(context, widgets2)
        self.panel2.add_widgets(widgets_panel2)
        self.panel2.set_location(1200, 100)

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
            if self.RobotConCHK.is_checked == True:
                self.lMotions = []
                self.gMotions = []
                URxMoveToPoseOperator(0)
                URxMoveToPoseOperator(5)
                self.stateUrRun = False
                bl_Server.resetJobLists()

        self._run()
        #self._fk()
        # self.Change_VeloAccel(Large_List)
        # print(Large_List) # =========================================================> UR5와의 통신 변수

        if self.shutdown_call:
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

        for widget in self.widgets3: # =======================================================> widgets3 / sw
            rtn = widget.handle_event(event)
        
        if self.instance is not None:
           self.instance.set_event(event, context)
        
        if self.sensor_cam is not None and self.sensor_cam_mode:
            self.sensor_cam.processing()

        if "ROBOT" in connClinetList:
            self.RobotConCHK.is_checked = True
        else:
            self.RobotConCHK.is_checked = False
        if "XAVIER" in connClinetList:
            self.CameraConCHK.is_checked = True
        else:
            self.CameraConCHK.is_checked = False
            
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
        if self.modeAuto == True:
            self.modeManual = False
            if self.stateUrRun == False:
                if (bl_Server.checkXavierData()) == True:
                    bl_Server.autoMode()
                    self.TPoseLists = bl_Server.getTPoseLists()
                    if self.TPoseLists:
                        self.lMotions = []
                        self.gMotions = []
                        self.urMoveTimes = []
                        self.urMoveRadius = []
                        self.gMotions = bl_Server.getgMotions()
                        self.urMoveTimes = bl_Server.getUrMoveTimeLists()
                        self.urMoveRadius = bl_Server.getUrMoveRadiusLists()
                        #print(self.gMotions, self.urMoveTimes ,self.urMoveRadius)
                        poseCnt = len(self.TPoseLists)
                        for i in range(0, poseCnt, 1):
                            loc = self.TPoseLists[i].location
                            self.lMotions.append(loc)
                        if self._motion_timer == 0:
                            self._motion_timer = 10
                        self.stateUrRun = True
            self._urRun()
        if self.modeManual == True:
            self.modeAuto = False
            self._urRun()

    def _urRun(self):
        if self._motion_timer > 0:
            self._motion_timer -= 1

        leftCnt = len(self.lMotions)
        jobCount = bl_Server.checkJobLists()
        if (self.Language_FLAG == False):  # ========================================================> Kor_Between_Eng / sw
            self.PoseCountText.text = f'Pose Count: {leftCnt}' + f' t=[{self._motion_timer}]'
            self.JobCountText.text = f'Job Reserve Count  : {jobCount}'
        elif (self.Language_FLAG == True):
            self.PoseCountText.text = f'동작시간: {leftCnt}' + f' t=[{self._motion_timer}]'
            self.JobCountText.text = f'남은 작업수  : {jobCount}'
        if self.lMotions and self._motion_timer == 0:
            self.instance.setMover(self.lMotions.pop())
            if self.RobotConCHK.is_checked == True:
                bpy.context.view_layer.update()
                try:
                    cur_gmtion_ = self.gMotions.pop()
                    cur_urmovetime_ = self.urMoveTimes.pop()
                    cur_urmoveradius_ = self.urMoveRadius.pop()
                except Exception as e:
                    print(e)
                    cur_gmtion_ = 0
                URxMoveToPoseOperator(1, cur_urmovetime_, cur_urmoveradius_, cur_gmtion_)
            else:
                print("Check Robot conn")

            if len(self.lMotions) == 0 and len(self.gMotions) == 0 and self.RobotConCHK.is_checked == True:
                URxStateCheck(0)
                self.stateUrRun = False
                URxMoveToPoseOperator(5)
                URxMoveToPoseOperator(0)
                #if jobCount == 0:

            # print('run motion!')
            if leftCnt > 0:
                self._motion_timer = int(self._delay_time * self.SpeedUD.get_value())

    def _setFK(self,Base, Shoulder, Elbow, Wrist1, Wrist2, Wrist3):
        bpy.data.objects['Armature.001'].pose.bones['Base1'].rotation_euler.y = Base
        bpy.data.objects['Armature.001'].pose.bones['Shoulder1'].rotation_euler.y = Shoulder + 1.5708
        bpy.data.objects['Armature.001'].pose.bones['Elbow1'].rotation_euler.y = -Elbow
        bpy.data.objects['Armature.001'].pose.bones['Wrist1'].rotation_euler.y = Wrist1 + 1.5708
        bpy.data.objects['Armature.001'].pose.bones['Wrist2'].rotation_euler.y = Wrist2
        bpy.data.objects['Armature.001'].pose.bones['Wrist3'].rotation_euler.y = Wrist3

    def _fk(self):
        fk_ = bl_Server.getFK()
        if fk_:
            fk_pose_ = fk_.pop()
            self._setFK(fk_pose_[0],fk_pose_[1],fk_pose_[2],fk_pose_[3],fk_pose_[4],fk_pose_[5])

    def _initialize(self):
        print('init')
        instance = Maviz(
            item = Maviz.setup_item("item"),
            mover = Maviz.setup_ik_mover("Area", "ik_control")
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

    # 버튼 Func.........#.........#.........#.........#.........#.........#.........

    def CallAdminMenu(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(16)
        if (self.Admin_MENU_FLAG == False):
            self.Admin_MENU_FLAG = True
        elif (self.Admin_MENU_FLAG == True):
            self.Admin_MENU_FLAG = False
        print("Admin_MENU_FLAG : {}".format(self.Admin_MENU_FLAG))

    def moveHomeB_call(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(0)

    def motionRunB_call(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.lMotions = []
        self.gMotions = []
        self.TPoseLists = self.instance.getMavizTPoseLists()
        self.gMotions = self.instance.getMavizGMotions()

        if len(self.TPoseLists) == 0:
            self.TPoseLists = bl_Server.getTPoseLists()
            self.gMotions = bl_Server.getgMotions()
            self.urMoveTimes = bl_Server.getUrMoveTimeLists()
            self.urMoveRadius = bl_Server.getUrMoveRadiusLists()

        poseCnt = len(self.TPoseLists)
        for i in range(0,poseCnt,1):
            loc = self.TPoseLists[i].location
            #print("debug : ",loc)
            self.lMotions.append(loc)
            #print(f'acrion pos{i}', ' ', loc)
        self._motion_timer = 10
        #print('motion append ', len(self.lMotions), ' timer = ', self._motion_timer)

    def emcStop_call(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(2)

    def addPoseSetB_call(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(3)

    def addPoseB_call(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(4)

    def motionDelB_call(self, widget):
        print("Button '{0}' is pressed".format(widget.text))        
        URxMoveToPoseOperator(5)
        self.instance.MavizdelPoseToBl()
        self.instance.delSaveMavizTPoseLists()

    def shutDownB_call(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(6)
        self.shutdown_call = True

    def setTeachModeB_call(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.TeachMode_ON_func()
        URxMoveToPoseOperator(7)

    def setOffTeachModeB_call(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.TeachMode_OFF_func()
        URxMoveToPoseOperator(8)

    def addCurrUrJointAngle(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        Temp_TimeRadius_Box = []
        Temp_TimeRadius_Box.append(urMoveTime)
        Temp_TimeRadius_Box.append(urMoveRadius)
        URxMoveToPoseOperator(9, Temp_TimeRadius_Box)

    def saveCurrUrJointAngle(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(10)

    def loadUrPoseLists(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        try:
            bpy.ops.object.search_enum_operator('INVOKE_DEFAULT') # =============================================================> bl_ui_Search / sw
        except Exception as e:
            print(e)

    def saveTPoseLists(self,widget): # ================================================================================> saveTPoseLists 원본
        print("Button '{0}' is pressed".format(widget.text))
        bl_Server.delPoseToBl() # ==============================================> save시 모션 삭제
        saveData_ = self.instance.getSaveMavizTPoseLists()
        timelists_ = self.instance.getUrMoveTimeLists()
        radiuslists_ = self.instance.getUrMoveRadiusLists()

        for time in enumerate(timelists_):
            saveData_[time[0]].append(time[1])

        for radius in enumerate(radiuslists_):
            if radius[0] == 0 or radius[0] == (len(saveData_) - 1):
                saveData_[radius[0]].append(int(0))
            else:
                saveData_[radius[0]].append(radius[1])

        for gMotion in range(0,len(saveData_),1):
            if gMotion == 0 or gMotion == (len(saveData_) - 1):
                saveData_[gMotion].append(int(0))
            else:
                saveData_[gMotion].append(int(1))

        URxMoveToPoseOperator(12, saveData_)

    def setVeloAccel(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (self.Language_FLAG == False): # ========================================================> Kor_Between_Eng / sw
            self.VeloText.text = f'Velo   :  {urVelo}'
            self.AccelText.text = f'Accel  :  {urAccel}'
        elif (self.Language_FLAG == True):
            self.VeloText.text = f'속도   :  {urVelo}'
            self.AccelText.text = f'가속도  :  {urAccel}'
        URxMoveToPoseOperator(13,urAccel,urVelo)

    def Change_VeloAccel(self, List): # =============> UR5의 실시간 정보로 velo, accel값 수정
        if (self.Language_FLAG == False): # ========================================================> Kor_Between_Eng / sw
            self.VeloText.text = f'Velo   :  {List[0][0]}'
            self.AccelText.text = f'Accel  :  {List[1][1]}'
        elif (self.Language_FLAG == True):
            self.VeloText.text = f'속도   :  {List[0][0]}'
            self.AccelText.text = f'가속도  :  {List[1][1]}'

    def gripperOn(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.Gripper_ON_func()
        URxMoveToPoseOperator(14)

    def gripperOff(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.Gripper_OFF_func()
        URxMoveToPoseOperator(15)

    # 버튼 Func END.........#.........#.........#.........#.........#.........#.........

    # 체크박스 .........#.........#.........#.........#.........#.........#.........

    def Gripper_ON_func(self):
        if self.GripperCHK_ON.is_checked == False:
            self.GripperCHK_ON.is_checked = True
            self.GripperCHK_OFF.is_checked = False

    def Gripper_OFF_func(self):
        if self.GripperCHK_OFF.is_checked == False:
            self.GripperCHK_ON.is_checked = False
            self.GripperCHK_OFF.is_checked = True

    def TeachMode_ON_func(self):
        if self.TeachModeCHK_ON.is_checked == False:
            self.TeachModeCHK_ON.is_checked = True
            self.TeachModeCHK_OFF.is_checked = False

    def TeachMode_OFF_func(self):
        if self.TeachModeCHK_OFF.is_checked == False:
            self.TeachModeCHK_ON.is_checked = False
            self.TeachModeCHK_OFF.is_checked = True

    def mode_select_1(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_1.is_checked == False:
            self.chb_select_1.is_checked = True
            self.chb_select_2.is_checked = False
            self.chb_select_3.is_checked = False
            print("send_1")
            # self.ser.run_CMD('h',0)#self.ser.run_CMD('p',1)

    def mode_select_2(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_2.is_checked == False:
            self.chb_select_1.is_checked = False
            self.chb_select_2.is_checked = True
            self.chb_select_3.is_checked = False
            print("send_2")
            # self.ser.run_CMD('h',2)#self.ser.run_CMD('p',2)

    def mode_select_3(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_3.is_checked == False:
            self.chb_select_1.is_checked = False
            self.chb_select_2.is_checked = False
            self.chb_select_3.is_checked = True
            print("send_3")
            # self.ser.run_CMD('h',1)#self.ser.run_CMD('p',3)

    # 체크박스 END.........#.........#.........#.........#.........#.........#.........

    # 모드변경 .........#.........#.........#.........#.........#.........#.........
    def modeChangeManu(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.modeManual = True
        self.modeAuto = False
        self.ModeStatusCHK_Auto.is_checked = False
        self.ModeStatusCHK_Manual.is_checked = True
        bl_Server.controlModeChange(False)

    def modeChangeAuto(self,widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.modeManual = False
        self.modeAuto = True
        self.ModeStatusCHK_Auto.is_checked = True
        self.ModeStatusCHK_Manual.is_checked = False
        bl_Server.controlModeChange(True)

    def Kor_to_Eng(self, widget):
        self.instance.Start_maviz_thread() # =============================================================> 수정 / sw
        print("Button '{0}' is pressed".format(widget.text))
        self.Language_FLAG = False # ==================================================> Language_FLAG 추가 / sw
        self.Switch_Kor.text = "Kor"
        self.Switch_Eng.text = "Eng"
        self.Auto_Button.text = "Auto"
        self.Manual_Button.text = "Manual"
        self.SpeedText.text = "Take Time"
        self.MotionRunA.text = "Run"
        self.RobotHomePA.text = "Home Position"
        self.Motionremv.text = "Motion Delete"
        self.Gripper_ON.text = "Gripper On"
        self.Gripper_OFF.text = "Gripper Off"
        self.Teach_ModeA.text = "Teach On"
        self.Off_Teach_ModeA.text = "Teach Off"
        self.VeloText_Left_Panel.text = "Velo"
        self.AccelText_Left_Panel.text = "Accel"
        self.Set_Ur_Velo_AccelA.text = "Set UR Speed"
        self.chb_select_1.text = "MIN"
        self.chb_select_2.text = "MID"
        self.chb_select_3.text = "MAX"
        self.PoseDelA.text = "Del"
        self.PoseSaveA.text = "Save"
        self.PoseLoadA.text = "Load"
        self.label_ProgramNum.text = "Program :"
        self.AdminMenu.text = "Admin"
        self.setBoardResetBT.text = "STOP"
        self.WinLable2.text = "Information"
        self.CommLabel.text = "Communication "
        self.RobotText.text = "Robot"
        self.CameraText.text = "Camera"
        self.GripperText.text = "Gripper"
        self.TeachModeText.text = "Teach Mode"
        self.ModeStatusText.text = "Mode Status"
        self.ModeStatusText_Auto.text = "Auto"
        self.ModeStatusText_Manual.text = "Manual"
        self.VeloText.text = "Velo   :  0"
        self.AccelText.text = "Accel  :  0"
        self.PoseCountText.text = f'Pose Count: 0 t=[0]'
        self.JobCountText.text = "Job Reserve Count  : 0"
        self.ShutdownB.text = "PROGRAM SHUTDOWN"
        self.ShutdownB.text_size = 22

    def Eng_to_Kor(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.Language_FLAG = True # ==================================================> Language_FLAG 추가 / sw
        self.Switch_Kor.text = "한"
        self.Switch_Eng.text = "영"
        self.Auto_Button.text = "자동"
        self.Manual_Button.text = "수동"
        self.SpeedText.text = " 경과시간"
        self.MotionRunA.text = "실행"
        self.RobotHomePA.text = "원위치"
        self.Motionremv.text = "지정동작 삭제"
        self.Gripper_ON.text = "노즐온"
        self.Gripper_OFF.text = "노즐오프"
        self.Teach_ModeA.text = "티칭모드온"
        self.Off_Teach_ModeA.text = "티칭모드오프"
        self.VeloText_Left_Panel.text = "속도"
        self.AccelText_Left_Panel.text = "가속도"
        self.Set_Ur_Velo_AccelA.text = "로봇속도 설정"
        self.chb_select_1.text = "최소"
        self.chb_select_2.text = "중간"
        self.chb_select_3.text = "최대"
        self.PoseDelA.text = "삭제"
        self.PoseSaveA.text = "저장"
        self.PoseLoadA.text = "열기"
        self.label_ProgramNum.text = "프로그램 :"
        self.AdminMenu.text = "관리자"
        self.setBoardResetBT.text = "비상정지"
        self.WinLable2.text = "상태창"
        self.CommLabel.text = "통신상태 "
        self.RobotText.text = " 로봇"
        self.CameraText.text = " 카메라"
        self.GripperText.text = "분사상태"
        self.TeachModeText.text = "학습모드"
        self.ModeStatusText.text = "모드상태"
        self.ModeStatusText_Auto.text = "자동"
        self.ModeStatusText_Manual.text = "   수동"
        self.VeloText.text = "속도   :  0"
        self.AccelText.text = "가속도  :  0"
        self.PoseCountText.text = f'경과시간: 0 t=[0]'
        self.JobCountText.text = "남은 작업량  : 0"
        self.ShutdownB.text = "프로그램 종료"
        self.ShutdownB.text_size = 28
        print(self.CameraText.text)
        print(self.GripperText.text)
        print(self.TeachModeText.text)
    # 모드변경 END .........#.........#.........#.........#.........#.........#.........

    # Up&Down 값 변경 .........#.........#.........#.........#.........#.........#.........
    def on_program_up_down_value_change(self,up_down, value):
        global pListCount
        pListCount = value
        bl_Server.autoModeChangeLoadTPoseLists(value)

    def on_ur_velo_up_down_value_change(self,up_down, value):
        global urVelo
        urVelo = value
        print(urVelo)

    def on_ur_accel_up_down_value_change(self,up_down, value):
        global urAccel
        urAccel = value
        print(urAccel)

    # def on_ur_move_time_up_down_value_change(self,up_down, value):
    #     global urMoveTime
    #     urMoveTime = value
    #     self.instance.urMoveTime = value
    #     print(urMoveTime)
    #
    # def on_ur_move_radius_up_down_value_change(self,up_down, value):
    #     global urMoveRadius
    #     urMoveRadius = value
    #     self.instance.urMoveRadius = value / 100
    #     print(urMoveRadius)

    def Time_Sliding_value_Change(self, Slider, value): # =======================================> Slider / sw
        global urMoveTime
        urMoveTime = value
        self.instance.urMoveTime = value / 100
        print(urMoveTime)

    def Radius_Sliding_value_Change(self, Slider, value): # =======================================> Slider / sw
        global urMoveRadius
        urMoveRadius = value
        self.instance.urMoveRadius = value / 100
        print(urMoveRadius)

    def on_chb_visibility_state_change(self, checkbox, state):
        active_obj = bpy.context.view_layer.objects.active
        if active_obj is not None:
            active_obj.hide_viewport = not state
    # Up&Down 값 변경 END .........#.........#.........#.........#.........#.........#.........

    # .미사용..#.........#.........#.........#.........#.........#.........
    '''
    
    def poseRunB_call(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        #URxMoveToPoseOperator(1)
        
    def setPoseState(self, state):
        print("state '{0}' is pressed".format(state))
        # bpy.data.objects['IK Target'].location = lMotions[state]
        # bpy.data.objects['IK Target'].rotation_euler = rMotions[state]
        
    def poseSetB_call(self, widget):
        self.instance.testButton
        if self.robot_tcp_mode:
            self.robot_tcp_mode = False
            self.label.text = "Robot:: click T"
            self.label.draw()
            print(self.label.text)
        else:
            #self.robot_tcp_mode = True
            self.label.text = "Robot F"
            self.label.draw()
            print(self.label.text)
            
    def bm_path_call(self, widget):
        self.MavizTPoseLists = []
        self.MavizTPoseLists = self.instance.getMavizTPoseLists()
        print("TPoseLists : ",self.MavizTPoseLists)
        print("Button '{0}' is pressed".format(widget.text))
        # 포인트 리스트
        pointList = []
        poseCnt = len(self.MavizTPoseLists)
        print("poseCnt",poseCnt)

        for i in range(poseCnt):
            loc = self.MavizTPoseLists[i].location
            print(f'pos{i}', ' ', loc)
            pointList.append(loc)
        print("debug3")
        curve_motion_line = curve_from_points('cur_motion_path', pointList)
        scn = bpy.context.scene
        scn.collection.objects.link(curve_motion_line)
        curve_motion_line.select_set(True)
        print('-bm_path_call-------end-------------------')

    def stopMotionc_call(self,widget):
        print("Button '{0}' is pressed".format(widget.text))

    def setPoseBT_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.label_poseList.text = "Pose Count [ '{0}']".format(mListCount)

    def setGripStop_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        # self.ser.run_CMD('g',1)#self.ser.run_CMD('e')

    def setSensor_press(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self._realsenseInit()

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
    '''
    # .미사용 END..#.........#.........#.........#.........#.........#.........



##################################################
def cleanup_and_quit():
    unregister()
    bpy.ops.wm.quit_blender()


def register():
    bpy.utils.register_class(MavizHandler)
    bpy.utils.register_class(SearchEnumOperator) # =========================================================> bl_ui_Search / sw
    bpy.utils.register_class(DialogOperator) # =============================================================> bl_ui_Save / sw


def unregister():
    bpy.utils.unregister_class(MavizHandler)
    bpy.utils.unregister_class(SearchEnumOperator) # =========================================================> bl_ui_Search / sw
    bpy.utils.unregister_class(DialogOperator) # =============================================================> bl_ui_Save / sw


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