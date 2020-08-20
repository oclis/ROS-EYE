# **** MAVIZ MAIN*****
import pathlib
import random
import tempfile

import bpy
import math
import os 
import sys
from bpy_extras.view3d_utils import region_2d_to_location_3d
from mathutils import Euler
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from bpy.types import Operator

from bl_ui_label import * 
from bl_ui_button import *
from bl_ui_checkbox import *
from bl_ui_slider import *
from bl_ui_up_down import *
from bl_ui_drag_panel import *

from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp

from IkMover import IKMover

class TMobj:
    def __init__(self, bl_obj,bl_glow_control):
        print('item')

class PoseObj:
    def __init__(self, bl_obj):
        print('pose')        
        self.dimensions = bl_obj.dimensions
        self.location = bl_obj.location
        self.direction = bl_obj.rotation_euler
        self.position = [0,0,0]

    def _set_new_pos(self, new_pos):
        self.position[0] = new_pos[0]
        self.position[1] = new_pos[1]
        self.position[2] = new_pos[2]
    
    def _set_rotation(self, new_dir):
        self.direction[0] = new_dir[0]
        self.direction[1] = new_dir[1]
        self.direction[2] = new_dir[2]

class MotionDisplay:
    def __init__(self, bl_obj):
        print('Motion')

class Maviz:
    INITIAL_MOTION_SPEED = 8
    INITIAL_MOVER_SPEED = 10
    _mouseX = 0
    _mouseY = 0

    @staticmethod
    def setup_item(blender_object_name ):
        tmp_obj = bpy.data.objects[blender_object_name]
        item = PoseObj(tmp_obj)
        return item

    @staticmethod
    def setup_ik_mover(blender_object_name, glow_control_name):
        tmp_obj = bpy.data.objects[blender_object_name]
        glow_control_obj = bpy.data.objects[glow_control_name]
        mvt = IKMover(tmp_obj, glow_control_obj)
        return mvt

    def __init__(self, item: 'item', mover: 'IKMover'):
        self.mover = mover
        self.item = item
        self.mover.speed = self.INITIAL_MOVER_SPEED
        # 현재 커서 위치를 불러 와야 함. 
        self.mover._setCurPos(self.mover.cur_location[0],self.mover.cur_location[1],self.mover.cur_location[2])
        self.drag_offset_x = 0
        self.drag_offset_y = 0
       
        self.is_drag = False
        self.is_rotation = False  # mouse tracking mode 

        self.action_for_key_state = {
            'PRESS': self.mover.start_command,
            'RELEASE': self.mover.stop_command,
        }
        self.TPListCount = 0 # name count
        print('MAVIZ created')

        self.urManualControlFlag = False
        self.urManualControlMoveValue = 0.1
        self.urMoveTimeLists = []
        self.urMoveRadiusLists = []
        self.urMoveTime = 0  # ur 이동 시간 값 저장 디폴트 0
        self.urMoveRadius = 0  # ur 이동 반지름 값 저장 디폴트 0
        self._urChangePoseY = 8

    def setMover(self, location, rotation):
        self.mover._setLocation(location[0],location[1],location[2])
        self.mover._setRotate(rotation[0],rotation[1],rotation[2])

    def update(self, time_delta):
        self.mover.update(time_delta)

    def set_event(self, event, context):
        if event.type == 'P' and event.value == 'PRESS':
            if self.is_rotation:
                print('rotation off')
                self.is_rotation = False
            else:
                print('rotation On')
                self.is_rotation = True

        if event.type == 'MOUSEMOVE':
            if self.is_drag:
                self.x = (event.mouse_x - self.drag_offset_x) / 2000
                self.z = self._urChangePoseY
                self.y = (event.mouse_y - self.drag_offset_y) / 2000
                # print('cur x=',self.x,' y=',self.y)
                if self.x > 0.5 or self.y > 0.5:
                    self.is_drag = False
                    self.drag_offset_x = 0
                    self.drag_offset_y = 0
                    # print('release')
                    self.mover.stop_command(IKMover.CMD_MOVE)
                else:
                    if self.is_rotation:
                        self.mover._setRotate(self.x, self.z, self.y)
                    else:
                        self.mover._setCurPos(self.x, self.z, self.y)
                    self.mover.start_command(IKMover.CMD_MOVE)
                return

        if bof.FLAG_IK_MOVE_DRAG == True:
            if event.type == 'LEFTMOUSE':
                if event.value == 'PRESS':
                    self.is_drag = True
                    self.drag_offset_x =  event.mouse_x
                    self.drag_offset_y =  event.mouse_y
                    area = bpy.context.window_manager.windows[0].screen.areas[0]
                    viewport = area.regions[0]
                    if viewport is not None:
                        pass

                elif event.value == 'RELEASE':
                    self.is_drag = False
                    self.mover.stop_command(IKMover.CMD_MOVE)
                    if self.is_rotation: # roation mode
                        self.item._set_rotation(self.mover.cur_roatation)
                    else: # axis move mode
                        self.item._set_new_pos(self.mover.cur_location)
                
        if event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                budp.draw_Ui_Ur_Add_Pose(self.mover.cur_location, self.mover.cur_roatation)

        if event.type == 'H' and event.value == 'PRESS':
            bod.data_Switch_Camera_Loc_Rot_Value(6.5, -60, 5.4, 90, 0, 0)

        if event.type == 'W' and event.value == 'PRESS':
            bpy.ops.transform.translate(value=(0, 0, -1), orient_type='LOCAL')

        if event.type == 'S' and event.value == 'PRESS':
            bpy.ops.transform.translate(value=(0, 0, 1), orient_type='LOCAL')

        if event.type == 'D' and event.value == 'PRESS':
            bpy.ops.transform.translate(value=(1, 0, 0), orient_type='LOCAL')

        if event.type == 'A' and event.value == 'PRESS':
            bpy.ops.transform.translate(value=(-1, 0, 0), orient_type='LOCAL')

        if event.type == 'Q' and event.value == 'PRESS':
            bpy.ops.transform.rotate(value=0.01, orient_axis='Y', orient_type='LOCAL')

        if event.type == 'E' and event.value == 'PRESS':
            bpy.ops.transform.rotate(value=-0.01, orient_axis='Y', orient_type='LOCAL')

        if event.type == 'R' and event.value == 'PRESS':
            bpy.ops.transform.rotate(value=0.01, orient_axis='X', orient_type='LOCAL')

        if event.type == 'F' and event.value == 'PRESS':
            bpy.ops.transform.rotate(value=-0.01, orient_axis='X', orient_type='LOCAL')

            if event.type == 'ONE' and event.value == 'PRESS':
                if (bof.FLAG_LCTRL_STATUS == True):
                    print("1")
                    # bod.data_Switch_Camera_Loc_Rot_Value(6.5, -60, 5.4, 90, 0, 0)
                    

    def curPose(self):
        return self.mover.cur_location

    @property
    def UrMoveTime(self):
        return self.urMoveTime

    @UrMoveTime.setter
    def UrMoveTime(self,value):
        self.urMoveTime = value

    @property
    def UrMoveRadius(self):
        return self.UrMoveRadius

    @UrMoveRadius.setter
    def UrMoveRadius(self,value):
        self.urMoveRadius = value

    def getMavizTPoseLists(self):
        return self.MavizTPoseLists

    def getMavizGMotions(self):
        return self.MavizGMotions

    def getSaveMavizTPoseLists(self):
        saveData_ = self.saveMavizTPoseLists
        self.saveMavizTPoseLists = []
        return saveData_

    def getUrMoveTimeLists(self):
        movetimedata_ = self.urMoveTimeLists
        self.urMoveTimeLists = []
        return movetimedata_

    def getUrMoveRadiusLists(self):
        moveradiusdata_ = self.urMoveRadiusLists
        self.urMoveRadiusLists = []
        return moveradiusdata_

    def delSaveMavizTPoseLists(self):
        self.saveMavizTPoseLists = []

    def splitMavizTPoseLists(self,cur_loc,cur_rot):
        self.saveMavizTPoseLists.append([cur_loc.x, cur_loc.y, cur_loc.z, cur_rot.x, cur_rot.y, cur_rot.z])
