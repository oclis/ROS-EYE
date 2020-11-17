import bpy
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof


def Bl_Ui_Draw_Pose_Operator(code):
    if (code == 0):
        Bl_Ui_Draw_Pose.draw_Del_Pose()

class Bl_Ui_Draw_Pose():
    draw_Pose_List_Count = 0
    mat_Magenta = bpy.data.materials.new("Magenta")
    mat_Magenta.diffuse_color = (float(1.5), 0.1, 1.0, 0.1)
    mat_Magenta.specular_color = (200.0, 1.0, 100.0)

    def draw_Pose(cur_loc, cur_rot):
        try:
            verts = [(0, 0, 3.0), (1.0, 0, 0), (0, 1.0, 0), (-1.0, 0, 0), (0, -1.0, 0)]
            faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 2, 3, 4)]
            poseMesh = bpy.data.meshes.new('Cube')
            poseMesh.from_pydata(verts, [], faces)
            poseObj = bpy.data.objects.new(f'pos{Bl_Ui_Draw_Pose.draw_Pose_List_Count}', poseMesh)
            poseObj.location = cur_loc
            poseObj.rotation_euler = cur_rot
            poseObj.scale = (0.01, 0.01, 0.01)
            # set color
            poseObj.active_material = Bl_Ui_Draw_Pose.mat_Magenta
            # link poseObject to blender
            bpy.context.collection.objects.link(poseObj)
            Bl_Ui_Draw_Pose.draw_Pose_List_Count += 1
            print('add pose : ', Bl_Ui_Draw_Pose.draw_Pose_List_Count)
        except Exception as e:
            print("draw_Pose",e)
            poseObj = -1

        return poseObj

    def draw_Pose_Path():
        try:
            pose_List   = bod.data_Draw_Ur_Pose_List
            point_List  = []
            pose_Count  = len(pose_List)
            for i in range(pose_Count):
                loc = pose_List[i].location
                point_List.append(loc)
            curve_Motion_Line = Bl_Ui_Draw_Pose.draw_Curve_From_Points('cur_motion_path', point_List)
            scn = bpy.context.scene
            scn.collection.objects.link(curve_Motion_Line)
            curve_Motion_Line.select_set(True)
        except Exception as e:
            print("draw_Pose_Path",e)
            pose_List = []
            point_List = []
            pose_Count = 0

        return {"FINISHED"}

    def draw_Curve_From_Points(name, points):
        try:
            # Adapted from https://blender.stackexchange.com/a/6751
            curve_data = bpy.data.curves.new(name, type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.resolution_u = 1
            curve_data.use_path_follow = True
            polyline = curve_data.splines.new(type='POLY')
            #polyline = curve_data.splines.new(type='NURBS')

            # Add the points to the curve
            polyline.points.add(len(points)-1)
            for i, point in enumerate(points):
                x, y, z = point
                polyline.points[i].co = (x, y, z, 1)
            # Create a curve object with the toolpath where the original object is
            curve_object = bpy.data.objects.new(name, curve_data)
        except Exception as e:
            print("draw_Curve_From_Points",e)
            curve_object = -1
        return curve_object

    def draw_Ui_Ur_Add_Pose(cur_loc, cur_rot):
        try:
            draw_Done_Pose_Obj = Bl_Ui_Draw_Pose.draw_Pose(cur_loc, cur_rot)
            bod.data_Set_Pose(draw_Done_Pose_Obj)
            bod.data_Set_Save_Curr_Ur_Pose(cur_loc, cur_rot)
            Bl_Ui_Draw_Pose.draw_Pose_Path()
        except Exception as e:
            print("draw_Ui_Ur_Add_Pose",e)

    def draw_Load_File_Ur_Add_Pose(load_pose_datas):
        try:
            for load_pose_data in load_pose_datas:
                load_Ur_Loc     = load_pose_data[0]
                load_Ur_Rot     = load_pose_data[1]
                load_Ur_Time    = load_pose_data[2]
                load_Ur_Radius  = load_pose_data[3]
                load_Ur_Gripper = load_pose_data[4]
                draw_Done_Pose_Obj = Bl_Ui_Draw_Pose.draw_Pose(load_Ur_Loc, load_Ur_Rot)
                bod.data_Set_Pose(draw_Done_Pose_Obj,load_Ur_Time,load_Ur_Radius,load_Ur_Gripper)
        except Exception as e:
            print("draw_Load_File_Ur_Add_Pose",e)

    def draw_Load_File_Data_Add_Pose(file_Data):
        try:
            bod.data_Reset_Pose()
            file_Load_Data = bod.data_Split_Load_Ur_Pose(file_Data)
            Bl_Ui_Draw_Pose.draw_Del_Pose()
            Bl_Ui_Draw_Pose.draw_Load_File_Ur_Add_Pose(file_Load_Data)
            Bl_Ui_Draw_Pose.draw_Pose_Path()
            Bl_Ui_Draw_Pose.draw_Reset()
        except Exception as e:
            print("draw_Load_file_Data_Add_Pose",e)
        finally:
            bof.FLAG_IK_MOVE_DRAG = True

    def draw_Del_Pose():
        try:
            Bl_Ui_Draw_Pose.draw_Reset()
            bod.data_Reset_Pose()
            bpy.ops.object.select_pattern(pattern="pos*", extend=False)
            bpy.ops.object.delete()
            bpy.ops.object.select_pattern(pattern="cur_motion_path*", extend=False)
            bpy.ops.object.delete()
        except Exception as e:
            print("draw_Del_Pose",e)

    def draw_Reset():
        try:
            Bl_Ui_Draw_Pose.draw_Pose_List_Count = 0
        except Exception as e:
            print("draw_Reset",e)