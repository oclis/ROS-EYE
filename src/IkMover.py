import bpy
from maviz import *
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp
from bl_op_flag import Bl_Op_Flag as bof

class IKMover:
    CMD_UP = 0
    CMD_DOWN = 1
    CMD_LEFT = 2
    CMD_RIGHT = 3
    CMD_MOVE = 4
    CMD_NUM_1 = 5
    CMD_NUM_3 = 6
    CMD_NUM_4 = 7
    CMD_NUM_5 = 8
    CMD_NUM_6 = 9
    CMD_NUM_7 = 10
    CMD_NUM_8 = 11
    CMD_NUM_9 = 12
    CMD_NUMPAD_PLUS = 13
    CMD_NUMPAD_MINUS = 14

    def __init__(self, bl_obj, bl_ik_control, speed_directions = (1.0, 0, 1.0), speed_value = 1):
        print('Mover init')

        self.FLAG_LEFT = False
        self.FLAG_RIGHT = False
        self.FLAG_UP = False
        self.FLAG_DOWN = False

        self.glow_timer = 0
        self.glow_time = 0.01

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

        self.position = [0, 0, 0]
        self._visible = True
        self._glow = False
        self.command_map = {
            self.CMD_UP: self._decrease_x,
            self.CMD_DOWN: self._increase_x,
            self.CMD_LEFT: self._decrease_y,
            self.CMD_RIGHT: self._increase_y,
            self.CMD_MOVE: self._move,
            self.CMD_NUM_1: self._num_1,
            self.CMD_NUM_3: self._num_3,
            self.CMD_NUM_4: self._num_4,
            self.CMD_NUM_5: self._num_5,
            self.CMD_NUM_6: self._num_6,
            self.CMD_NUM_7: self._num_7,
            self.CMD_NUM_8: self._num_8,
            self.CMD_NUM_9: self._num_9,
        } # self.CMD_RIGHT: self._increase_y,

        self.urManualControlMoveValue = 0.01
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

        for command in self.active_commands:
            self.command_map[command](time_delta)
            self.bound_location[0] = self.position[0]
            self.bound_location[1] = self.position[1]
            self.bound_location[2] = self.position[2]

    def _increase_y(self, time_delta):
        self._setCurRot(0,0,time_delta)

    def _decrease_y(self, time_delta):
        self._setCurRot(0,0,-time_delta)

    def _increase_x(self, time_delta):
        self._setCurRot(time_delta,0,0)

    def _decrease_x(self, time_delta):
        self._setCurRot(-time_delta,0,0)

    def _increase_axis(self, i, time_delta):
        self.position[i] +=  0.1

    def _decrease_axis(self, i, time_delta):
        self.position[i] -= 0.1

    def _move(self, time_delta):
        pass
        # print('move  x=',self.position[0],' z=',self.position[2])
    def _rotate(self, time_delta):
        pass

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

    def _num_1(self, time_delta):
        self.numkey_x = -self.urManualControlMoveValue
        self.numkey_y = 0.0
        self.numkey_z = -self.urManualControlMoveValue
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()
        # print("NUMPAD_1")

    def _num_3(self, time_delta):
        self.numkey_x = self.urManualControlMoveValue
        self.numkey_y = 0.0
        self.numkey_z = -self.urManualControlMoveValue
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()

    def _num_4(self, time_delta):
        self.numkey_x = -self.urManualControlMoveValue
        self.numkey_y = 0.0
        self.numkey_z = 0.0
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()

    def _num_5(self, time_delta):
        self.numkey_x = 0.0
        self.numkey_y = 0.0
        self.numkey_z = -self.urManualControlMoveValue
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()
        # print("NUMPAD_5")

    def _num_6(self, time_delta):
        self.numkey_x = self.urManualControlMoveValue
        self.numkey_y = 0.0
        self.numkey_z = 0.0
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()

    def _num_7(self, time_delta):
        self.numkey_x = 0.0
        self.numkey_y = self.urManualControlMoveValue
        self.numkey_z = 0.0
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()

    def _num_8(self, time_delta):
        self.numkey_x = 0.0
        self.numkey_y = 0.0
        self.numkey_z = self.urManualControlMoveValue
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()

    def _num_9(self, time_delta):
        self.numkey_x = 0.0
        self.numkey_y = -self.urManualControlMoveValue
        self.numkey_z = 0.0
        self._setCurPos(self.numkey_x, self.numkey_y, self.numkey_z)
        self.urManualControl()

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
