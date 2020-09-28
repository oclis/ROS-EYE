from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel,QGridLayout,QCheckBox,QMenu, QVBoxLayout, QHBoxLayout, \
     QGroupBox, QLineEdit, QPushButton, QTextEdit,QComboBox
from PyQt5.QtGui import QPixmap,QImage,QColor
from PyQt5.QtCore import QDir, Qt,QRect,QSize
from PyQt5.QtWidgets import QFileDialog
import socket
import time
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
import numpy as np
import img_client
import MysqlController
import recognizer
import QMUtil
from recognizer import find_almost_similar_image_locations
import os
import datetime

HOST = '223.171.46.135'
PORT = 9999
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
img_date = datetime.datetime.now().strftime("%Y%m%d")
PATH = '../../../img_fursys/' + img_date

class Ui_ImageDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.c = img_client.ClientSocket(self)
        self.d = MysqlController.MysqlController('172.17.0.161','mgt','aA!12345','maviz')
        #self.d = MysqlController.MysqlController('172.17.1.153','mgt','aA!12345','maviz')
        #self.d = MysqlController.MysqlController('localhost','mgt','aA!12345','maviz')
        self.f = recognizer.featureMatcher()
        self.iv = QMUtil.ImageViewer()
        self.initUI()
        #self.create_folder(PATH)

    def __del__(self):
        self.c.stop()

    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI')
        self.setWindowTitle('Magenta Robotics Inc')
        self.image_label = QLabel() # source image
        #self.rst_label = QLabel() # result image
        self.f_label = QLabel()  #feature image

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
        #cb.addItem('Color')
        cb.addItem('ColorA')
        cb.addItem('ColorB')
        cb.addItem('Depth')
        cb.activated[str].connect(self.onActivatedCombo)
        box.addWidget(label)
        box.addWidget(cb)
        self.imgCur =  cv2.imread("c.jpg", cv2.IMREAD_COLOR)
        self.imgSrc =  self.imgCur.copy()
        self.image_label.setGeometry(QRect(110, 0, 640, 480))
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

        self.iv.setGeometry(QRect(0, 0, 640, 480))
        #self.rst_label.setText("result")
        vbox = QVBoxLayout()
        vbox.addWidget(self.iv)
        groupbox.setLayout(vbox)
        groupbox.setFixedSize(QSize(680, 520))
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
        self.infomsg.setFixedHeight(350)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255,255,0))

        self.sendmsg = QLineEdit()

        i_box = QHBoxLayout()
        self.sendbtn = QPushButton('이미지 선택')
        self.sendbtn.setAutoDefault(True)
        self.sendbtn.clicked.connect(self.sendImage2rst)

        self.loadbtn = QPushButton('이미지 열기')
        self.loadbtn.setAutoDefault(True)
        self.loadbtn.clicked.connect(self.pushButtonClicked)
        i_box.addWidget(self.sendbtn)
        i_box.addWidget(self.loadbtn)

        self.imgProc = QPushButton('영상 필터 처리')
        self.imgProc.clicked.connect(self.imgProcess)

        self.clearbtn = QPushButton('정보창 지움')
        self.clearbtn.clicked.connect(self.clearMsg)

        cbox = QVBoxLayout()
        cbox.addWidget(label)
        cbox.addWidget(self.infomsg)
        cbox.addWidget(self.sendmsg)
        #cbox.addWidget(self.sendbtn)
        cbox.addLayout(i_box)
        cbox.addWidget(self.imgProc)
        cbox.addWidget(self.clearbtn)
        cbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(box)
        vbox.addLayout(cbox)
        gb.setLayout(vbox)
        return gb

    def createPushButtonGroup(self):
        groupbox = QGroupBox('MAIVZ DB 접속')
        groupbox.setCheckable(True)
        groupbox.setChecked(False)

        box = QHBoxLayout()
        label = QLabel('품종')
        self.pname = QLineEdit()
        box.addWidget(label)
        box.addWidget(self.pname)
        label = QLabel('색상')
        self.ccode = QLineEdit('WW')
        box.addWidget(label)
        box.addWidget(self.ccode)
        label = QLabel('코드')
        self.pcode = QLineEdit()
        box.addWidget(label)
        box.addWidget(self.pcode)
        self.savebtn = QPushButton('저장')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.savebtn.clicked.connect(self.saveRecode)
        box.addWidget(self.savebtn)
        self.selectbtn = QPushButton('조회')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.selectbtn.clicked.connect(self.selectRecode)
        box.addWidget(self.selectbtn)
        popupbutton = QPushButton('품종인식 TEST')
        menu = QMenu(self)
        menu.addAction('Feature Matching',self.fm)
        menu.addAction('Second Item',self.test2)
        menu.addAction('Third Item',self.test3)
        menu.addAction('Fourth Item',self.test4)
        popupbutton.setMenu(menu)

        self.checkBox1 = QCheckBox("Feature Matching", self)
        self.checkBox1.stateChanged.connect(self.checkBoxState)
        cbox = QVBoxLayout()
        label = QLabel('조회')
        cbox.addWidget(label)
        cbox.addWidget(popupbutton)
        cbox.addWidget(self.checkBox1)
        cbox.addStretch(1)

        self.f_label.setGeometry(QRect(60, 0, 640, 480))
        self.f_label.setText("Feature")
        self.f_label.setAlignment(Qt.AlignCenter)
        self.f_label.setWordWrap(False)
        self.f_label.setObjectName("f_label")

        vbox = QVBoxLayout()
        vbox.addLayout(box)
        vbox.addLayout(cbox)
        vbox.addWidget(self.f_label)
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
        self.iv.crop.cut_signal.connect(self.cut_image)
        self.f.report.msg_signal.connect(self.update_msg)
        self.c.disconn.disconn_signal.connect(self.updateDisconnect)
        self.infomsg.append('이미지 서버에 접속 했습니다')

    def updateImageLable(self, q_img):
        self.image_label.setPixmap(q_img)
        if self.checkBox1.isChecked() == True:
            self.fm()

    def updateFeatureLable(self, q_img):
        self.f_label.setPixmap(q_img)

    def sendImage2rst(self):
        self.iv.setImage(self.convert_cv_qt(self.imgCur))
        #self.rst_label.setPixmap(self.convert_cv_qt(self.imgCur))
        self.imgSrc =  self.imgCur.copy()
        self.infomsg.append('결과 영상을 업데이트 했습니다')

    def updateDisconnect(self):
        self.btn.setText('접속')
        self.infomsg.append('이미지 서버에 접속이 종료되었습니다')

    def onActivatedCombo(self, text):
        self.infomsg.append(text)
        #self.c.changeMode()
        self.c.changeMode(text)
        self.infomsg.append('이미지 채널이 변경 되었습니다')

    def sendMsg(self):
        sendmsg = self.sendmsg.text()
        self.infomsg.append(sendmsg)
        self.sendmsg.clear()

    def clearMsg(self):
        self.infomsg.clear()

    def imgProcess(self):
        self.f_label.setPixmap(self.convert_cv_qt(self.imgCur))
        self.infomsg.append('영상처리를 시작 합니다. ')

    def saveRecode(self):
        pn = self.pname.text()
        cc = self.ccode.text()
        pc = self.pcode.text()
        check_result = self.d.check_data(pc)
        if check_result :
            self.d.insert_partname(pn,cc,pc)
            self.d.insert_partimage(pc,self.imgSrc)
            self.infomsg.append('데이터를 MAVIZ DB에 저장 합니다. ')
            self.pname.clear()
        else :
            self.infomsg.append('데이터가 이미 DB에 존재합니다')
        #self.ccode.clear()
        #self.pcode.clear()

    def selectRecode(self):
        pn = self.pname.text()
        pc = self.pcode.text()
        self.imgSrc,name,color = self.d.select_partimage(pc)
        self.infomsg.append('데이터를 MAVIZ DB에서 조회 합니다. ')
        self.pname.clear()
        self.ccode.clear()
        #self.pcode.clear()
        self.pname.setText(name)
        self.ccode.setText(color)
        #self.f_label.setPixmap(self.convert_cv_qt(img))
        self.iv.setImage(self.convert_cv_qt(self.imgSrc))

    def fm(self): #feature matching
        result = find_almost_similar_image_locations(self.imgSrc,self.imgCur)
        try :
            if result is not None:
                y0 = int(result['rectangle'][0][0])
                y1 = int(result['rectangle'][2][0])
                x0 = int(result['rectangle'][0][1])
                x1 = int(result['rectangle'][2][1])
                cood = f' y0={y0} y1={y1} x0={x0} x1={x1}'
                cv2.rectangle(self.imgCur, (y0,x0), (y1, x1), (255, 0, 255), 1)
        finally:
            pass
        #rst = self.f.get_corrected_img( self.imgSrc, self.imgCur)
        self.iv.setImage(self.convert_cv_qt(self.imgCur))

    def test2(self):
        self.infomsg.append('test 2 ')
    def test3(self):
        self.infomsg.append('test 3 ')
    def test4(self):
        self.infomsg.append('test 4 ')

    def closeEvent(self, e):
        self.c.stop()

    def checkBoxState(self):
        if self.checkBox1.isChecked() == True:
            self.infomsg.append('Feature matcing!! checked')
        else:
            self.infomsg.append('Feature matcing!! end')

    def convert_cv_qt(self, frame):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def extract_ROI(self, frame):
        x_roi = 200
        y_roi = 40
        w_roi = 250
        h_roi = 300
        roi = frame[y_roi:y_roi+h_roi,x_roi:x_roi+w_roi]
        rgb_image = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        roi_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = roi_to_Qt_format.scaled(250, 300, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    '''
    def create_folder(self,directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("폴더 생성 성공")
        except OSError:
            print('Error: Creating directory. ' + directory )
    '''

    def pushButtonClicked(self) :
        fname = QFileDialog.getOpenFileName(self)
        #self.label.setText(fname[0])
        img_path = fname[0]
        fname_list = img_path.split('/')
        length = len(fname_list)
        #print(fname_list)
        img_name = fname_list[length-2] + "/" + fname_list[length-1]
        self.infomsg.append(img_name)
        self.imgSrc = cv2.imread(img_path)
        self.infomsg.append("이미지 사이즈 : " +  str(self.imgSrc.shape))
        self.iv.setImage(self.convert_cv_qt(self.imgSrc))
        #return fname



# 슬랏  #####################################
    @pyqtSlot(np.ndarray)
    def update_image(self,cv_img):
        self.imgCur = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.updateImageLable(qt_img)

    @pyqtSlot(np.ndarray, int, int)
    def cut_image(self,cv_img, h, w):
        self.imgSrc = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.infomsg.append("이미지 사이즈 : width = " + str(w) + ", height = " + str(h))
        self.updateFeatureLable(qt_img)

    @pyqtSlot(str)
    def update_msg(self,str):
         self.infomsg.append(str)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_ImageDialog()
    ui.connectSignal()
    sys.exit(app.exec_())

