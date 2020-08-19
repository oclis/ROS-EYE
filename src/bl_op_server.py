#!/usr/bin/env python3

import os
import cv2
import bpy
import math
import time
import socket
import threading
import numpy as np

from bl_urx_script import *
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof # ====================> SeonWoo

def URxMoveToPoseOperator(code, cmd1 = 0, cmd2 = 0, cmd3 = 0):
  #ik_target = bpy.data.objects['IK Target']
  if(code == 0):    #"Home Posistion"
    print("debug : URxMoveToPoseOperator code : 0 , Home")
    bl_Server.set_Off_Teach_Mode()
    bl_Server.move_Home()

  elif(code == 1):  #right "Run" btn
    print("debug : URxMoveToPoseOperator code : 1 , Run")
    time = cmd1
    radius = cmd2
    gMotion = cmd3
    armature_obj = bpy.data.objects['Armature_ik']

    robotMode = "movej"
    if (robotMode == "movej"):
        bl_Server.movej(bod.data_Split_Local_Orientation(armature_obj), time, radius, gMotion)
    elif(robotMode == "speedj"):
        print("debug code 1")
        bl_Server.speedj(bod.data_Split_Local_Orientation(armature_obj.pose.bones))

  elif(code == 2):  #"STOP" btn
    print("debug : URxMoveToPoseOperator code : 2 , STOP")
    bl_Server.emergency()

  elif(code == 3):
    print("debug : ")

  elif(code == 4):
    print("debug : ")

  elif(code == 5):
    print("debug : ")

  elif(code == 6):  #"PROGRAM_shut_Down"
    print("debug : URxMoveToPoseOperator code : 6 , PROGRAM_shut_Down")
    bl_Server.shut_Down()

  elif(code == 7):     #왼쪽위에
    # print("debug : ")
    print("Left max")
    bpy.data.objects['ik_control'].location.x = 0.0
    bpy.data.objects['ik_control'].location.y = 10.0
    bpy.data.objects['ik_control'].location.z = 8.0

  elif(code == 8):      #왼쪽아래
    # print("debug : ")
    print("Left min")
    bpy.data.objects['ik_control'].location.x = 0.0
    bpy.data.objects['ik_control'].location.y = 10.0
    bpy.data.objects['ik_control'].location.z = 2.0

  elif(code == 9):      #오른쪽위에
    # print("debug : ")
    print("Right max")
    bpy.data.objects['ik_control'].location.x = 10.0
    bpy.data.objects['ik_control'].location.y = 10.0
    bpy.data.objects['ik_control'].location.z = 8.0

  elif (code == 10):    #오른쪽아래
    # print("debug : ")
    print("Right min")
    bpy.data.objects['ik_control'].location.x = 10.0
    bpy.data.objects['ik_control'].location.y = 10.0
    bpy.data.objects['ik_control'].location.z = 2.0
    
  elif (code == 11):
    print("debug : ")

  elif (code == 12):
    print("debug : ")

  elif (code == 13):  # "set_Velo"
    print("debug : URxMoveToPoseOperator code : 13 , set_Velo")
    bl_Server.set_Velo(cmd1,cmd2)

  elif (code == 14):
    print("debug : ")

  elif (code == 15):
    print("debug : ")

  return {'FINISHED'}


def URxConfigChange(code,cmd1):
    if(code == 0):
        bl_Server.ur_Pose_Change_Y = cmd1

    return {'FINISHED'}

def URxStateCheck(code):
    if(code == 0):
        bl_Server.finish_Work()

    return {'FINISHED'}



class Bl_Maviz_Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.FLAG_CLOUD_POINT = False  # 포즈 셋 플레그 True 일 때만 Xavier에서 데이터를 받고 받자 마자 False로 변경됨
        self.FLAG_AUTO_CONTROL_MODE = False  # 수동 자동 모드 확인
        self.FLAG_CHECK_XAVIER_DATA = False
        self.FLAG_STATE_UR_RUN = False
        self.lock = threading.Lock()  # 스레드락
        self.clients = {}  # 접속된 클라이언트 리스트
        self.client_Count = 0  # client의 수
        self.xavier_Pose_Datas = 0  # XAVIER에서 전송 받은 포즈를 담기 위한 변수
        self.xavier_Image_Datas = 0  # 영상 데이터를 받기 위한 변수
        self.print_Curr_Ur_Angle_Data = []  # 현재 로봇의 각 축의 라디안 값을 담기 위한 list (화면 출력용)
        self.auto_ModeLoadNumber = 0
        self.auto_ModeLists = 0
        self.auto_ModeListCount = 0
        self._changePoseY = 8

        # Server Init###########################################################
        self.host = self.get_Ip()
        self.port = 30002
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(3)
        self.max_bytes = 2048  # 최대 수신 데이터
        #######################################################################

    def get_Ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.0.1',0))
        ip = s.getsockname()[0]
        return ip

    def run(self):
        # 서버 스레드 스타트
        thread_server = threading.Thread(target=self.server)
        thread_server.daemon = True
        thread_server.start()
        # 클라이언트 접속 여부 확인 스레드
        thread_client_Conn_Check = threading.Thread(target=self.client_Conn_Check)
        thread_client_Conn_Check.daemon = True
        thread_client_Conn_Check.start()
        # 이미지 실시간 출력 스레드
        thread_show_Image = threading.Thread(target=self.show_Image)
        thread_show_Image.daemon = True
        thread_show_Image.start()
        # 서버가 Robot에게 실행 유무를 전송하는 스레드
        thread_server_Alive = threading.Thread(target=self.server_Alive_Thread)
        thread_server_Alive.daemon = True
        thread_server_Alive.start()


    def server(self):
        print("Server Started")
        try:
            self.accept_Client()
        except Exception as e:
            print(e)

    def auto_Mode(self):
        print("debug auto_Mode")
        loadNumber_ = self.auto_ModeLists
        self.auto_ModeLists = 0
        self.load_TPose_Lists(loadNumber_)
        self.auto_ModeListCount = self.auto_ModeListCount - 1
        self.FLAG_CHECK_XAVIER_DATA = False
        #if self.auto_ModeLists == 0:


    def accept_Client(self):
        while (True):
            client_socket, addr = self.server_socket.accept()
            print('accept', addr)
            # 최초 접속시 XAVIER OR ROBOT 이라는 디바이스 명을 받아 저장하여 클라이언트 관리
            deviceName = client_socket.recv(1024).decode("utf-8")
            # 클라이언트 정보 저장
            self.add_Client(deviceName, client_socket, addr)

            # 각 클라이언트의 디바이스 명으로 각각의 recv 스레드 생성
            recv_thread = threading.Thread(target=self.recv, args=(client_socket, addr, deviceName))
            recv_thread.daemon = True
            recv_thread.start()

    def server_Alive_Thread(self):
        while(1):
            time.sleep(1)
            devices = self.clients.keys()
            for device in devices:
                if device == "EMC":
                    self.server_Alive()

    # 클라이언트 생존 여부 확인
    def client_Conn_Check(self):
        check_Count = 0
        while (True):
            devices = self.clients.keys()

            try:
                if devices:
                    for device in devices:
                        if device == "ROBOT" and "ROBOT" not in bod.data_Tcp_Clinet_List:
                            bod.data_Tcp_Clinet_List[device] = self.client_Count
                            self.client_Count += 1
                        if device == "XAVIER" and "XAVIER" not in bod.data_Tcp_Clinet_List:
                            bod.data_Tcp_Clinet_List[device] = self.client_Count
                            self.client_Count += 1
                        if device == "EMC" and "EMC" not in bod.data_Tcp_Clinet_List:
                            bod.data_Tcp_Clinet_List[device] = self.client_Count
                            self.client_Count += 1

                if check_Count == 100:
                    if len(bod.data_Tcp_Clinet_List) != 0:
                        print("Connect Client : ", bod.data_Tcp_Clinet_List)
                    else:
                        print("Not Connected")
                    check_Count = 0
                check_Count += 1
            except Exception as e:
                print(e)
            time.sleep(0.1)

    def show_Image(self):
        while True:
            time.sleep(0.1)
            if self.xavier_Image_Datas:
                decode_img = cv2.imdecode(np.fromstring(self.xavier_Image_Datas, dtype='uint8'), 1)  # 320,240
                resize_img = cv2.resize(decode_img, dsize=(640, 480))  # 640,480
                cv2.imshow('RealSense-server', resize_img)
                cv2.waitKey(1)

    def recv_All(self, sock, count):
        buf = b''
        while count:
            # newbuf = sock.recv(count)
            newbuf = sock.recv(self.max_bytes)
            # print(newbuf,type(newbuf),len(newbuf))
            if not newbuf:
                return None

            buf += newbuf
            count -= len(newbuf)
            if count < 0:
                count = 0
        return buf

    def recv(self, client, addr, deviceName):
        while (True):
            try:

                recv_data = client.recv(self.max_bytes)
                length = len(recv_data)
                # print("\n$$$", length, type(recv_data))

                # 데이터 길이 및 유무 확인 후 없다면 연결 종료
                if not recv_data:
                    print("Disconnected by - ", deviceName, ':', addr[0], ':', addr[1])
                    self.del_Client(deviceName)
                    client.close()
                    break

                # 디바이스 명이 XAVIER 일 경우 받은 데이터 처리
                if deviceName == 'XAVIER':
                    buffer = recv_data.decode()
                    print("XAVIER Read : {}".format(buffer))
                    print(type(buffer))
                    if buffer == '1' and self.FLAG_AUTO_CONTROL_MODE == True and self.FLAG_STATE_UR_RUN == False:
                        try:
                            print("debug XAVIER Read")
                            self.auto_ModeLists = self.auto_ModeLoadNumber
                            self.auto_ModeListCount = self.auto_ModeListCount + 1
                            self.FLAG_CHECK_XAVIER_DATA = True
                            self.FLAG_STATE_UR_RUN = True
                            print("debug XAVIER Read out ")
                        except Exception as e:
                            print(e)


                    # 이미지 처리 부분
                    # buffer = recv_data
                    # if (length > self.max_bytes - 1) or (length == 8):
                    #     # Image_LENGTH + jpg_IMAGE
                    #     # print(recv_data[0:8])
                    #     try:
                    #         img_length = int(buffer[0:8])  # TRY False(str or bytes)
                    #         len_data = img_length - length - 8
                    #         self.xavier_Image_Datas = buffer[8:] + self.recv_All(client, len_data)
                    #
                    #         # for end
                    #     except:
                    #         # print(">>> int change error !")
                    #         pass
                    #         try:
                    #             str_data = buffer[0:6].decode()
                    #             # print(str_data)
                    #             # print(">>>",length,type(str_data)) #'str'
                    #         except:
                    #             pass
                    #             # print(">>> str change error !")
                    #
                    # # 포즈 처리 부분
                    # else:
                    #     if self.FLAG_CLOUD_POINT == True:  # self.FLAG_CLOUD_POINT 가 True 일 경우만 포즈 데이터를 저장
                    #         try:
                    #             xavierPoseData = buffer.decode()
                    #             if (length < 3):
                    #                 print("> none data")
                    #             elif (length < 7):
                    #                 str_data = xavierPoseData
                    #                 print("> Server check")
                    #             else:
                    #                 print(xavierPoseData)
                    #                 self.lock.acquire()  # 스레드 락 (테스트후 삭제 예정)
                    #                 self.xavier_Pose_Datas = xavierPoseData
                    #                 self.lock.release()
                    #                 self.FLAG_CLOUD_POINT = False
                    #                 print("self.FLAG_CLOUD_POINT", self.FLAG_CLOUD_POINT)
                    #         except:
                    #             print(">>> data Error !!")
                    #print("XAVIER Read : {}".format(recv_data))

                # 디바이스 명이 ROBOT 일 경우 받은 데이터 처리
                elif deviceName == 'ROBOT':
                    buffer = recv_data.decode()
                    if buffer == "fw":
                        print("Work is finished")
                    else:
                        buffer_ = eval(buffer)
                        if buffer_[0] == 0:
                            curr_Ur_State = buffer_
                            bod.robot1.robot_Set_Curr_Ur_State(curr_Ur_State)
                            # print("ROBOT State Read : {}".format(buffer_))
                        if buffer_[0] == 1:
                            curr_Ur_Angle = buffer_
                            bod.data_Set_Curr_Ur_Angle(curr_Ur_Angle)

                # 디바이스 명이 EMC 일 경우 받은 데이터 처리 비상시 긴급 정지를 위해 ROBOT에서 스레드로 계속 확인
                elif deviceName == 'EMC':
                    buffer = recv_data.decode()
                    print("EMC Read : {}".format(buffer))

                # 디바이스 명 없이 접속
                else:
                    buffer = recv_data.decode()
                    print("Unkown Device Name Read : {}".format(buffer))
                    print("Unkown Device Name Disconnected by - ", addr[0], ':', addr[1])
                    client.close()
                    break

            except Exception as e:
                print("Something's wrong : {}".format(e))
                client.close()
                self.del_Client(deviceName)
                break

    # 전 클라이언트에게 데이터 순차 전송
    def send_To_All(self, data):
        if len(self.clients) != 0 :
            for client in self.clients.values():
                client.sendall(bytes(data, encoding='utf8'))

    # 로봇에게만 데이터 전송
    def send_To_Robot(self, datas):
        if "ROBOT"in self.clients:
            client = self.clients.get("ROBOT")
            client.sendall(bytes(datas, encoding='utf8'))
        else:
            print("Not Connect ROBOT")

    def send_To_Emc(self, datas):
        if "EMC"in self.clients:
            client = self.clients.get("EMC")
            client.sendall(bytes(datas, encoding='utf8'))
        else:
            print("Not Connect EMC")

    def send_To_Xavier(self, datas):
        if "XAVIER"in self.clients:
            client = self.clients.get("XAVIER")
            client.sendall(bytes(datas, encoding='utf8'))
        else:
            print("Not Connect XAVIER")

    # 클라이언트 추가
    def add_Client(self, deviceName, client, addr):
        self.lock.acquire()
        self.clients[deviceName] = (client)
        self.lock.release()
        print("Join Client : ", deviceName)

    # 클라이언트 삭제
    def del_Client(self, deviceName):
        try:
            self.lock.acquire()
            del self.clients[deviceName]
            del bod.data_Tcp_Clinet_List[deviceName]
            self.client_Count -= 1
            self.lock.release()
        except Exception as e:
            print("del_Client error", e)

    # Robot의 현재 각 joint angle값을 리턴하여 블렌더의 Robot을 이동
    def getFK(self):
        data_ = self.print_Curr_Ur_Angle_Data
        self.print_Curr_Ur_Angle_Data = []
        return data_

    # ROBOT과 통신 CMD
    def movej(self, angles, time, radius, gmotion):
        script = URScript()
        script.movej(angles, time, radius, gmotion)
        print(script.text)
        self.send_To_Robot(script.text)

    def speedj(self,angles):    #speedj 테스트를 위해 추가
        script = URScript()
        script.speedj(angles)
        print(script.text)
        self.send_To_Robot(script.text)

    def servoj(self,angles):
        script = URScript()
        script.servoj(angles)
        print(script.text)
        self.send_To_Robot(script.text)

    def emergency(self):
        script = URScript()
        script.emergency()
        self.send_To_Emc(script.text)

    def server_Alive(self):
        script = URScript()
        script.server_Alive()
        self.send_To_Emc(script.text)

    def move_Home(self):
        print("move_home")
        script = URScript()
        script.move_home()
        self.send_To_Robot(script.text)

    def set_Teach_Mode(self):
        print("set_Teach_Mode")
        script = URScript()
        script.TeachMode()
        self.send_To_Robot(script.text)

    def set_Velo(self,accel,velo):
        script = URScript()
        script.set_Velo(accel,velo)
        print(script.text)
        self.send_To_Robot(script.text)

    def set_Off_Teach_Mode(self):
        print("set_Off_Teach_Mode")
        script = URScript()
        script.offTeachMode()
        self.send_To_Robot(script.text)

    def set_Digital_Out(self, num, out):
        print("set_digital_out")
        script = URScript()
        script.set_digital_out(num, out)
        self.send_To_Robot(script.text)

    def finish_Work(self):
        print("finish_Work")
        script = URScript()
        script.finish_Work()
        print(script.text)
        self.send_To_Robot(script.text)

    # ROBOT 및 XAVIER shut_Down
    def shut_Down(self):
        try:
            print("ROBOT shut_Down")
            script = URScript()
            script.end_signal()
            self.send_To_Robot(script.text)
            # self.del_Client("ROBOT")
            # time.sleep((1))
            # self.del_Client("EMC")
            print("Sended ROBOT shut_Down Signal")
            #print("XAVIER shut_Down")
            #XAVIEREndSignal = [0, 0, 1, 0]
            #XAVIEREndSignal = str(XAVIEREndSignal)
            #self.send_To_All(XAVIEREndSignal)
            #self.del_Client("XAVIER")
            #print("Sended XAVIER shut_Down Signal")
        except Exception as e:
            print("shut_Down error", e)

    # FLAG 상태 변경
    def check_Xavier_Data(self):
        #print("self.check_Xavier_Data : ",self.FLAG_CHECK_XAVIER_DATA)
        #print("len(self.auto_ModeLists) : ",len(self.auto_ModeLists))
        return self.FLAG_CHECK_XAVIER_DATA

    def reset_Job_Lists(self):
        self.auto_ModeListCount = 0
        self.FLAG_CHECK_XAVIER_DATA = False
        self.auto_ModeLists = []

    def change_Flag_Could_Point(self):
        self.FLAG_CLOUD_POINT = True
        print("self.FLAG_CLOUD_POINT : ", self.FLAG_CLOUD_POINT)

    @property
    def ur_Pose_Change_Y(self):
        return self._changePoseY

    @ur_Pose_Change_Y.setter
    def ur_Pose_Change_Y(self,value):
        self._changePoseY = value
        print(self._changePoseY)

    @property
    def ur_State_Change(self):
        return self.FLAG_STATE_UR_RUN

    @ur_State_Change.setter
    def ur_State_Change(self,value):
        self.FLAG_STATE_UR_RUN = value

bl_Server = Bl_Maviz_Server()
bl_Server.run()