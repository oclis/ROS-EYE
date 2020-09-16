from threading import *
from socket import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QImage
import numpy as np
import cv2

class Signal(QObject):  
    recv_signal = pyqtSignal(QImage)
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
                length = self.recvall( self.client, 16)
                StringData =  self.recvall(self.client, int(length))
                data = np.fromstring(StringData, dtype='uint8')
                decode_img = cv2.imdecode(data, 1)
                rgb_image = cv2.cvtColor(decode_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                    
                self.fileCounter += 1
                if self.fileCounter % 2 == 0: 
                    if self.bMode:                  
                        self.recv.recv_signal.emit(p)  
                else:
                    if not self.bMode:                   
                        self.recv.recv_signal.emit(p)    
               
                                              
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
