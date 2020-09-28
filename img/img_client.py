from threading import *
from socket import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QImage
import numpy as np
import cv2
import datetime
import os

img_date = datetime.datetime.now().strftime("%Y%m%d")
PATH = '../../../img_fursys/' + img_date


class Signal(QObject):
    recv_signal = pyqtSignal(np.ndarray)
    disconn_signal = pyqtSignal()


class ClientSocket:
    fileCounter = 0

    def __init__(self, parent):
        print('ClientSocket int')
        self.parent = parent
        self.recv = Signal()
        self.disconn = Signal()

        self.bConnect = False
        #self.bMode = False
        self.bMode = "ColorA"
        self.create_folder(PATH)

    def __del__(self):
        self.stop()

    def connectServer(self, ip, port):
        self.client = socket(AF_INET, SOCK_STREAM)

        try:
            self.client.connect((ip, port))
        except Exception as e:
            print('Connect Error : ', e)
            return False
        else:
            self.bConnect = True
            self.t = Thread(target=self.receive, args=(self.client,))
            self.t.start()
            print('Connected')

        return True

    def stop(self):
        self.bConnect = False
        if hasattr(self, 'client'):
            self.client.close()
            del (self.client)
            print('Client Stop')
            self.disconn.disconn_signal.emit()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)

        return buf

    def receive(self, client):
        #time = 0
        #timeVal = 3
        while self.bConnect:
            try:
                #time +=1
                states = self.recvall(self.client, 6)
                length = self.recvall(self.client, 16)
                StringData = self.recvall(self.client, int(length))
                states = states.decode()
                state_list = states.split('@')
                action_state = state_list[0]
                goods_state = state_list[1]
                camera_state = state_list[2]
                #print("action state :" + action_state)
                #print("camera_state  :" + camera_state)
                #print("good state : " + goods_state)
                data = np.fromstring(StringData, dtype='uint8')
                decode_img = cv2.imdecode(data, 1)
                img_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

                #if time == timeVal :
                if action_state == 'A' and goods_state == 'Y':
                    if camera_state == "CA" :
                        filename = img_time + '_colorA.jpg'
                        PATHA = PATH + "/colorA"
                        self.create_folder(PATHA)
                        cv2.imwrite(os.path.join(PATHA, filename), decode_img)
                        #print("camera_state : " + camera_state)
                    elif camera_state == "CB":
                        filename = img_time + '_colorB.jpg'
                        PATHB = PATH + "/colorB"
                        self.create_folder(PATHB)
                        cv2.imwrite(os.path.join(PATHB, filename), decode_img)
                    else :
                        pass
                    #time = 0

                if camera_state == "CA" :
                    #if not self.bMode:
                    if self.bMode =="ColorA":
                        self.recv.recv_signal.emit(decode_img)
                elif camera_state == 'CB':
                    if self.bMode =="ColorB":
                        self.recv.recv_signal.emit(decode_img)
                    #pass
                elif camera_state == 'DA':
                    #if self.bMode:
                    if self.bMode == "Depth":
                        self.recv.recv_signal.emit(decode_img)
                '''
                self.fileCounter += 1
                if self.fileCounter % 2 == 0:
                    if self.bMode:
                        self.recv.recv_signal.emit(decode_img)
                        filename = img_time + '_depth.jpg'  # depth 파일생성
                        if action_state == 'A' and goods_state == 'Y':
                            cv2.imwrite(os.path.join(PATH, filename), decode_img)
                else:
                    if not self.bMode:
                        self.recv.recv_signal.emit(decode_img)
                        filename = img_time + '_color.jpg'  # color 파일생성
                        if action_state == 'A' and goods_state == 'Y':
                            cv2.imwrite(os.path.join(PATH, filename), decode_img)
                '''
            except Exception as e:
                print('Recv() Error :', e)
                break

        self.stop()

    #def changeMode(self):
    def changeMode(self, mode):
        if not self.bConnect:
            print('Has no connect!')
            return
        if mode == "ColorA" :
            self.bMode = "ColorA"
            print('change mode == ColorA')
        elif mode == "ColorB" :
            self.bMode = "ColorB"
            print('change mode == ColorB')
        elif mode == "Depth" :
            self.bMode = "Depth"
            print('change mode == Depth')
        '''
        self.bMode = not self.bMode
        if self.bMode:
            print('change mode == True')
        else:
            print('False')
        '''

    def send(self, msg):
        if not self.bConnect:
            return
        try:
            self.client.send(msg.encode())
        except Exception as e:
            print('send() Error :', e)

    def create_folder(self,directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("폴더 생성 성공")
        except OSError:
            print('Error: Creating directory. ' + directory )