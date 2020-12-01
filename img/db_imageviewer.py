from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel,QGridLayout,QCheckBox,QMenu, QVBoxLayout, QHBoxLayout, \
     QGroupBox, QLineEdit, QPushButton, QTextEdit,QComboBox, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap,QImage,QColor
from PyQt5.QtCore import QDir, Qt,QRect,QSize
#from PyQt5.QtWidgets import QFileDialog
#from PyQt5.QtWidgets import QMessageBox
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
import numpy as np
import MysqlController


HOST = '223.171.46.135'
PORT = 9999
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class Ui_ImageDialog(QWidget):

    action_state, goods_state = None, None
    #groupbox_flag = False
    infomsg_count = 0
    idx = 0

    def __init__(self):
        super().__init__()
        #self.c = img_client.ClientSocket(self)
        #self.d = MysqlController.MysqlController('223.171.42.36','mgt','aA!12345','maviz')

        #self.d = MysqlController.MysqlController('172.17.1.153','mgt','aA!12345','maviz')
        #self.d = MysqlController.MysqlController('172.17.0.161','mgt','aA!12345','maviz')
        #self.d = MysqlController.MysqlController('192.168.0.183','mgt','aA!12345','maviz')
        self.d = MysqlController.MysqlController('localhost','mgt','aA!12345','maviz')
        #self.f = recognizer.featureMatcher()
        #self.iv = QMUtil.ImageViewer()
        self.initUI()

    def __del__(self):
        #self.c.stop()
        pass

    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI')
        self.setWindowTitle('Magenta Robotics Inc')
        self.f_label = QLabel()  #feature image


        self.f_label.setPixmap(QtGui.QPixmap("c_db.jpg"))
        self.f_label.setAlignment(Qt.AlignCenter)
        self.f_label.setWordWrap(False)
        self.f_label.setGeometry(QRect(0, 0, 640, 640))

        vb = QVBoxLayout()
        vb.addLayout(self.createPushButtonGroup())
        vb.addWidget(self.f_label)

        self.f_label.setObjectName("image_label")

        self.setLayout(vb)
        self.show()

    def createPushButtonGroup(self):


        box1 = QHBoxLayout()
        label = QLabel('품종')
        self.pname = QLineEdit()
        box1.addWidget(label)
        box1.addWidget(self.pname)
        label = QLabel('색상')
        self.ccode = QLineEdit('WW')
        box1.addWidget(label)
        box1.addWidget(self.ccode)
        label = QLabel('코드')
        self.pcode = QLineEdit()
        box1.addWidget(label)
        box1.addWidget(self.pcode)


        box2 = QHBoxLayout()

        self.loadbtn = QPushButton('이미지 열기')
        self.loadbtn.setAutoDefault(True)
        self.loadbtn.clicked.connect(self.pushButtonClicked)
        box2.addWidget(self.loadbtn)
        self.savebtn = QPushButton('저장')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.savebtn.clicked.connect(self.saveRecode)
        box2.addWidget(self.savebtn)
        self.selectbtn = QPushButton('조회')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.selectbtn.clicked.connect(self.selectRecode)
        box2.addWidget(self.selectbtn)
        self.modifybtn = QPushButton('수정')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.modifybtn.clicked.connect(self.modifyRecode)
        box2.addWidget(self.modifybtn)



        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(250)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255,255,0))

        box3 = QHBoxLayout()
        '''
        self.dbbtn = QPushButton('접속')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.dbbtn.clicked.connect(self.dbConnect)
        box.addWidget(self.dbbtn)
        '''

        self.prevbtn = QPushButton('이전')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.prevbtn.clicked.connect(self.searchPrev)
        box3.addWidget(self.prevbtn)
        self.nextbtn = QPushButton('다음')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.nextbtn.clicked.connect(self.searchNext)
        box3.addWidget(self.nextbtn)

        '''
        self.f_label.setGeometry(QRect(60, 0, 640, 480))
        #self.f_label.setText("Feature")
        self.f_label.setAlignment(Qt.AlignCenter)
        self.f_label.setWordWrap(False)
        self.f_label.setObjectName("f_label")
        '''

        vbox = QVBoxLayout()
        vbox.addLayout(box1)
        vbox.addLayout(box2)
        vbox.addLayout(box3)

        #vbox.addLayout(cbox)
        #vbox.addWidget(self.f_label)
        vbox.addWidget(self.infomsg)
        return vbox


# 기능관련 #############################

    def connectSignal(self):
        #self.f.report.msg_signal.connect(self.update_msg)
        self.dbConnect()

    def updateDisconnect(self):
        self.btn.setText('접속')
        self.infomsg_append('이미지 서버에 접속이 종료되었습니다')

    def onActivatedCombo(self, text):
        self.infomsg_append(text)
        #self.c.changeMode()
        #self.c.changeMode(text)
        self.infomsg_append('이미지 채널이 변경 되었습니다')

    def sendMsg(self):
        sendmsg = self.sendmsg.text()
        self.infomsg_append(sendmsg)
        self.sendmsg.clear()

    def clearMsg(self):
        self.infomsg.clear()
        self.infomsg_count = 0



    def dbConnect(self):
        #db접속 되어있는 상태
        if self.d.bConnect == False:
            self.d.db_connect()
            #if self.d.db_connect() :
            if self.d.bConnect == True :
                #self.dbbtn.setText('접속 종료')
                self.infomsg_append('DB 서버에 접속 했습니다')

            '''
            else:
                self.d.db_disconnect()
                self.dbbtn.setText('접속')
                self.infomsg_append('DB 서버 접속 종료 했습니다')
            '''
        #db접속 종료
        elif self.d.bConnect == True:
            self.d.db_disconnect()
            self.dbbtn.setText('접속')
            self.infomsg_append('DB 서버 접속 종료 했습니다')
            #self.alarm_box("DB 연결 오류", "DB컴퓨터 확인 해주세요")

    def saveRecode(self):
        pn = self.pname.text()
        cc = self.ccode.text()
        pc = self.pcode.text()
        if len(pn) > 0 and len(cc) > 0 and len(pc) > 0 :
            check_result = self.d.check_data(pc)
            if check_result :
                self.d.insert_partname(pn,cc,pc)
                self.d.insert_partimage(pc,self.imgSrc)
                self.infomsg_append('데이터를 MAVIZ DB에 저장합니다. ')
                self.pname.clear()
            else :
                self.infomsg_append('데이터가 이미 DB에 존재합니다')
            #self.ccode.clear()
            #self.pcode.clear()
        else :
            self.alarm_box("DB 등록 오류", "빈칸을 입력해주세요")

    def modifyRecode(self):
        pc = self.pcode.text()
        if len(pc) > 0 :
            check_result = self.d.check_data(pc)
            if check_result :
                fname = QFileDialog.getOpenFileName(self)
                if fname[0]:
                    img_path = fname[0]
                    fname_list = img_path.split('/')
                    length = len(fname_list)
                    # print(fname_list)
                    img_name = fname_list[length - 2] + "/" + fname_list[length - 1]
                    self.infomsg_append(img_name)
                    self.imgSrc = cv2.imread(img_path)
                    self.infomsg_append("이미지 사이즈 : " + str(self.imgSrc.shape))
                    #self.f_label.setPixmap(self.convert_cv_qt(self.imgSrc))
                    self.d.modify_partimage(pc, self.imgSrc)
                    self.infomsg_append('데이터를 MAVIZ DB에 수정합니다. ')
                    self.pname.clear()
                else:
                    QMessageBox.about(self, 'Warning', '파일을 선택하지 않았습니다.')
        else :
            self.alarm_box("DB 등록 오류", "빈칸을 입력해주세요")

    def selectRecode(self):
        pn = self.pname.text()
        pc = self.pcode.text()
        if len(pc) > 0 :
            self.imgSrc,name,color = self.d.select_partimage(pc)
            self.infomsg_append('데이터를 MAVIZ DB에서 조회 합니다. ')
            self.pname.clear()
            self.ccode.clear()
            #self.pcode.clear()
            self.pname.setText(name)
            self.ccode.setText(color)
            #self.f_label.setPixmap(self.convert_cv_qt(img))
            #self.iv.setImage(self.convert_cv_qt(self.imgSrc))
        else :
            self.alarm_box("조회 오류", "부품코드를 입력해주세요")

    def searchPrev(self):
        self.infomsg_append("이전 품종 이미지")
        #self.imgSrc, name, color = self.d.select_partimage(pc)
        #self.pname.setText(name)
        #self.ccode.setText(color)

    def searchNext(self):
        self.infomsg_append("다음 품종 이미지")
        #self.imgSrc, name, color = self.d.select_partimage(pc)
        #self.pname.setText(name)
        #self.ccode.setText(color)

    def convert_cv_qt(self, frame):
        """Convert from an opencv image to QPixmap"""
        frame = cv2.resize(frame,(0,0),fx=0.7,fy=0.7)
        #frame = cv2.resize(frame,dsize=(800,600))
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        #p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        p = convert_to_Qt_format.scaled(w, h, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def pushButtonClicked(self) :
        fname = QFileDialog.getOpenFileName(self)
        #self.label.setText(fname[0])
        img_path = fname[0]
        fname_list = img_path.split('/')
        length = len(fname_list)
        #print(fname_list)
        img_name = fname_list[length-2] + "/" + fname_list[length-1]
        #self.infomsg_append(img_name)
        self.imgSrc = cv2.imread(img_path)
        self.f_label.setImage(self.convert_cv_qt(self.imgSrc))
        #self.infomsg_append("이미지 사이즈 : " +  str(self.imgSrc.shape))
        #self.iv.setImage(self.convert_cv_qt(self.imgSrc))
        #return fname

    def alarm_box(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.about(self, title, message)

    def infomsg_append(self, str):
        self.infomsg.append(str)
        self.infomsg_count += 1
        print(self.infomsg_count)
        if self.infomsg_count == 10000 :
            self.infomsg_count = 0
            self.clearMsg()
            self.iv.clear()

# 슬랏  #####################################
    @pyqtSlot(np.ndarray)
    def update_image(self,cv_img):
        self.imgCur = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.updateImageLable(qt_img)
        #self.detect_set()
        det_img = self.imgCur.copy()
        #returnData = self.det.detect_act(det_img,self.goods_state,self.iv,self.f_label,self.d)
        #if returnData != None :
            #self.infomsg_append(returnData)
        #self.detect_act()

    @pyqtSlot(str, str)
    def recv_state(self, actionstate, goodstate):
        self.action_state = actionstate
        self.goods_state = goodstate
        #print(actionstate)
        #print(goodstate)


    @pyqtSlot(np.ndarray, int, int)
    def cut_image(self,cv_img, h, w):
        self.imgSrc = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.infomsg_append("이미지 사이즈 : width = " + str(w) + ", height = " + str(h))
        self.updateFeatureLable(qt_img)

    @pyqtSlot(str)
    def update_msg(self,str):
         self.infomsg_append(str)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_ImageDialog()
    ui.connectSignal()
    sys.exit(app.exec_())
