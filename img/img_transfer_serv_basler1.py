#!/usr/bin/python
import numpy as np
import socket
import time
import copy
import cv2
import sys
import os
import datetime
from pypylon import pylon
os.environ["PYLON_CAMEMU"] = "3"
from pypylon import genicam

import threading


HOST = '192.168.10.100'
PORT = 9999

# ROI 전체 사진 짜르기 camera A 1280 x 620
roi_x = 640
roi_y = 0
roi_w = 1280
roi_h = 640

# ROI 기계 작동 유무
move_value = 0
# move_value = 250

# ROI 물체 유무
x_roi_goods = 640
y_roi_goods = 0
w_roi_goods = 640
h_roi_goods = 570
goods_value = 5000

# mog2 setting
mog_history = 400
mog_varTh = 16

# Text setting
FONT_LOCATION = (25, 420)
FONT_SIZE = 3
FONT_SCALE = cv2.FONT_HERSHEY_SIMPLEX
FONT_COLOR = (0, 0, 255)

# FONT_LOCATION_TIME = (255, 20)
FONT_LOCATION_TIME = (25, 440)
FONT_COLOR_TIME = (255, 255, 255)
FONT_SCALE_TIME = cv2.FONT_HERSHEY_PLAIN


print("opencv:", cv2.__version__)  # opencv 버전 출력

#기계 작동유무 확인 함수
def active_check (src1, src2) :
    if src1 is None:
        src1 = src2
    # prev_image
    gray_src1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
    gray_src1 = cv2.GaussianBlur(gray_src1, (0, 0), 1.0)

    # current_image
    gray_src2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
    gray_src2 = cv2.GaussianBlur(gray_src2, (0, 0), 1.0)

    dst = cv2.absdiff(gray_src1, gray_src2)
    _, dst_th = cv2.threshold(dst, 15, 255, cv2.THRESH_BINARY)
    dst_roi = dst_th[0: 40 , 0: 360]
    goods_roi = dst_th
    move_check = cv2.countNonZero(dst_roi)
    if move_check < move_value and move_check > 10:
        print("ROI_move_value :", move_check)
    goods_check = cv2.countNonZero(goods_roi)
    #print("ROI goods_check :", goods_check)
    #print("ROI_move_value :", move_check)
    return dst, move_check,goods_check

#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
kernel3 = np.ones((3,3),np.uint8)
kernel5 = np.ones((5,5),np.uint8)
kernel7 = np.ones((7,7),np.uint8)
kernel11 = np.ones((11,11),np.uint8)

def open_close_dilate(src) :
    dst = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel11)
    #dst = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel11)
    dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel5)
    #dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel5)
    #dst = cv2.dilate(dst, kernel3, iterations=3)
    dst = cv2.dilate(dst, kernel3,iterations=2)
    return dst

# returns a frame that is the average of all the provided frames
def bg_average(average, images,count):
    cv2.accumulate(images, average)
    average = average / count
    average = np.uint8(average)
    return average

def color_histo (src) :
    yCrCb = cv2.cvtColor(src, cv2.COLOR_BGR2YCrCb)
    # y, Cr, Cb로 컬러 영상을 분리 합니다.
    y, Cr, Cb = cv2.split(yCrCb)
    # y값을 히스토그램 평활화를 합니다.
    # equalizedY = cv2.equalizeHist(y)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalizedY = clahe.apply(y)

    # equalizedY, Cr, Cb를 합쳐서 새로운 yCrCb 이미지를 만듭니다.
    yCrCb2 = cv2.merge([equalizedY, Cr, Cb])
    # 마지막으로 yCrCb2를 다시 BGR 형태로 변경합니다.
    yCrCbDst = cv2.cvtColor(yCrCb2, cv2.COLOR_YCrCb2BGR)
    return yCrCbDst

# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

if camera.IsGrabbing():  # realsense 가 0이면 usb3.0 연결됨
    device_bool = True
    print("> usb3.0 connect BASLER")
else:  # 아니면 python3 시스템 exit
    device_bool = False
    print("> NOT connect BASLER camera ! \n> python3 system exit !!!")
    sys.exit()

def accept_client():
    global serv_sock
    # Create socket and wait for client connection
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 소켓 생성
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created!')
    serv_sock.bind((HOST, PORT))  # 소켓 연결 바인드
    print('Socket bind complete!')
    serv_sock.listen(5)
    print('Socket now listening!')

    while True :
        try:
            clnt_sock, addr = serv_sock.accept()
            print(str(addr) + ' Socket client accepted!')
        except KeyboardInterrupt:
            serv_sock.close()
            print("Keyboard interrupt")
        t = threading.Thread(target=handle_client, args=(clnt_sock, addr))
        t.daemon = True
        t.start()


def handle_client(clnt_sock, addr) :
    color_a = None
    color_b = None
    no_bg = None

    active_flag = True

    goods_state = 'Y'  # default Y / 없을 경우 N
    active_state = 'A'  # default A / 멈춘 경우 S

    time = 0
    time_val = 4

    first_frame = None

    while clnt_sock is not None:
        # Wait for a coherent pair of frames: depth and color
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            time += 1
            image = converter.Convert(grabResult)
            img = image.GetArray()
            # color_a = img
            # print(time)
            # print("cameraContextValue : " + str(cameraContextValue))
            if color_a is not None and color_b is not None:
                # 기계 이동 체크
                if time % 2 == 0:
                    dst, move_check, goods_check = active_check(first_frame, color_a)
                    first_frame = color_a
                    if goods_check > goods_value:
                        goods_bool = True
                        goods_state = 'Y'
                        active_flag = True
                        active_state = 'A'
                    else:
                        goods_bool = False
                        goods_state = 'N'
                        if goods_check != 0:
                            print("goods_check : " + str(goods_check))
                        active_flag = False
                        active_state = 'S'

                a_histo = color_histo(color_a)


                active_flag_old = active_flag

                # print(cameraContextValue, img.shape)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # jpg의 별도 파라미터, 0~100 품질 높을수록 좋음 90설정

                color_result, color_img_encode = cv2.imencode('.jpg', color_a, encode_param)  # encode결과 result에 별도로 저장
                if color_result == False:
                    print('could not encode image!')
                    quit()

                try:
                    if time == time_val:
                        state = active_state + "@" + goods_state
                        # state = state.encode()
                        color_array_data = np.array(color_img_encode)
                        if color_array_data is None:
                            print('There is no color img data!')
                            serv_sock.close()
                            break
                        color_state = state + "@CA"
                        color_state = color_state.encode()
                        color_stringData = color_array_data.tostring()
                        # size_c = len(color_stringData)
                        # print("size : " ,size_c)
                        clnt_sock.sendall(
                            color_state + (str(len(color_stringData))).encode().ljust(16) + color_stringData)

        grabResult.Release()

                except ConnectionResetError as e:
                    print('Disconnected by ' + str(addr))
                    break
                    serv_sock.close()


# except genicam.GenericException as e:
# Error handling
# print("An exception occurred.", e.GetDescription())
# exitCode = 1

try:
    #while device_bool:
    if device_bool :
        accept_client()

finally :
    # Stop streaming
    # Releasing the resource
    camera.StopGrabbing()



