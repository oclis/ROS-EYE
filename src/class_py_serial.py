#!/usr/bin/python

# -*- coding: utf-8 -*-
#import library-class
import serial
import time
import threading
import sys

#from serial import Serial
from cmd_state import cmd_State

class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._intances:
#            cls._instances[cls] = super(Singleton,cls).__call__(*args, **kwargs)
            cls._instances[cls] = super(Singleton,cls).__new__(*args, **kwargs)
        return cls._instances[cls]

    #def get_instatce():

class py3_serial(object):
    __metaclass__ = Singleton
    def __init__(self):
        self._dict = {}
        threading.Thread.__init__(self)
    #set PORT

        self.PORT='/dev/arduino'
        self.BaudRate=115200

    #set state_Manager
        self.state = cmd_State()
        print(self.state.operate)
        print(self.state.moving)
        print(self.state.enable)
        self._torqueState = True
    #Create PORT
        self.GRIPPER = serial.Serial() #GRIPPER=serial.Serial(PORT,BaudRate)

    #Connect PORT
    def connect_port(self):
        if self.isRunning() == False:
            print("state False")
            self.GRIPPER.baudrate = self.BaudRate
            self.GRIPPER.port = self.PORT
            self.GRIPPER.open()

            result=self.GRIPPER.readline().decode('utf8').replace(' ', '').replace('\n', '')
            if not result :
                print("RECONNECT")
            else:
                print(result)
        else:
            print("state True")

    #WRITE
    def write_port(self,data):
        self.GRIPPER.write(data.encode('utf-8'))
        print('COMAND : ' + data)

    #READ
    def read_port(self):
        result=self.GRIPPER.readline().decode('utf8').replace(' ', '').replace('\n', '')
        if not result :
            return

        return result

    #COMMAND
    def run_CMD(self,cmd,data=0):
        if cmd == 'd' or cmd == 'D': # delay setting, ex) run_CMD('d', (unsigined long)millisecond )
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd+str(data)) 
               self.state.set_operate(True)
            else:
                return

        elif cmd == 's' or cmd == 'S': # start loop, ex) run_CMD('s', (unsigined long)count_loop )
            if self.state.isEnable(cmd) == True:
                self.write_port(cmd+str(data))
                self.state.set_operate(True)
            else:
                return

        elif cmd == 'e' or cmd == 'E': # end loop, ex) run_CMD('e')
            if self.state.isEnable(cmd) == True:
                self.write_port('e')
                self.state.set_operate(True)
            else:
                return

        elif cmd == 'v' or cmd == 'V': # velocit setting, ex) run_CMD('v', (unsigined long)microsecond )
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd+str(data)) 
               self.state.set_operate(True)
            else:
                return

        elif cmd == 't' or cmd == 'T': # torque ON/OFF, ex) run_CMD('t', (int)Bool)
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd+str(data)) 
               self.state.set_operate(True)
            else:
                return

        elif cmd == 'r' or cmd == 'R': # boadr_reset, ex) run_CMD('r'),
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd) 
               self.state.set_operate(True)
            else:
                return

        elif cmd == 'i' or cmd == 'I':
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd)
               self.state.set_operate(True)
            else:
               return

        elif cmd == 'h' or cmd == 'H':
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd)#self.write_port(cmd+str(data))
               self.state.set_operate(True)
            else:
               return

        elif cmd == 'p' or cmd == 'P':
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd+str(data))
               self.state.set_operate(True)
            else:
               return

        elif cmd == 'g' or cmd == 'G':
            if self.state.isEnable(cmd) == True:
               self.write_port(cmd+str(data))
               self.state.set_operate(True)
            else:
               return

        while self.state.operate:
            time.sleep(0.1)
    #check
    def isRunning(self):
            return self.GRIPPER.isOpen()

    def thread_read(self,name):
        while self.isRunning():#run_event.is_set():
            try:
                str_data =self.read_port()
                str_state=str_data.split(':')[0]
                print("recieve: "+str_data)

                if str_state == 'mode_1' or 'mode_2' or 'mode_3' or 'set_vel':
                    self.state.set_operate(False)

                    if str_state == 'mode_2':
                        self.state.set_moving(True)
                    elif str_state == 'mode_3':
                        self.state.set_moving(False)

                if str_data[0:4] == 'stop':#
                    self.state.set_moving(False)#

                if str_data[0:6] == 'torque':
                    self.state.set_operate(False)
                    if str_data == 'torqueon\r':
                        self._torqueState = True
                    elif str_data == 'torqueoff\r':
                        self._torqueState = False

                    self.torqueState(self._torqueState)

                if str_state[0:9] == 'resetloop':
                    print("reset message_1")
                    self.state.set_operate(False)
                    self.state.set_moving(True)
                    self._boardState = False
                    self.boardState(self._boardState)

                if str_state[0:7] == 'CONNECT':
                    print("reset message_2")
                    self.state.set_moving(False)
                    self._boardState = True
                    self.boardState(self._boardState)

                if str_state[0:8] == 'INITMODE':
                    self.state.set_operate(False)
                    self.state.set_moving(True)
                    self._poseState = False
                    self.poseState(self._poseState)

                if str_state[0:12] == 'HOMEPOSITION':
                    self.state.set_moving(False)
                    self._poseState = True
                    self.poseState(self._poseState)

                if str_data[0:4] == 'grip':
                    self.state.set_moving(False)
                    self._poseState = True
                    self.poseState(self._poseState)

#                if str_data[0:4] == 'stop':
#                    self.state.set_moving(False)
#                    self._poseState = True
#                    self.poseState(self._poseState)

#                if str_data[0:4] == 'down':
#                    self.state.set_moving(False)
#                    self._poseState = True
#                    self.poseState(self._poseState)

#                if str_data[0:4] == 'up':
#                    self.state.set_moving(False)
#                    self._poseState = True
#                    self.poseState(self._poseState)

                    
    #            elif str_state == 'subloop':
    #                print(str_data.split(':')[1])
            except Exception as e:
                print (e)
                pass

    def run_rx(self):
        print('serial main')
        self.connect_port()
        self.rx = threading.Thread(target=self.thread_read, args=("rx",))

        self.rx.setDaemon(True)
        self.rx.start()
        time.sleep(.5)

    def disconnect_port(self):
        self.GRIPPER.close()
        print('close')

    def set_torqueState(self, torqueState_func):
        self.torqueState_func = torqueState_func 

    def set_boardState(self, boardState_func):
        self.boardState_func = boardState_func

    def set_poseState(self, poseState_func):
        self.poseState_func = poseState_func

    def torqueState(self, torqueState_func):
        self.torqueState_func(self) 

    def boardState(self, boardState_func):
        self.boardState_func(self)

    def poseState(self, poseState_func):
        self.poseState_func(self)

    def main(self):
        print('serial main')
        self.connect_port()
        rx = threading.Thread(target=self.thread_read, args=("rx",))

        rx.setDaemon(True)
        rx.start()

        time.sleep(.5)

        while self.isRunning():
            try:
                cmd = input("COMMAND = ")
                length = len(cmd)

                if length == 1:
                    self.run_CMD(cmd[0])
                elif length > 1 :
                    self.run_CMD(cmd[0], int(cmd[1:length]))

                while self.state.operate:
                    time.sleep(0.1)

            except KeyboardInterrupt:
                self.GRIPPER.close()
                print('close')

#if __name__ == '__main__':
#
#    ser = py3_serial()
#    ser.run_rx()
#    ser.run_CMD('e')
#    ser.run_CMD('e')
#    ser.run_CMD('e')
#    ser.run_CMD('e')
#    ser.run_CMD('e')
#    ser.run_CMD('e')

