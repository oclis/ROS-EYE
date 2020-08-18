
import bpy
from maviz import *

class IKMover:
    CMD_MOVE = 0

    def __init__(self, bl_obj, bl_ik_control, speed_directions=(1.0, 0, 1.0), speed_value=1):
        print('Mover init')       
        self.glow_timer = 0
        self.glow_time = 0.01
        self.x_range_base = [0, 0]
        self.z_range_base = [0, 0]
        self.ranges = [
            (0, 0),
            (0, 0),
            (0, 0),
        ]

        self._speed_value = speed_value
        self._speeds = speed_directions
        self.speed = speed_value
        self.bound_location = bl_ik_control.location
        self.bound_scale = bl_ik_control.scale
        self.bound_glow_control = bl_obj.scale
        self.blender_object = bl_obj
        self.dimensions = bl_obj.dimensions
        self.rotation = bl_ik_control.rotation_euler

        self.urManualControlFlag = False

        self.position = [0, self.bound_location[1], 0]
        self._visible = True
        self._glow = False

        self.urManualControlMoveValue = 0.1
        self._urChangePoseY = 8

        self.active_commands = set()    

    @property
    def speed(self):
        return self._speed_value

    @speed.setter
    def speed(self, value):
        self._speed_value = value

    def on_hit(self):
        self.resize(0.8)
        self.glow = True

    def resize(self, factor):
        self.bound_scale[0] = factor * self.bound_scale[0]
        self.bound_scale[2] = factor * self.bound_scale[2]

    def set_size(self, value):
        self.bound_scale[0] = value
        self.bound_scale[2] = value

    def start_command(self, command):
        self.active_commands.add(command)

    def stop_command(self, command):
        try:
            self.active_commands.remove(command)
        except KeyError:
            pass

    @property
    def visible(self):
        return self._visible

    @property
    def cur_location(self):
        return self.bound_location

    @property
    def cur_roatation(self):
        return self.rotation

    @visible.setter
    def visible(self, visible):
        self._visible = visible

    def update(self, time_delta):
        if self.glow and self.glow_timer > 0:
            self.glow_timer -= time_delta
            if self.glow_timer <= 0:
                self.glow = False

        if (self.active_commands):
            self.bound_location[0] = self.position[0]
            self.bound_location[2] = self.position[2]

    def urManualControl(self):
        if self.urManualControlFlag == True:
            URxMoveToPoseOperator(1,0,0,0)

    def _setCurPos(self, xp, yp, zp):
        self.position[0] += xp
        self.position[1] += yp
        self.position[2] += zp

    def _setCurRot(self, xp, yp, zp):
        self.rotation[0] += xp
        self.rotation[1] += yp
        self.rotation[2] += zp

    def _setLocation(self,xp, yp, zp):
        self.bound_location[0]  = xp
        self.bound_location[1]  = yp
        self.bound_location[2]  = zp

    def _setRotate(self, xp, yp, zp):
        self.rotation[0] = xp
        self.rotation[1] = yp
        self.rotation[2] = zp

    @property
    def glow(self):
        return self._glow

    @glow.setter
    def glow(self, value):
        if value:
            self.bound_glow_control[0] = 1
            self.glow_timer = self.glow_time
        else:
            self.bound_glow_control[0] = 0

        self._glow = value        
