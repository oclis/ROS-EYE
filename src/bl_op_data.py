import os
import bpy
import math
import queue
import datetime

from bl_def_robot import *
from bl_def_task import *
from multipledispatch import dispatch

class Bl_Op_Data():
    robot1 = Bl_Def_Robot()

    data_Generate_Job_Count = 1
    data_Reserve_Job_Queue = queue.Queue()

    data_Draw_Ur_Pose_List = []
    data_Draw_Ur_Time_List = []
    data_Draw_Ur_Radius_List = []
    data_Draw_Ur_Gripper_Motion_List = []

    data_Ui_Job_Time = 0
    data_Ui_Ur_Time = 0
    data_Ui_Ur_Radius = 0
    data_Ui_Ur_Velo = 0
    data_Ui_Ur_Accel = 0

    data_Curr_Ur_Angle = []

    data_Save_Ur_Pose_List = []
    data_Load_Ur_Pose_List = []

    data_Save_To_File_List = []
    data_Tcp_Clinet_List = {}

    good_Word = ['삶이 있는 한 희망은 있다', '산다는것 그것은 치열한 전투이다.', '만족은 결과가 아니라 과정에서 온다.',
         '부드러운 자 만이 언제나 진실로 강하다.', 'The journey is the reward.', 'Live simply that others may simply live.'
         , 'Hate the sin, love the sinner. ', 'Peace is the path.']







    def data_Generate_Job():
        print("debug : data_Generate_Job 1")
        try:
            generate_Job_ = Bl_Def_Task()
            generate_Job_.job_Number = ("job_Num:{}".format(Bl_Op_Data.data_Generate_Job_Count))
            generate_Job_.job_Pose_List = Bl_Op_Data.data_Get_Draw_Ur_Pose_List()
            generate_Job_.job_Move_Times = Bl_Op_Data.data_Get_Draw_Ur_Time_List()
            generate_Job_.job_Move_Radius = Bl_Op_Data.data_Get_Draw_Ur_Radius_List()
            generate_Job_.job_Gripper_Motions = Bl_Op_Data.data_Get_Draw_Ur_Gripper_Motion_List()
            Bl_Op_Data.robot1.robot_Job.put(generate_Job_)
            Bl_Op_Data.data_Generate_Job_Count += 1
        except Exception as e:
            print("data_Generate_Job error : ",e)

    def data_Distribute_Job():
        tmp = Bl_Op_Data.data_Reserve_Job_Queue.get()
        Bl_Op_Data.robot1.robot_Job.put(tmp)
        Bl_Op_Data.robot1.robot_Job_Add_Time = datetime.datetime.now()
        #print(Bl_Op_Data.robot1.robot_Job.qsize())
        print("Bl_Op_Data.robot1.robot_Job_Add_Time",Bl_Op_Data.robot1.robot_Job_Add_Time)

    def data_Get_File_List():
        DataPath = os.path.abspath('./Data')
        files = os.listdir(DataPath)
        filenum = len(files)
        if filenum < 1:
            print("There is no Coordinate in File")
        else:
            bl_Load_Standard_parameter = []
            for i in range(0, filenum):
                Call_files = open("{}/{}".format(DataPath, files[i]), 'rt')
                val1 = "{}".format(files[i])
                val2 = "{}".format(files[i])
                val3 = " "
                bl_Search_module_pack = (val1, val2, val3)
                bl_Load_Standard_parameter.append(bl_Search_module_pack)
            Call_files.close()
            return bl_Load_Standard_parameter

    # - POSE DATA -
    #Pose Save
    def data_Set_Save_Curr_Ur_Pose(cur_loc, cur_rot):
        Bl_Op_Data.data_Save_Ur_Pose_List.append([cur_loc.x, cur_loc.y, cur_loc.z, cur_rot.x, cur_rot.y, cur_rot.z])

    def data_Get_Save_Curr_Ur_Pose():
        Save_Ur_Pose_Return = Bl_Op_Data.data_Save_Ur_Pose_List
        Bl_Op_Data.data_Save_Ur_Pose_List = []
        return Save_Ur_Pose_Return

    def data_Set_Save_To_Mem():
        save_Pose_Data = Bl_Op_Data.data_Get_Save_Curr_Ur_Pose()
        save_Time_Lists_ = Bl_Op_Data.data_Get_Draw_Ur_Time_List()
        save_Radius_Lists_ = Bl_Op_Data.data_Get_Draw_Ur_Radius_List()

        for time in enumerate(save_Time_Lists_):
            save_Pose_Data[time[0]].append(time[1])
        for radius in enumerate(save_Radius_Lists_):
            if radius[0] == 0 or radius[0] == (len(save_Pose_Data) - 1):
                save_Pose_Data[radius[0]].append(int(0))
            else:
                save_Pose_Data[radius[0]].append(radius[1])
        for save_Gripper_Motion in range(0, len(save_Pose_Data), 1):
            if save_Gripper_Motion == 0 or save_Gripper_Motion == (len(save_Pose_Data) - 1):
                save_Pose_Data[save_Gripper_Motion].append(int(0))
            else:
                save_Pose_Data[save_Gripper_Motion].append(int(1))

        Bl_Op_Data.data_Set_Save_To_File(save_Pose_Data)

    #Pose Save To File
    def data_Set_Save_To_File(datas):
        Bl_Op_Data.data_Save_To_File_List = datas

    def data_Get_Save_To_File():
        Save_To_File_List_Return = Bl_Op_Data.data_Save_To_File_List
        Bl_Op_Data.data_Save_To_File_List = []
        return Save_To_File_List_Return

    #DATA SPLIT
    def data_Split_Load_Ur_Pose(datas):
        load_Pose_List = []
        for data in datas:
            load_Loc        = (data[0], data[1], data[2])
            load_Rot        = (data[3], data[4], data[5])
            load_Time       = (data[6])
            load_Radius     = (data[7])
            load_Gripper    = (data[8])
            load_Pose_List.append([load_Loc, load_Rot, load_Time, load_Radius, load_Gripper])

        return load_Pose_List

    def data_Split_Local_Orientation(object):
        matrix_Channel_Child_Wrist1 = object.pose.bones['Wrist2'].matrix_channel
        matrix_Channel_Parent_Wrist2 = object.pose.bones['Wrist1'].matrix_channel
        matrix_Channel_Child_Wrist2 = object.pose.bones['Wrist3'].matrix_channel
        matrix_Channel_Parent_Wrist3 = object.pose.bones['Wrist2'].matrix_channel

        Base_ = object.pose.bones['Base'].matrix_channel.to_euler().z
        Shoulder_ = object.pose.bones['Shoulder'].matrix_channel.to_euler().y
        Elbow_ = object.pose.bones['Elbow'].matrix_channel.to_euler().y
        Wrist1_ = object.pose.bones['Wrist1'].matrix_channel.to_euler().y
        Wrist2 = -((matrix_Channel_Child_Wrist1.inverted() @ matrix_Channel_Parent_Wrist2).to_euler().z)
        Wrist3 = -((matrix_Channel_Child_Wrist2.inverted() @ matrix_Channel_Parent_Wrist3).to_euler().y)

        Base = Base_ - (math.pi / 2)
        Shoulder = Shoulder_ - (math.pi / 2)
        Elbow = Elbow_ - Shoulder_
        Wrist1 = (Wrist1_ - (math.pi / 2)) - Elbow_

        return (Base, Shoulder, Elbow, Wrist1, Wrist2, Wrist3)

    @dispatch(object)
    def data_Set_Pose(poseobj):
        time = Bl_Op_Data.data_Get_Ui_Ur_Time()
        radius = Bl_Op_Data.data_Get_Ui_Ur_Radius()
        Bl_Op_Data.data_Draw_Ur_Pose_List.append(poseobj)
        Bl_Op_Data.data_Draw_Ur_Time_List.append(time)
        Bl_Op_Data.data_Draw_Ur_Radius_List.append(radius)
        Bl_Op_Data.data_Print_Draw_List()

    @dispatch(object, int, int, int)
    def data_Set_Pose(poseobj, time, radius, gripper):
        Bl_Op_Data.data_Draw_Ur_Pose_List.append(poseobj)
        Bl_Op_Data.data_Draw_Ur_Time_List.append(time)
        Bl_Op_Data.data_Draw_Ur_Radius_List.append(radius)
        Bl_Op_Data.data_Draw_Ur_Gripper_Motion_List.append(gripper)
        Bl_Op_Data.data_Print_Draw_List()

    @dispatch(object, int, float, int)
    def data_Set_Pose(poseobj, time, radius, gripper):
        Bl_Op_Data.data_Draw_Ur_Pose_List.append(poseobj)
        Bl_Op_Data.data_Draw_Ur_Time_List.append(time)
        Bl_Op_Data.data_Draw_Ur_Radius_List.append(radius)
        Bl_Op_Data.data_Draw_Ur_Gripper_Motion_List.append(gripper)
        Bl_Op_Data.data_Print_Draw_List()

    def data_Reset_Pose():
        Bl_Op_Data.data_Draw_Ur_Pose_List = []
        Bl_Op_Data.data_Draw_Ur_Time_List = []
        Bl_Op_Data.data_Draw_Ur_Radius_List = []
        Bl_Op_Data.data_Draw_Ur_Gripper_Motion_List = []

    # - DRAW UR POSE DATA -
    def data_Get_Draw_Ur_Pose_List():
        Ur_Pose_List_Return = Bl_Op_Data.data_Draw_Ur_Pose_List
        Bl_Op_Data.data_Draw_Ur_Pose_List = []
        return Ur_Pose_List_Return

    def data_Get_Draw_Ur_Time_List():
        Ur_Time_List_Return = Bl_Op_Data.data_Draw_Ur_Time_List
        Bl_Op_Data.data_Draw_Ur_Time_List = []
        return Ur_Time_List_Return

    def data_Get_Draw_Ur_Radius_List():
        Ur_Radius_List_Return = Bl_Op_Data.data_Draw_Ur_Radius_List
        Bl_Op_Data.data_Draw_Ur_Radius_List = []
        return Ur_Radius_List_Return

    def data_Get_Draw_Ur_Gripper_Motion_List():
        Ur_Gripper_Motion_List_Return = Bl_Op_Data.data_Draw_Ur_Gripper_Motion_List
        Bl_Op_Data.data_Draw_Ur_Gripper_Motion_List = []
        return Ur_Gripper_Motion_List_Return

    # - UI DATA -
    #Velo
    def data_Set_Ui_Ur_Velo(value):
        Bl_Op_Data.data_Ui_Ur_Velo = value

    def data_Get_Ui_Ur_Velo():
        return Bl_Op_Data.data_Ui_Ur_Velo
    #Accel
    def data_Set_Ui_Ur_Accel(value):
        Bl_Op_Data.data_Ui_Ur_Accel = value

    def data_Get_Ui_Ur_Accel():
        return Bl_Op_Data.data_Ui_Ur_Accel

    #Job time
    def data_Set_Ui_Job_Time(value):
        Bl_Op_Data.data_Ui_Job_Time = value
        # print(Bl_Op_Data.data_Ui_Job_Time)

    def data_Get_Ui_Job_Time():
        # print(Bl_Op_Data.data_Ui_Job_Time)
        return Bl_Op_Data.data_Ui_Job_Time

    #Time
    def data_Set_Ui_Ur_Time(value):
        Bl_Op_Data.data_Ui_Ur_Time = value
        #print(Bl_Op_Data.data_Ui_Ur_Time)

    def data_Get_Ui_Ur_Time():
        #print(Bl_Op_Data.data_Ui_Ur_Time)
        return Bl_Op_Data.data_Ui_Ur_Time
    #Radius
    def data_Set_Ui_Ur_Radius(value):
        Bl_Op_Data.data_Ui_Ur_Radius = value
        #print(Bl_Op_Data.data_Ui_Ur_Radius)

    def data_Get_Ui_Ur_Radius():
        #print(Bl_Op_Data.data_Ui_Ur_Radius)
        return Bl_Op_Data.data_Ui_Ur_Radius

    # - CURR UR DATA -
    # Curr Ur Angle
    def data_Set_Curr_Ur_Angle(value):
        Bl_Op_Data.data_Curr_Ur_Angle = value
        #print(Bl_Op_Data.data_Curr_Ur_Angle)

    def data_Get_Curr_Ur_Angle():
        Curr_Ur_Angle_Return = Bl_Op_Data.data_Curr_Ur_Angle
        Bl_Op_Data.data_Curr_Ur_Angle = []
        return Curr_Ur_Angle_Return

    #DATA_PRINT
    def data_Print_Draw_List():
        print(Bl_Op_Data.data_Draw_Ur_Time_List)
        print(Bl_Op_Data.data_Draw_Ur_Pose_List)
        print(Bl_Op_Data.data_Draw_Ur_Radius_List)
        print(Bl_Op_Data.data_Draw_Ur_Gripper_Motion_List)

    def data_Switch_Camera_Loc_Rot_Value(loc_x, loc_y, loc_z, rot_x, rot_y,rot_z):  # You gotta input rotation value as degree.
        bpy.data.objects['Camera'].location[0] = loc_x
        bpy.data.objects['Camera'].location[1] = loc_y
        bpy.data.objects['Camera'].location[2] = loc_z
        bpy.data.objects['Camera'].rotation_euler[0] = math.radians(rot_x)
        bpy.data.objects['Camera'].rotation_euler[1] = math.radians(rot_y)
        bpy.data.objects['Camera'].rotation_euler[2] = math.radians(rot_z)
