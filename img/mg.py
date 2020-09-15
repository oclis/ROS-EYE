from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,QPushButton, QTextEdit, QMainWindow
from PyQt5.QtGui import QPixmap,QImage
import socket
import time
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
import numpy as np
import img_client

HOST = '223.171.46.135'
PORT = 9999
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class Ui_ImageDialog(QWidget):
    def __init__(self):
        print('start')
        super().__init__()
        print('__init__')
        self.c = img_client.ClientSocket(self)
        print('ClientSocket')
        self.initUI()

    def __del__(self):
        self.c.stop()

    def initUI(self):
# 클라이언트 설정 부분
        print('initUI') 
        self.setWindowTitle('Image Client')
        ipbox = QHBoxLayout()

        gb = QGroupBox('서버 설정')
        ipbox.addWidget(gb)
        box = QHBoxLayout()
        label = QLabel('Server IP')
        
        self.ip = QLineEdit('223.171.46.135')
        self.ip.setInputMask('000.000.000.000;_')
        box.addWidget(label)
        box.addWidget(self.ip)
        label = QLabel('Server Port')
        self.port = QLineEdit(str(PORT))
        box.addWidget(label)
        box.addWidget(self.port)

        self.btn = QPushButton('접속')  
        self.btn.clicked.connect(self.connectClicked)
        box.addWidget(self.btn)
        gb.setLayout(box)
        # 채팅창 부분  
        infobox = QHBoxLayout()
        gb = QGroupBox('Image') 
        infobox.addWidget(gb)
        box = QVBoxLayout()
        
        label = QLabel('받은 메시지')
        box.addWidget(label)

        self.image_label = QLabel()
        self.image_label.setGeometry(QRect(110, 0, 750, 480))
        self.image_label.setText("")
        self.image_label.setPixmap(QtGui.QPixmap("c.jpg"))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setWordWrap(False)
        self.image_label.setObjectName("image_label")
        box.addWidget(self.image_label)

        label = QLabel('명령어')
        box.addWidget(label)
        self.sendmsg = QTextEdit()
        self.sendmsg.setFixedHeight(50)
        box.addWidget(self.sendmsg)
        hbox = QHBoxLayout()
        box.addLayout(hbox)
        self.sendbtn = QPushButton('보내기')
        self.sendbtn.setAutoDefault(True)
        self.sendbtn.clicked.connect(self.sendMsg)
        
        self.clearbtn = QPushButton('명령 지움')
        self.clearbtn.clicked.connect(self.clearMsg)
        hbox.addWidget(self.sendbtn)
        hbox.addWidget(self.clearbtn)
        gb.setLayout(box)
        
        vbox = QVBoxLayout()
        vbox.addLayout(ipbox)
        vbox.addLayout(infobox)
        self.setLayout(vbox)
        self.show()
        print('initUI end') 

    def connectClicked(self):
          if self.c.bConnect == False:
               ip = self.ip.text()
               port = self.port.text()
               if self.c.connectServer(ip, int(port)):
                    self.btn.setText('접속 종료')
               else:
                    self.c.stop()
                    self.sendmsg.clear()
                    self.btn.setText('접속')
          else:
                self.c.stop()
                self.sendmsg.clear()
                self.recvmsg.clear()
                self.btn.setText('접속')
    def connectSignal(self):
        self.c.recv.recv_signal.connect(self.update_image)
        self.c.disconn.disconn_signal.connect(self.updateDisconnect)    

    def updateImageLable(self, q_image):        
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

    def updateDisconnect(self):
        self.btn.setText('접속')

    def sendMsg(self):
        sendmsg = self.sendmsg.toPlainText()
        self.c.send(sendmsg)
        self.sendmsg.clear()

    def clearMsg(self):
        pass

    def closeEvent(self, e):
        self.c.stop() 

    @pyqtSlot(QImage)
    def update_image(self,q_img):
        self.updateImageLable(q_img)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_ImageDialog()
    ui.connectSignal()
    sys.exit(app.exec_())
