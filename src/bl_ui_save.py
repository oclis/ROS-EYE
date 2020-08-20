import os
import bpy
from bl_op_server import *
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof

class DialogOperator(bpy.types.Operator):
    bl_idname = "object.dialog_operator"
    bl_label = "Motion Save"
    DataPath = os.path.abspath('./Data')

    Name: bpy.props.StringProperty(name = "저장할 이름을 입력하세요")

    def execute(self, context):
        message = ("What you typed : {}".format(self.Name))
        self.report({'INFO'}, message)
        save_Pose_Data = bod.data_Get_Save_To_File()
        print(save_Pose_Data)

        if save_Pose_Data: # Datas => jointangle_Datas
            write_File = open("{}/{}.txt".format(self.DataPath, self.Name), 'w')
            write_File.write(str(save_Pose_Data))
            write_File.close()
        bof.FLAG_IK_MOVE_DRAG = True

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

