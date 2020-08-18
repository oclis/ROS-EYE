import bpy

from bl_ui_label import *
from bl_ui_button import *
from bl_ui_checkbox import *
from bl_ui_slider import *
from bl_ui_up_down import *
from bl_ui_drag_panel import *
from bl_ui_draw_pose import Bl_Ui_Draw_Pose_Operator

from bl_op_data import Bl_Op_Data as bod
from bl_op_server import URxMoveToPoseOperator
from bl_op_flag import Bl_Op_Flag as bof


class Bl_Ui_Draw_Panel_Menu():
    def draw_Menu_Left(self):
        # left panel
        self.WinLable = BL_UI_Label(10, 10, 200, 25)
        self.WinLable.text = "MAVIZ | UR5 "
        self.WinLable.text_size = 24
<<<<<<< HEAD
        self.WinLable.text_color = (210/255, 73/255, 153/255, 1.0)

        self.MotionRunA = BL_UI_Button(160, 60, 140, 85)
        self.MotionRunA.bg_color = (15/225, 76/225, 129/225, 0.8)
=======
        self.WinLable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.MotionRunA = BL_UI_Button(160, 60, 140, 85)
        self.MotionRunA.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.MotionRunA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.MotionRunA.text = "Run"
        self.MotionRunA.text_size = 32
        # self.MotionRunB.set_image("//img/gray_r.png")
        self.MotionRunA.set_image_size((24, 24))
        self.MotionRunA.set_image_position((4, 2))
        self.MotionRunA.set_mouse_down(self.bcall_Run_Motion)

        self.SpeedText = BL_UI_Label(25, 65, 150, 15)
        self.SpeedText.text = "Take Time :"
        self.SpeedText.text_size = 13

        self.SpeedUD = BL_UI_Up_Down(100, 65)
<<<<<<< HEAD
        self.SpeedUD.color = (210/255, 73/255, 153/255, 1.0)
=======
        self.SpeedUD.color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.SpeedUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.SpeedUD.min = 1.0
        self.SpeedUD.max = 10.0
        self.SpeedUD.decimals = 0
        self.SpeedUD.set_value(0)
        self.SpeedUD.set_value(bod.data_Ui_Job_Time)
        self.SpeedUD.set_value_change(self.up_Down_On_Ur_Job_Time_Up_Down_Value_Change)

        self.label_urMoveTimeNum = BL_UI_Label(25, 95, 40, 15)
        self.label_urMoveTimeNum.text = "Time :"
        self.label_urMoveTimeNum.text_size = 16

        self.urMoveTimeUD = BL_UI_Up_Down(100, 95)
<<<<<<< HEAD
        self.urMoveTimeUD.color = (210/255, 73/255, 153/255, 1.0)
=======
        self.urMoveTimeUD.color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.urMoveTimeUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.urMoveTimeUD.min = 0.0
        self.urMoveTimeUD.max = 10.0
        self.urMoveTimeUD.decimals = 0
        self.urMoveTimeUD.set_value(0)  #
        self.urMoveTimeUD.set_value(bod.data_Ui_Ur_Time)
        self.urMoveTimeUD.set_value_change(self.up_Down_On_Ur_Move_Time_Up_Down_Value_Change)

        self.label_ur_Move_RadiusNum = BL_UI_Label(25, 125, 40, 15)
        self.label_ur_Move_RadiusNum.text = "Radius :"
        self.label_ur_Move_RadiusNum.text_size = 16

        self.ur_Move_RadiusUD = BL_UI_Up_Down(100, 125)
<<<<<<< HEAD
        self.ur_Move_RadiusUD.color = (210/255, 73/255, 153/255, 1.0)
=======
        self.ur_Move_RadiusUD.color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.ur_Move_RadiusUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.ur_Move_RadiusUD.min = 0.0
        self.ur_Move_RadiusUD.max = 10.0
        self.ur_Move_RadiusUD.decimals = 0
        self.ur_Move_RadiusUD.set_value(0)
        self.ur_Move_RadiusUD.set_value_change(self.up_Down_On_Ur_Move_Radius_Up_Down_Value_Change)

        self.VeloText_Left_Panel = BL_UI_Label(25, 160, 40, 15)
<<<<<<< HEAD
        self.VeloText_Left_Panel.color = (210/255, 73/255, 153/255, 1.0)
        self.VeloText_Left_Panel.text = "Velo :"
        self.VeloText_Left_Panel.text_size = 16
        self.veloUD = BL_UI_Up_Down(100, 160)
        self.veloUD.color = (210/255, 73/255, 153/255, 1.0)
=======
        self.VeloText_Left_Panel.color = (0.2, 0.8, 0.8, 0.8)
        self.VeloText_Left_Panel.text = "Velo :"
        self.VeloText_Left_Panel.text_size = 16
        self.veloUD = BL_UI_Up_Down(100, 160)
        self.veloUD.color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.veloUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.veloUD.min = 1.0
        self.veloUD.max = 10.0
        self.veloUD.decimals = 0
        self.veloUD.set_value(1)
        self.veloUD.set_value_change(self.up_Down_On_Ur_Velo_Up_Down_Value_Change)

        self.AccelText_Left_Panel = BL_UI_Label(25, 190, 40, 15)
<<<<<<< HEAD
        self.AccelText_Left_Panel.color = (210/255, 73/255, 153/255, 1.0)
=======
        self.AccelText_Left_Panel.color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.AccelText_Left_Panel.text = "Accel :"
        self.AccelText_Left_Panel.text_size = 16

        self.accelUD = BL_UI_Up_Down(100, 190)
<<<<<<< HEAD
        self.accelUD.color = (210/255, 73/255, 153/255, 1.0)
=======
        self.accelUD.color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.accelUD.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.accelUD.min = 1.0
        self.accelUD.max = 10.0
        self.accelUD.decimals = 0
        self.accelUD.set_value(bod.data_Ui_Ur_Velo)
        self.accelUD.set_value_change(self.up_Down_On_Ur_Accel_Up_Down_Value_Change)

        self.Set_Ur_Velo_AccelA = BL_UI_Button(160, 160, 140, 50)
<<<<<<< HEAD
        self.Set_Ur_Velo_AccelA.bg_color = (15/225, 76/225, 129/225, 0.8)
=======
        self.Set_Ur_Velo_AccelA.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.Set_Ur_Velo_AccelA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Set_Ur_Velo_AccelA.text = "Set UR Speed"
        self.Set_Ur_Velo_AccelA.set_image_size((24, 24))
        self.Set_Ur_Velo_AccelA.set_image_position((4, 2))
        self.Set_Ur_Velo_AccelA.set_mouse_down(self.bcall_Set_Velo_Accel)

        self.Motionremv = BL_UI_Button(20, 280, 135, 70)
<<<<<<< HEAD
        self.Motionremv.bg_color = (15/225, 76/225, 129/225, 0.8)
=======
        self.Motionremv.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.Motionremv.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Motionremv.text = "Motion Delete"
        # self.Motionremv.set_image("//img/gray_play.png")
        self.Motionremv.set_image_size((24, 24))
        self.Motionremv.set_image_position((4, 2))
        self.Motionremv.set_mouse_down(self.bcall_Draw_Del_Pose)

        self.RobotHomePA = BL_UI_Button(20, 220, 280, 50)
<<<<<<< HEAD
        self.RobotHomePA.bg_color = (15/225, 76/225, 129/225, 0.8)
=======
        self.RobotHomePA.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.RobotHomePA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.RobotHomePA.text = "Home Position"
        # self.RobotHomePA.set_image("//img/gray_play.png")
        self.RobotHomePA.set_image_size((24, 24))
        self.RobotHomePA.set_image_position((4, 2))
        self.RobotHomePA.set_mouse_down(self.bcalll_Return_To_Home)

        self.PoseSaveA = BL_UI_Button(165, 280, 135, 30)
<<<<<<< HEAD
        self.PoseSaveA.bg_color = (15/225, 76/225, 129/225, 0.8)
=======
        self.PoseSaveA.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.PoseSaveA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.PoseSaveA.text = "Save"
        self.PoseSaveA.set_image_size((24, 24))
        self.PoseSaveA.set_image_position((4, 2))
        self.PoseSaveA.set_mouse_down(self.bcall_Save_Pose_Lists)

        self.PoseLoadA = BL_UI_Button(165, 320, 135, 30)
<<<<<<< HEAD
        self.PoseLoadA.bg_color = (15/225, 76/225, 129/225, 0.8)
=======
        self.PoseLoadA.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.PoseLoadA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.PoseLoadA.text = "Load"
        self.PoseLoadA.set_image_size((24, 24))
        self.PoseLoadA.set_image_position((4, 2))
        self.PoseLoadA.set_mouse_down(self.bcall_Load_Ur_Pose_Lists)

        # grip-massage MIN
        self.chb_select_1 = BL_UI_Checkbox(20, 360, 100, 15)
        self.chb_select_1.text = "MIN"  # "Stop"
        self.chb_select_1.text_size = 14
        self.chb_select_1.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_1.is_checked = True
        self.chb_select_1.set_mode(1)
        self.chb_select_1.set_mouse_down(self.checkbox_Mode_Select_1)
        # grip-massage MID
        self.chb_select_2 = BL_UI_Checkbox(130, 360, 100, 15)
        self.chb_select_2.text = "MID"  # "Up"
        self.chb_select_2.text_size = 14
        self.chb_select_2.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_2.is_checked = False
        self.chb_select_2.set_mode(2)
        self.chb_select_2.set_mouse_down(self.checkbox_Mode_Select_2)
        # grip-massage MAX
        self.chb_select_3 = BL_UI_Checkbox(240, 360, 100, 15)
        self.chb_select_3.text = "MAX"  # "Down"
        self.chb_select_3.text_size = 14
        self.chb_select_3.text_color = (0.2, 0.9, 0.9, 1.0)
        self.chb_select_3.is_checked = False
        self.chb_select_3.set_mode(3)
        self.chb_select_3.set_mouse_down(self.checkbox_Mode_Select_3)

        self.setBoardResetBT = BL_UI_Button(20, 700, 280, 80)
<<<<<<< HEAD
        self.setBoardResetBT.bg_color = (210/255, 73/255, 153/255, 1.0)
=======
        self.setBoardResetBT.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.setBoardResetBT.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.setBoardResetBT.text = "STOP"
        self.setBoardResetBT.text_color = (1.0, 1.0, 1.0, 1.0)
        self.setBoardResetBT.text_size = 36
        # self.setBoardResetBT.set_image("//img/rotate.png")
        self.setBoardResetBT.set_image_size((24, 24))
        self.setBoardResetBT.set_image_position((4, 2))
        self.setBoardResetBT.set_mouse_down(self.bcall_Stop_Emergency)

        widgets_panel = [self.MotionRunA, self.WinLable, self.RobotHomePA, self.Motionremv, self.VeloText_Left_Panel,
                         self.AccelText_Left_Panel, self.veloUD, self.accelUD, self.Set_Ur_Velo_AccelA,
                         self.chb_select_1, self.chb_select_2, self.chb_select_3, self.urMoveTimeUD,
                         self.label_urMoveTimeNum, self.ur_Move_RadiusUD, self.label_ur_Move_RadiusNum,
                         self.PoseSaveA, self.PoseLoadA, self.setBoardResetBT, self.SpeedText, self.SpeedUD]


        return widgets_panel

    def draw_Menu_Right(self):
        # righit 두번째 패널

        self.WinLable2 = BL_UI_Label(10, 10, 200, 25)
        self.WinLable2.text = "Information"
        self.WinLable2.text_size = 26
<<<<<<< HEAD
        self.WinLable2.text_color = (210/255, 73/255, 153/255, 1.0)
=======
        self.WinLable2.text_color = (0.6, 0.9, 0.3, 1.0)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10

        self.CommLabel = BL_UI_Label(25, 50, 200, 25)
        self.CommLabel.text_color = (1.0, 1.0, 1.0, 1.0)
        self.CommLabel.text = "Communication "
        self.CommLabel.text_size = 20

        self.RobotText = BL_UI_Label(25, 90, 200, 25)
        self.RobotText.text = "Robot"
        self.RobotText.text_size = 20
<<<<<<< HEAD
        self.RobotText.text_color = (210/255, 73/255, 153/255, 1.0)
=======
        self.RobotText.text_color = (0.6, 0.9, 0.3, 1.0)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10

        self.RobotConCHK = BL_UI_Checkbox(45, 130, 100, 15)
        self.RobotConCHK.text = ""
        self.RobotConCHK.text_size = 14
        self.RobotConCHK.text_color = (0.2, 0.9, 0.9, 1.0)
        self.RobotConCHK.is_checked = False

        self.ShutdownB = BL_UI_Button(20, 510, 280, 60)
<<<<<<< HEAD
        self.ShutdownB.bg_color = (210/255, 73/255, 153/255, 1.0)
=======
        self.ShutdownB.bg_color = (0.2, 0.8, 0.8, 0.8)
>>>>>>> ee090615a7868204ded86f191c45f90186b1bc10
        self.ShutdownB.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.ShutdownB.text = "PROGRAM SHUTDOWN"
        self.ShutdownB.text_size = 22
        # self.ShutdownB.set_image("//img/rotate.png")
        self.ShutdownB.set_image_size((24, 24))
        self.ShutdownB.set_image_position((4, 2))
        self.ShutdownB.set_mouse_down(self.bcall_Shut_Down)

        widgets_panel2 = [self.WinLable2, self.CommLabel, self.RobotText, self.RobotConCHK, self.ShutdownB]

        return widgets_panel2

    # Function
    def bcalll_Return_To_Home(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(0)

    def bcall_Run_Motion(self, widget):
        try:
            print("Button '{0}' is pressed".format(widget.text))
            bod.data_Generate_Job()
        except Exception as message:
            print("bcall_run_Motion error : ", message)

    def bcall_Stop_Emergency(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(2)

    def bcall_Draw_Del_Pose(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        Bl_Ui_Draw_Pose_Operator(0)

    def bcall_Shut_Down(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        URxMoveToPoseOperator(6)
        bof.FLAG_OP_SHUTDOWN = True

    def bcall_Load_Ur_Pose_Lists(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        try:
            bof.FLAG_IK_MOVE_DRAG = False
            bpy.ops.object.load_enum_operator('INVOKE_DEFAULT')
        except Exception as e:
            print(e)

    def bcall_Save_Pose_Lists(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        try:
            bof.FLAG_IK_MOVE_DRAG = False
            bod.data_Set_Save_To_Mem()
            Bl_Ui_Draw_Pose_Operator(0)
            bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
        except Exception as e:
            print(e)

    def bcall_Set_Velo_Accel(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        velo = bod.data_Get_Ui_Ur_Velo()
        accel = bod.data_Get_Ui_Ur_Accel()
        URxMoveToPoseOperator(13, velo, accel)

    def checkbox_Mode_Select_1(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_1.is_checked == False:
            self.chb_select_1.is_checked = True
            self.chb_select_2.is_checked = False
            self.chb_select_3.is_checked = False
            print("send_1")
            # self.ser.run_CMD('h',0)#self.ser.run_CMD('p',1)

    def checkbox_Mode_Select_2(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_2.is_checked == False:
            self.chb_select_1.is_checked = False
            self.chb_select_2.is_checked = True
            self.chb_select_3.is_checked = False
            print("send_2")
            # self.ser.run_CMD('h',2)#self.ser.run_CMD('p',2)

    def checkbox_Mode_Select_3(self, checkbox, __mode):
        print(__mode)
        if self.chb_select_3.is_checked == False:
            self.chb_select_1.is_checked = False
            self.chb_select_2.is_checked = False
            self.chb_select_3.is_checked = True
            print("send_3")
            # self.ser.run_CMD('h',1)#self.ser.run_CMD('p',3)

    def up_Down_On_Ur_Velo_Up_Down_Value_Change(self, up_down, value): # up_Down_On_Ur_Accel_Up_Down_Value_Change
        bod.data_Set_Ui_Ur_Velo(value)
        print("up_Down__On_Ur_Velo_Up_Down_Value_Change : ",bod.data_Get_Ui_Ur_Velo())

    def up_Down_On_Ur_Accel_Up_Down_Value_Change(self, up_down, value): # on_ur_accel_up_down_value_change
        bod.data_Set_Ui_Ur_Accel(value)
        print("up_Down__On_Ur_Accel_Up_Down_Value_Change",bod.data_Get_Ui_Ur_Accel())

    def up_Down_On_Ur_Job_Time_Up_Down_Value_Change(self, up_down, value):
        bod.data_Set_Ui_Job_Time(value)
        print("up_Down__On_Ur_Job_Time_Up_Down_Value_Change : ",bod.data_Get_Ui_Job_Time())

    def up_Down_On_Ur_Move_Time_Up_Down_Value_Change(self, up_down, value):
        bod.data_Set_Ui_Ur_Time(value)
        print("up_Down__On_Ur_Move_Time_Up_Down_Value_Change : ",bod.data_Get_Ui_Ur_Time())

    def up_Down_On_Ur_Move_Radius_Up_Down_Value_Change(self, up_down, value):
        bod.data_Set_Ui_Ur_Radius(value / 100)
        print("up_Down__On_Ur_Move_Radius_Up_Down_Value_Change : ", bod.data_Get_Ui_Ur_Radius())

    def on_chb_visibility_state_change(self, checkbox, state):
        active_obj = bpy.context.view_layer.objects.active
        if active_obj is not None:
            active_obj.hide_viewport = not state