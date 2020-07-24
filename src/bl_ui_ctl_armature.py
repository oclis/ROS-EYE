import bpy
from bl_op_data import Bl_Op_Data as bod

class Bl_Ui_Ctl_Armature():

    def draw_Curr_Ur_FK():
        curr_Ur_Angle = bod.data_Get_Curr_Ur_Angle()
        if curr_Ur_Angle:
            Base = curr_Ur_Angle[1]
            Shoulder = curr_Ur_Angle[2]
            Elbow = curr_Ur_Angle[3]
            Wrist1 = curr_Ur_Angle[4]
            Wrist2 = curr_Ur_Angle[5]
            Wrist3 = curr_Ur_Angle[6]

            bpy.data.objects['Armature_UR'].pose.bones['Base'].rotation_euler.y = Base + 1.57079
            bpy.data.objects['Armature_UR'].pose.bones['Shoulder'].rotation_euler.y = Shoulder + 1.5708
            bpy.data.objects['Armature_UR'].pose.bones['Elbow'].rotation_euler.y = -Elbow
            bpy.data.objects['Armature_UR'].pose.bones['Wrist1'].rotation_euler.y = Wrist1 + 1.5708
            bpy.data.objects['Armature_UR'].pose.bones['Wrist2'].rotation_euler.y = Wrist2
            bpy.data.objects['Armature_UR'].pose.bones['Wrist3'].rotation_euler.y = Wrist3