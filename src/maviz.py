# **** MAVIZ MAIN*****
import pathlib
import random
import tempfile

import bpy
import math
import os 
import sys
from bpy_extras.view3d_utils import region_2d_to_location_3d
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from bpy.types import Operator

from bl_ui_label import * 
from bl_ui_button import *
from bl_ui_checkbox import *
from bl_ui_slider import *
from bl_ui_up_down import *
from bl_ui_drag_panel import *
from bl_ui_draw_op import *
#from bl_urx import *
from bl_urx_server import URxMoveToPoseOperator, URxConfigChange

from IkMover import IKMover


# ======================================== #

from bl_urx_server import bl_Server
import threading
import time

global is_drag_G

# ======================================== #

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

        self.command_for_key_type = {
            'LEFT_ARROW': IKMover.CMD_LEFT,
            'RIGHT_ARROW': IKMover.CMD_RIGHT,
            'UP_ARROW': IKMover.CMD_UP,
            'DOWN_ARROW': IKMover.CMD_DOWN,
        }
        self.action_for_key_state = {
            'PRESS': self.mover.start_command,
            'RELEASE': self.mover.stop_command,
        }
        self.TPListCount = 0 # name count
        self.mat = bpy.data.materials.new("PKHG")
        self.mat.diffuse_color = (float(1.5), 0.1, 1.0, 0.1)
        self.mat.specular_color = (200.0, 1.0, 100.0)
        print('MAVIZ created')


        self.MavizTPoseLists = []
        self.MavizGMotions = []
        self.saveMavizTPoseLists = []
        self.urManualControlFlag = False
        self.urManualControlMoveValue = 0.1
        self.urMoveTimeLists = []
        self.urMoveRadiusLists = []
        self.urMoveTime = 0  # ur 이동 시간 값 저장 디폴트 0
        self.urMoveRadius = 0  # ur 이동 반지름 값 저장 디폴트 0
        self._urChangePoseY = 8

    # ==================================================================================== #

    def Start_maviz_thread(self):
        print("Threading is started")
        thread_server = threading.Thread(target=self.show_is_drag)
        thread_server.daemon = True
        thread_server.start()

    def show_is_drag(self):
        while (True):
            if (bl_Server.k_server == True):
                self.is_drag = False
            # time.sleep(0.01)

    # ==================================================================================== #

    def setMover(self, location):
        #print('setMover - move', location)
        self.mover._setLocation(location[0],location[1],location[2])

    def update(self, time_delta):
        self.mover.update(time_delta)

    def urManualControl(self):
        if self.urManualControlFlag == True:
            URxMoveToPoseOperator(1,0,0,0)

    def set_event(self, event, context):
        #if lm_Count > 1 :
        if event.type == 'R' and event.value == 'PRESS':
            if self.is_rotation:
                print('rotation off')
                self.is_rotation = False
            else:
                print('rotation On')
                self.is_rotation = True

        if event.type == 'MOUSEMOVE':
            if self.is_drag:
                self.x = (event.mouse_x - self.drag_offset_x)/2000
                self.z = self._urChangePoseY
                self.y = (event.mouse_y - self.drag_offset_y)/2000
                #print('cur x=',self.x,' y=',self.y)
                if self.x > 0.5 or self.y > 0.5:
                    self.is_drag = False
                    self.drag_offset_x = 0
                    self.drag_offset_y = 0
                    #print('release')  
                    self.mover.stop_command(IKMover.CMD_MOVE)
                else:
                    if self.is_rotation:
                        self.mover._setRotate(self.x,self.y)
                    else: 
                        self.mover._setCurPos(self.x,self.z,self.y)
                    self.mover.start_command(IKMover.CMD_MOVE)
                return

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.is_drag = True
                self.drag_offset_x =  event.mouse_x
                self.drag_offset_y =  event.mouse_y  
                area = bpy.context.window_manager.windows[0].screen.areas[0]
                #print('IK location = ',self.mover.bound_location)
                viewport = area.regions[0]
                if viewport is not None:
                    #print('region ', viewport.x,viewport.y,viewport.width,viewport.height)
                    region3D = context.space_data.region_3d
                    loc = region_2d_to_location_3d(viewport, region3D, (event.mouse_x, event.mouse_y), (0, 0, 0))             
                    #print('press',self.drag_offset_x,' ', self.drag_offset_y,' loc =',loc)
                #    self.mover.bound_location = loc
                    
            elif event.value == 'RELEASE':
                self.is_drag = False

                #print('release')
                self.mover.stop_command(IKMover.CMD_MOVE)
                if self.is_rotation:   # roation mode 
                    self.item._set_rotation(self.mover.cur_roatation)
                else: # axis move mode
                    self.item._set_new_pos(self.mover.cur_location)
                
        if event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                self.addPose(self.mover.cur_location, self.mover.cur_roatation)

        if event.type == 'PAGE_UP'  and event.value == 'PRESS':
            if self._urChangePoseY >= 9:
                self._urChangePoseY = 9
            else:
                self._urChangePoseY += 1
            URxConfigChange(0,self._urChangePoseY)

        if event.type == 'PAGE_DOWN' and event.value == 'PRESS':
            if self._urChangePoseY <= 5:
                self._urChangePoseY = 6
            else:
                self._urChangePoseY -= 1
            URxConfigChange(0,self._urChangePoseY)

        if event.type == 'NUMPAD_PLUS':
            if event.value == 'PRESS':
                if self.urManualControlMoveValue < 1:
                    self.urManualControlMoveValue = self.urManualControlMoveValue + 0.1
                    print(self.urManualControlMoveValue)
                if self.urManualControlMoveValue > 1:
                    self.urManualControlMoveValue = 1
                    print(self.urManualControlMoveValue)

        if event.type == 'NUMPAD_MINUS':
            if event.value == 'PRESS':
                if self.urManualControlMoveValue > 0:
                    self.urManualControlMoveValue = self.urManualControlMoveValue - 0.1
                    print(self.urManualControlMoveValue)
                if self.urManualControlMoveValue < 0:
                    self.urManualControlMoveValue = 0
                    print(self.urManualControlMoveValue)

        if event.type == 'NUMPAD_PERIOD':
            if event.value == 'PRESS':
                self.urManualControlFlag = True
                print(self.urManualControlFlag)

        if event.type == 'NUMPAD_0':
            if event.value == 'PRESS':
                self.urManualControlFlag = False
                print(self.urManualControlFlag)

        if event.type == 'NUMPAD_1':
            if event.value == 'PRESS':
                self.numkey_x = -self.urManualControlMoveValue
                self.numkey_y = self._urChangePoseY
                self.numkey_z = -self.urManualControlMoveValue
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_1")

        if event.type == 'NUMPAD_2':
            if event.value == 'PRESS':
                self.numkey_x = 0.0
                self.numkey_y = self._urChangePoseY
                self.numkey_z = -self.urManualControlMoveValue
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_2")

        if event.type == 'NUMPAD_3':
            if event.value == 'PRESS':
                self.numkey_x = self.urManualControlMoveValue
                self.numkey_y = self._urChangePoseY
                self.numkey_z = -self.urManualControlMoveValue
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_3")

        if event.type == 'NUMPAD_4':
            if event.value == 'PRESS':
                self.numkey_x = -self.urManualControlMoveValue
                self.numkey_y = self._urChangePoseY
                self.numkey_z = 0.0
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_4")

        if event.type == 'NUMPAD_5':
            if event.value == 'PRESS':
                self.addPose(self.mover.cur_location, self.mover.cur_roatation)
                #print("NUMPAD_4")

        if event.type == 'NUMPAD_6':
            if event.value == 'PRESS':
                self.numkey_x = self.urManualControlMoveValue
                self.numkey_y = self._urChangePoseY
                self.numkey_z = 0.0
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_6")

        if event.type == 'NUMPAD_7':
            if event.value == 'PRESS':
                self.numkey_x = -self.urManualControlMoveValue
                self.numkey_y = self._urChangePoseY
                self.numkey_z = self.urManualControlMoveValue
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_7")

        if event.type == 'NUMPAD_8':
            if event.value == 'PRESS':
                self.numkey_x = 0.0
                self.numkey_y = self._urChangePoseY
                self.numkey_z = self.urManualControlMoveValue
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_8")

        if event.type == 'NUMPAD_9':
            if event.value == 'PRESS':
                self.numkey_x = self.urManualControlMoveValue
                self.numkey_y = self._urChangePoseY
                self.numkey_z = self.urManualControlMoveValue
                self.mover._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
                self.mover.start_command(IKMover.CMD_MOVE)
                self.urManualControl()
                #print("NUMPAD_9")

        if event.type in self.command_for_key_type:
            action = self.action_for_key_state[event.value]            
            action(self.command_for_key_type[event.type])

    def addPose(self, cur_loc, cur_rot):
        global urMoveTime
        global urMoveRadius
        #print(self.urMoveTime)
        #print(self.urMoveRadius)
        verts = [(0, 0, 3.0), (1.0, 0, 0), (0, 1.0, 0), (-1.0, 0, 0), (0, -1.0, 0)]
        faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),(1,2,3,4)]
        poseMesh =  bpy.data.meshes.new('Cube') 
        poseMesh.from_pydata(verts, [], faces)
        poseObj = bpy.data.objects.new(f'pos{self.TPListCount}',poseMesh)
        poseObj.location = cur_loc
        poseObj.rotation_euler = cur_rot
        poseObj.scale = (0.1, 0.1, 0.1)
        # set color
        poseObj.active_material = self.mat
        self.MavizTPoseLists.append(poseObj)
        self.MavizGMotions.append(int(0))
        self.splitMavizTPoseLists(cur_loc)
        self.urMoveTimeLists.append(self.urMoveTime)
        self.urMoveRadiusLists.append(self.urMoveRadius)
        self.TPListCount+=1
        bpy.context.collection.objects.link(poseObj)
        print('add pose : ',self.TPListCount)


    def MavizdelPoseToBl(self):
        bpy.ops.object.select_pattern(pattern="pos*", extend=False)
        bpy.ops.object.delete()
        bpy.ops.object.select_pattern(pattern="cur_motion_path*", extend=False)
        bpy.ops.object.delete()
        self.MavizTPoseLists = []
        self.TPListCount = 0
        print(self.MavizTPoseLists)
        print("MavizdelPoseToBl clear")

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

    def splitMavizTPoseLists(self,cur_loc):
        pose_x = cur_loc.x
        pose_y = cur_loc.y
        pose_z = cur_loc.z

        poselist = [pose_x, pose_y, pose_z]
        self.saveMavizTPoseLists.append(poselist)

    def testButton(self, text):
        print(text)