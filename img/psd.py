from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel,QGridLayout,QCheckBox,QMenu, QVBoxLayout, QHBoxLayout, \
     QGroupBox, QLineEdit, QPushButton, QTextEdit,QComboBox, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap,QImage,QColor
from PyQt5.QtCore import QDir, Qt,QRect,QSize
#from PyQt5.QtWidgets import QFileDialog
#from PyQt5.QtWidgets import QMessageBox
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

#Yolo detect
import argparse
#import platform
import shutil
import time
from pathlib import Path
import torch
import torch.backends.cudnn as cudnn
from numpy import random
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords,
    xyxy2xywh, plot_one_box, strip_optimizer, set_logging)
from utils.torch_utils import select_device, load_classifier, time_synchronized

HOST = '223.171.46.135'
PORT = 9999
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class Ui_ImageDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.c = img_client.ClientSocket(self)
        self.d = MysqlController.MysqlController('223.171.42.36','mgt','aA!12345','maviz')
        #self.d = MysqlController.MysqlController('172.17.1.153','mgt','aA!12345','maviz')

        #self.d = MysqlController.MysqlController('172.17.0.161','mgt','aA!12345','maviz')

        #self.d = MysqlController.MysqlController('192.168.100.100','mgt','aA!12345','maviz')
        #self.d = MysqlController.MysqlController('localhost','mgt','aA!12345','maviz')
        self.f = recognizer.featureMatcher()
        self.iv = QMUtil.ImageViewer()
        self.initUI()


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
        #self.image_label.setGeometry(QRect(110, 0, 640, 480))
        self.image_label.setGeometry(QRect(110, 0, 640, 640))
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

        #self.iv.setGeometry(QRect(0, 0, 640, 480))
        #self.iv.setGeometry(QRect(110, 0, 800, 600))
        #self.rst_label.setGeometry(QRect(110, 0, 640, 640))
        #self.rst_label.setPixmap(QtGui.QPixmap("c.jpg"))
        #self.iv.setGeometry(QRect(110, 0, 640, 640))
        self.iv.setPixmap(QtGui.QPixmap("c.jpg"))
        #self.iv.setGeometry(QRect(110, 0, 640, 640))
        #self.iv.setAlignment(Qt.AlignCenter)
        #self.iv.setWordWrap(False)
        #self.rst_label.setText("result")

        vbox = QVBoxLayout()
        vbox.addWidget(self.iv)
        #vbox.addWidget(self.rst_label)

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
        self.infomsg.setFixedHeight(350)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255,255,0))
        self.infomsg.setFontPointSize(20)

        self.sendmsg = QLineEdit()

        i_box = QHBoxLayout()
        #self.sendbtn = QPushButton('이미지 선택')
        self.sendbtn = QPushButton('품종인식 test')
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
        #popupbutton = QPushButton('품종인식 TEST')
        menu = QMenu(self)
        menu.addAction('Feature Matching',self.fm)
        menu.addAction('Second Item',self.test2)
        menu.addAction('Third Item',self.test3)
        menu.addAction('Fourth Item',self.test4)
        #popupbutton.setMenu(menu)

        self.checkBox1 = QCheckBox("Feature Matching", self)
        self.checkBox1.stateChanged.connect(self.checkBoxState)
        cbox = QVBoxLayout()
        label = QLabel('조회')
        cbox.addWidget(label)
        #cbox.addWidget(popupbutton)
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
        #self.iv.setImage(self.convert_cv_qt(self.imgCur))
        #self.rst_label.setPixmap(self.convert_cv_qt(self.imgCur))
        self.imgSrc =  self.imgCur.copy()
        #self.infomsg.append('결과 영상을 업데이트 했습니다')
        self.infomsg.append('detect test')
        filename = "detect.png"
        path = "./detect"
        cv2.imwrite(os.path.join(path, filename), self.imgSrc)
        self.detect()

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
        self.infomsg.append('영상처리를 시작 합니다. ')
        yCrCb = cv2.cvtColor(self.imgCur, cv2.COLOR_BGR2YCrCb)
        # y, Cr, Cb로 컬러 영상을 분리 합니다.
        y, Cr, Cb = cv2.split(yCrCb)
        # y값을 히스토그램 평활화를 합니다.
        #equalizedY = cv2.equalizeHist(y)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalizedY = clahe.apply(y)

        # equalizedY, Cr, Cb를 합쳐서 새로운 yCrCb 이미지를 만듭니다.
        yCrCb2 = cv2.merge([equalizedY, Cr, Cb])
        # 마지막으로 yCrCb2를 다시 BGR 형태로 변경합니다.
        yCrCbDst = cv2.cvtColor(yCrCb2, cv2.COLOR_YCrCb2BGR)
        self.f_label.setPixmap(self.convert_cv_qt(yCrCbDst))


        '''
        gray_img = cv2.cvtColor(self.imgCur, cv2.COLOR_BGR2GRAY)
        equalized_img = cv2.equalizeHist(gray_img)
        img = cv2.cvtColor(equalized_img,cv2.COLOR_GRAY2BGR)
        self.f_label.setPixmap(self.convert_cv_qt(img))
        '''
        #self.f_label.setPixmap(self.convert_cv_qt(self.imgCur))

    def saveRecode(self):
        pn = self.pname.text()
        cc = self.ccode.text()
        pc = self.pcode.text()
        if len(pn) > 0 and len(cc) > 0 and len(pc) > 0 :
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
        else :
            self.alarm_box("DB 등록 오류", "빈칸을 입력해주세요")

    def selectRecode(self):
        pn = self.pname.text()
        pc = self.pcode.text()
        if len(pc) > 0 :
            self.imgSrc,name,color = self.d.select_partimage(pc)
            self.infomsg.append('데이터를 MAVIZ DB에서 조회 합니다. ')
            self.pname.clear()
            self.ccode.clear()
            #self.pcode.clear()
            self.pname.setText(name)
            self.ccode.setText(color)
            #self.f_label.setPixmap(self.convert_cv_qt(img))
            self.iv.setImage(self.convert_cv_qt(self.imgSrc))
        else :
            self.alarm_box("조회 오류", "부품코드를 입력해주세요")



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
        frame = cv2.resize(frame,(0,0),fx=0.7,fy=0.7)
        #frame = cv2.resize(frame,dsize=(800,600))
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        #p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        p = convert_to_Qt_format.scaled(w, h, Qt.KeepAspectRatio)
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

    def alarm_box(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.about(self, title, message)

    def detect(self,save_img=False):

        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default='best.pt', help='model.pt path(s)')
        parser.add_argument('--source', type=str, default='./detect',help='source')  # file/folder, 0 for webcam
        parser.add_argument('--output', type=str, default='./output', help='output folder')  # output folder
        parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
        parser.add_argument('--conf-thres', type=float, default=0.4, help='object confidence threshold')
        parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
        parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument('--view-img', action='store_true', help='display results')
        parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
        parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
        parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true', help='augmented inference')
        parser.add_argument('--update', action='store_true', help='update all models')
        opt = parser.parse_args()

        print("detect 설정값 : ", opt)

        out, source, weights, view_img, save_txt, imgsz = \
            opt.output, opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size
        webcam = source.isnumeric() or source.startswith(('rtsp://', 'rtmp://', 'http://')) or source.endswith('.txt')

        # Initialize
        set_logging()
        device = select_device(opt.device)

        if os.path.exists(out):
            shutil.rmtree(out)  # delete output folder
        os.makedirs(out)  # make new output folder

        half = device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        model = attempt_load(weights, map_location=device)  # load FP32 model
        imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
        if half:
            model.half()  # to FP16

        # Second-stage classifier
        classify = False
        if classify:
            modelc = load_classifier(name='resnet101', n=2)  # initialize
            modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model'])  # load weights
            modelc.to(device).eval()

        # Set Dataloader
        # vid_path, vid_writer = None, None
        if webcam:
            view_img = True
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz)
        else:
            save_img = True
            dataset = LoadImages(source, img_size=imgsz)

        # Get names and colors
        names = model.module.names if hasattr(model, 'module') else model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]


        # Run inference
        t0 = time.time()
        img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
        _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
        for path, img, im0s, vid_cap in dataset:
            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            pred = model(img, augment=opt.augment)[0]

            # Apply NMS
            pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes,
                                       agnostic=opt.agnostic_nms)
            t2 = time_synchronized()

            # Apply Classifier
            if classify:
                pred = apply_classifier(pred, modelc, img, im0s)

            # Process detections
            for i, det in enumerate(pred):  # detections per image
                if webcam:  # batch_size >= 1
                    p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
                else:
                    p, s, im0 = path, '', im0s

                save_path = str(Path(out) / Path(p).name)
                txt_path = str(Path(out) / Path(p).stem) + ('_%g' % dataset.frame if dataset.mode == 'video' else '')
                #s += '%gx%g ' % img.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    #print("type : " , type(det))
                    #print("det : " , det)
                    goods_type = None
                    percent = None
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += '%g %s, ' % (n, names[int(c)])  # add to string

                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        if save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            with open(txt_path + '.txt', 'a') as f:
                                f.write(('%g ' * 5 + '\n') % (cls, *xywh))  # label format
                        #print(cls)
                        if save_img or view_img:  # Add bbox to image
                            goods_type = names[int(cls)]
                            percent = '%.2f' % (conf)
                            label = '%s %.2f' % (names[int(cls)], conf)
                            print(percent)

                            #plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)
                            plot_one_box(xyxy, im0, label=label, color=(0,0,255), line_thickness=3)

                    print("names : ", names[int(cls)])
                    #print("확률 : %.2f", percent )
                    cv_img, name, color = self.d.load_image(goods_type)
                    if cv_img is not None :
                        qt_img = self.convert_cv_qt(cv_img)
                        self.updateFeatureLable(qt_img)
                        self.infomsg.append("[DETECT] 품종 : %s, 코드 : %s, 개수 : %d" % (name, goods_type, len(det)))
                        img_time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
                        img_date = datetime.datetime.now().strftime("%Y_%m_%d")
                        log_string = img_time + "," + name + ","+goods_type+"," + str(len(det))
                        f = open("./log/"+img_date+'_log.csv', mode='at', encoding='utf-8')
                        f.writelines(log_string+'\n')
                        f.close()
                        print(log_string)

                        print("db 이미지 업로드 성공")
                    else :
                        print("해당 품목 db에서 조회불가 ")
                else :
                    print("detect 없음")
                    self.infomsg.append("[DETECT] 위 품종은 신규 학습이 필요합니다.")

                print(s)
                # Print time (inference + NMS)
                print('%sDone. (%.3fs)' % (s, t2 - t1))
                self.iv.setImage(self.convert_cv_qt(im0))

                # Stream results
                if view_img:
                    cv2.imshow(p, im0)
                    if cv2.waitKey(1) == ord('q'):  # q to quit
                        raise StopIteration

                # Save results (image with detections)
                if save_img:
                    if dataset.mode == 'images':
                        cv2.imwrite(save_path, im0)
                    else:
                        if vid_path != save_path:  # new video
                            vid_path = save_path
                            if isinstance(vid_writer, cv2.VideoWriter):
                                vid_writer.release()  # release previous video writer

                            fourcc = 'mp4v'  # output video codec
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                        vid_writer.write(im0)
        '''
        if save_txt or save_img:
            print('Results saved to %s' % Path(out))
            if platform.system() == 'Darwin' and not opt.update:  # MacOS
                os.system('open ' + save_path)
        '''




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

