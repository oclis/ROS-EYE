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
        self.bMode = False

         
    def __del__(self):
        self.stop()
 
    def connectServer(self, ip, port):
        self.client = socket(AF_INET, SOCK_STREAM)           
 
        try:
            self.client.connect( (ip, port) )
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
            del(self.client)
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
        while self.bConnect:            
            try:
                states = self.recvall(self.client,3)
                length = self.recvall( self.client, 16)
                StringData =  self.recvall(self.client, int(length))
                states = states.decode()
                state_list = states.split('@')
                action_state = state_list[0]
                goods_state = state_list[1]
                #print("action state :" + action_state)
                #print("good state : " + goods_state)
                data = np.fromstring(StringData, dtype='uint8')
                decode_img = cv2.imdecode(data, 1)
                img_date = datetime.datetime.now().strftime("%H_%M_%S")

                self.fileCounter += 1
                if self.fileCounter % 2 == 0:
                    if self.bMode:                  
                        self.recv.recv_signal.emit(decode_img)
                        filename = img_date + '_depth.jpg'  # depth 파일생성
                        if action_state == 'A' and goods_state == 'Y' :
                            cv2.imwrite(os.path.join(PATH,filename), decode_img)
                else:
                    if not self.bMode:                   
                        self.recv.recv_signal.emit(decode_img)
                        filename = img_date + '_color.jpg'  # color 파일생성
                        if action_state == 'A' and goods_state == 'Y':
                            cv2.imwrite(os.path.join(PATH,filename), decode_img)

            except Exception as e:
                print('Recv() Error :', e)                
                break
 
        self.stop()

    def changeMode(self):

        if not self.bConnect :
            print('Has no connect!')
            return
        self.bMode = not self.bMode
        if self.bMode :
            print('change mode == True')
        else:
            print('False')


    def send(self, msg):
        if not self.bConnect:
            return
        try:            
            self.client.send(msg.encode())
        except Exception as e:
            print('send() Error :', e)   
