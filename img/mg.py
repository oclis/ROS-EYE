from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel,QGridLayout,QCheckBox,QMenu, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,QPushButton, QTextEdit,QComboBox
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
        super().__init__()
        self.c = img_client.ClientSocket(self)
        self.initUI()

    def __del__(self):
        self.c.stop()

    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI') 
        self.setWindowTitle('Magenta Robotics Inc')
        self.image_label = QLabel()
        self.rst_label = QLabel()
        # 영상처리 영역 #############################
        grid = QGridLayout()
        grid.addWidget(self.createInputImage(), 0, 0)
        grid.addWidget(self.createResultImage(), 1, 0)
        grid.addWidget(self.createInfoGroup(), 0, 1)
        grid.addWidget(self.createPushButtonGroup(), 1, 1)
        self.setLayout(grid)
        self.show()
       

    def createInputImage(self):
        groupbox = QGroupBox('Input Image from Line')
        label = QLabel('실시간영상')
        box = QHBoxLayout()
        cb = QComboBox(self)
        cb.addItem('Color')
        cb.addItem('Depth')
        cb.activated[str].connect(self.onActivatedCombo)
        box.addWidget(label)
        box.addWidget(cb)
            
        self.image_label.setGeometry(QRect(110, 0, 640, 480))
        self.image_label.setText("")
        self.image_label.setPixmap(QtGui.QPixmap("c.jpg"))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setWordWrap(False)
        self.image_label.setObjectName("image_label")

        vbox = QVBoxLayout()
        vbox.addLayout(box)
        vbox.addWidget(self.image_label)
  
        groupbox.setLayout(vbox)

        return groupbox

    def createResultImage(self):
        groupbox = QGroupBox('Result Image')
        label = QLabel('결과 영상')
    
        self.rst_label.setGeometry(QRect(60, 0, 640, 480))
        self.rst_label.setText("")
        self.rst_label.setPixmap(QtGui.QPixmap("c.jpg"))
        self.rst_label.setAlignment(Qt.AlignCenter)
        self.rst_label.setWordWrap(False)
        self.rst_label.setObjectName("rst_label")

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(self.rst_label)
        groupbox.setLayout(vbox)
        return groupbox

    def createInfoGroup(self):
        gb = QGroupBox('서버 설정')
        gb.setFlat(True)

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

        self.btn = QPushButton('접속')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn.clicked.connect(self.connectClicked)
        box.addWidget(self.btn)
             
        label = QLabel('정보')
        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(150)
        self.sendmsg = QLineEdit()
        self.sendbtn = QPushButton('보내기')
        self.sendbtn.setAutoDefault(True)
        self.sendbtn.clicked.connect(self.sendMsg)
        self.clearbtn = QPushButton('명령 지움')
        self.clearbtn.clicked.connect(self.clearMsg)
        
        cbox = QVBoxLayout()
        cbox.addWidget(label)
        cbox.addWidget(self.infomsg)
        cbox.addWidget(self.sendmsg)
        cbox.addWidget(self.sendbtn)
        cbox.addWidget(self.clearbtn)
        cbox.addStretch(1)
        
        vbox = QVBoxLayout()        
        vbox.addLayout(box)
        vbox.addLayout(cbox)        
        gb.setLayout(vbox)
        return gb    

    def createPushButtonGroup(self):
        groupbox = QGroupBox('기능 버튼')
        groupbox.setCheckable(True)
        groupbox.setChecked(True)

        checkbox1 = QCheckBox('Checkbox1')
        checkbox2 = QCheckBox('Checkbox2')
        checkbox2.setChecked(True)
        tristatebox = QCheckBox('Tri-state Button')
        tristatebox.setTristate(True)

        pushbutton = QPushButton('Normal Button')
        togglebutton = QPushButton('Toggle Button')
        togglebutton.setCheckable(True)
        togglebutton.setChecked(True)
        flatbutton = QPushButton('Flat Button')
        flatbutton.setFlat(True)
        popupbutton = QPushButton('Popup Button')
        menu = QMenu(self)
        menu.addAction('First Item')
        menu.addAction('Second Item')
        menu.addAction('Third Item')
        menu.addAction('Fourth Item')
        popupbutton.setMenu(menu)

        vbox = QVBoxLayout()
        vbox.addWidget(checkbox1)
        vbox.addWidget(checkbox2)
        vbox.addWidget(tristatebox)
        vbox.addWidget(pushbutton)
        vbox.addWidget(togglebutton)
        vbox.addWidget(flatbutton)
        vbox.addWidget(popupbutton)
        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        return groupbox


# 기능관련 #############################
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
                self.infomsg.clear()
                self.btn.setText('접속')

    def connectSignal(self):
        self.c.recv.recv_signal.connect(self.update_image)
        self.c.disconn.disconn_signal.connect(self.updateDisconnect)    

    def updateImageLable(self, q_image):        
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

    def updateDisconnect(self):
        self.btn.setText('접속')

    def onActivatedCombo(self, text):
        self.infomsg.append(text)
        self.c.changeMode()

    def sendMsg(self):
        sendmsg = self.sendmsg.text()
        self.infomsg.append(sendmsg)        
        self.sendmsg.clear()

    def clearMsg(self):
        pass

    def closeEvent(self, e):
        self.c.stop() 
# 슬랏  #############################
    @pyqtSlot(QImage)
    def update_image(self,q_img):
        self.updateImageLable(q_img)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_ImageDialog()
    ui.connectSignal()
    sys.exit(app.exec_())
