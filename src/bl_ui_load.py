import bpy
from bpy.props import (EnumProperty,
                        PointerProperty)
from bpy.types import (Operator,
                       AddonPreferences,
                       PropertyGroup)
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp
from bl_op_data import Bl_Op_Data as bod

import os


def my_callback(scene, context):
    file_List = bod.data_Get_File_List()
    return file_List

class MySetting(PropertyGroup):
    objs = EnumProperty(name="Objects",description="",items=my_callback)

class LoadEnumOperator(bpy.types.Operator):
    bl_idname = "object.load_enum_operator"
    bl_label = "Load Enum Operator"
    bl_property = "select_Name"
    select_Name = MySetting.objs
    DataPath = os.path.abspath('./Data')

    def execute(self, context):
        self.report({'INFO'}, "Selected:" + self.select_Name)
        budp.draw_Del_Pose()
        read_File = open("{}/{}".format(self.DataPath, self.select_Name), 'r')
        load_File_Data = eval(read_File.read())
        load_File_Data.reverse()
        budp.draw_Load_File_Data_Add_Pose(load_File_Data)
        read_File.close()

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}