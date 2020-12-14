import sys
import cv2
import numpy as np
import base64
import os
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

from PyQt5.QtCore import pyqtSignal,QObject,Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
import datetime

class Detector:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default='best.pt', help='model.pt path(s)')
        parser.add_argument('--source', type=str, default='./detect', help='source')  # file/folder, 0 for webcam
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
        self.opt = parser.parse_args()
        model, imgsz, out, source, weights, view_img, save_txt, device, half, modelc, dataset, save_img, classify = None, None, None, None, None, None, None, None, None, None, None, None, None

    def detect_set(self):
        self.out, self.source, self.weights, self.view_img, self.save_txt, self.imgsz = \
            self.opt.output, self.opt.source, self.opt.weights, self.opt.view_img, self.opt.save_txt, self.opt.img_size
        # self.webcam = self.source.isnumeric() or self.source.startswith(('rtsp://', 'rtmp://', 'http://')) or self.source.endswith('.txt')

        # Initialize
        set_logging()
        self.device = select_device(self.opt.device)

        if os.path.exists(self.out):
            shutil.rmtree(self.out)  # delete output folder
        os.makedirs(self.out)  # make new output folder

        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        self.model = attempt_load(self.weights, map_location=self.device)  # load FP32 model
        self.imgsz = check_img_size(self.imgsz, s=self.model.stride.max())  # check img_size
        if self.half:
            self.model.half()  # to FP16

        # Second-stage classifier
        self.classify = False
        if self.classify:
            self.modelc = load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(
                torch.load('weights/resnet101.pt', map_location=self.device)['model'])  # load weights
            self.modelc.to(self.device).eval()
        # Set Dataloader
        # vid_path, vid_writer = None, None
        '''
        if self.webcam:
            view_img = True
            cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(self.source, img_size=self.imgsz)
        else:
        '''
        self.save_img = True
        self.dataset = LoadImages(self.source, img_size=self.imgsz)

    def detect_act(self,img, goods_state,iv,f_label,d):
        #self.imgSrc = self.imgCur.copy()
        # self.infomsg_append('결과 영상을 업데이트 했습니다')
        # self.infomsg_append('detect test')
        filename = "detect.png"
        path = "./detect"
        cv2.imwrite(os.path.join(path, filename), img)
        returnData = None
        if goods_state == "Y" :
            returnData = self.detect(iv,f_label,d)
        if returnData != None :
            return returnData

    def detect(self, iv,f_label,d,save_img=False):
        # Get names and colors
        self.iv = iv
        names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        #colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]
        # Run inference
        #t0 = time.time()
        img = torch.zeros((1, 3, self.imgsz, self.imgsz), device=self.device)  # init img
        _ = self.model(img.half() if self.half else img) if self.device.type != 'cpu' else None  # run once
        returnData = None
        for path, img, im0s, vid_cap in self.dataset:
            img = torch.from_numpy(img).to(self.device)
            img = img.half() if self.half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            pred = self.model(img, augment=self.opt.augment)[0]

            # Apply NMS
            pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes,
                                       agnostic=self.opt.agnostic_nms)
            t2 = time_synchronized()

            # Apply Classifier
            if self.classify:
                pred = apply_classifier(pred, self.modelc, img, im0s)
            #print("pred",pred)
            # Process detections
            for i, det in enumerate(pred):  # detections per image
                '''
                if self.webcam:  # batch_size >= 1
                    p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
                else:
                '''
                p, s, im0 = path, '', im0s

                save_path = str(Path(self.out) / Path(p).name)
                txt_path = str(Path(self.out) / Path(p).stem) + ('_%g' % self.dataset.frame if self.dataset.mode == 'video' else '')
                #s += '%gx%g ' % img.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                # detect 했을 경우
                if det is not None and len(det):
                    total = 0.0
                    # Rescale boxes from img_size to im0 size
                    #print("type : " , type(det))
                    #print("det : " , det)
                    goods_type = None
                    percent = None
                    more_than_90 = 0
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += '%g %s, ' % (n, names[int(c)])  # add to string

                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        if self.save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            with open(txt_path + '.txt', 'a') as f:
                                f.write(('%g ' * 5 + '\n') % (cls, *xywh))  # label format
                        #print(cls)
                        if self.save_img or self.view_img:  # Add bbox to image
                            goods_type = names[int(cls)]
                            percent = '%.2f' % (conf)
                            #print(type(percent))
                            percent = float(percent)
                            #print("percent",type(percent))
                            label = '%s %.2f' % (names[int(cls)], conf)
                            print(percent)
                            x_point = (int(xyxy[2])+int(xyxy[0])) /2
                            y_point = (int(xyxy[3])+int(xyxy[1])) /2
                            width = int(xyxy[2])- int(xyxy[0])
                            height = int(xyxy[3])- int(xyxy[1])
                            log_string = img_time + "," + goods_type + "," + str(width) + "," + str(height) + "," + (str(x_point),str(y_point))
                            try:
                                if not os.path.exists("log"):
                                    os.makedirs("log")
                            except OSError:
                                print('Error: Creating directory. log')
                            f = open("./log/" + img_date + '_log.csv', mode='at', encoding='utf-8')
                            f.writelines(log_string + '\n')
                            f.close()
                            print("log_string : ", log_string)
                            #if percent > 0.70:
                            #plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)
                            plot_one_box(xyxy, im0, label=label, color=(0,0,255), line_thickness=3)
                                #total = total + percent
                                #more_than_90 += 1

                    if d.bConnect == True :
                        #avg = total/len(det)
                        if more_than_90 != 0 :
                            avg = total/more_than_90
                            avg = round(avg,2)
                            #print(total)
                            #print(more_than_90)
                            #print(avg)
                            print("names : ", names[int(cls)])
                            #print("확률 : %.2f", percent )
                            cv_img, name, color = d.load_image(goods_type)
                            if cv_img is not None :
                                qt_img = self.convert_cv_qt(cv_img)
                                f_label.setPixmap(qt_img)
                                #self.updateFeatureLable(qt_img)
                                #self.infomsg_append("[DETECT] 품종 : %s, 코드 : %s, 개수 : %d" % (name, goods_type, len(det)))

                                #img_time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
                                img_time = datetime.datetime.now().strftime("%H:%M:%S")
                                img_date = datetime.datetime.now().strftime("%Y_%m_%d")
                                returnData = img_time+","+name+","+goods_type+","+str(more_than_90)
                                #self.infomsg_append(img_time+",%s,%s,%d" % (name, goods_type, more_than_90))
                                #log_string = img_time + "," + name + ","+goods_type+"," + str(len(det)) +","+ avg
                                #log_string = img_time + "," + name + ","+goods_type+"," + str(more_than_90) +","+ str(avg)
                                log_string = img_time + "," + name + "," + goods_type + ","
                                try:
                                    if not os.path.exists("log"):
                                        os.makedirs("log")
                                except OSError:
                                    print('Error: Creating directory. log')
                                f = open("./log/"+img_date+'_log.csv', mode='at', encoding='utf-8')
                                f.writelines(log_string+'\n')
                                f.close()
                                print(log_string)
                                #print("db 이미지 업로드 성공")

                        #detect 없을 시
                        else :
                            print("해당 품목 db에서 조회불가 ")
                            #self.iv.clear()
                            iv.clear()
                            #self.f_label.clear()
                            f_label.clear()
                else :
                    print("detect 없음")
                    #self.infomsg_append("[DETECT] 위 품종은 신규 학습이 필요합니다.")
                    #self.infomsg_append("detect 학습 필요")

                print(s)
                # Print time (inference + NMS)
                print('%sDone. (%.3fs)' % (s, t2 - t1))
                iv.setImage(self.convert_cv_qt(im0))

                # Stream results
                if self.view_img:
                    cv2.imshow(p, im0)
                    if cv2.waitKey(1) == ord('q'):  # q to quit
                        raise StopIteration

                # Save results (image with detections)
                if self.save_img:
                    if self.dataset.mode == 'images':
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
            time.sleep(1)
        return returnData
        '''
        if save_txt or save_img:
            print('Results saved to %s' % Path(out))
            if platform.system() == 'Darwin' and not opt.update:  # MacOS
                os.system('open ' + save_path)
        '''

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