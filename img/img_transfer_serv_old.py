#!/usr/bin/python
import pyrealsense2 as rs  # SDK에 엑세스하기에 필요한 파이썬 바인딩 C++을 제공함
import numpy as np
import socket
import time
import copy
import cv2
import sys
import os
import datetime
from time import sleep

active_flag = True
active_flag_old = None
device_bool = False
goods_bool = True   #제품있는지 체크
move_bool = True    #움직임

goods_state = 'Y'   #default Y / 없을 경우 N
active_state = 'A'  #default A / 멈춘 경우 S

HOST = '192.168.10.100'
PORT = 9999

width = 1280
height = 720
fps = 30

#sleep_time = 2.5
time = 0
time_val = 2
clipping_distance_in_meters = 4.5 #meter

#ROI 전체 사진 짜르기
roi_x = 450
roi_y = 0
roi_w = 720
roi_h = 720

#ROI 기계 작동 유무
move_value = 250

#ROI 물체 유무
x_roi_goods = 400
y_roi_goods = 100
w_roi_goods = 240
h_roi_goods = 240
goods_value = 700

#mog2 setting
mog_history = 225
#mog_varTh = 15

#Text setting
FONT_LOCATION = (25,420)
FONT_SIZE = 1
FONT_SCALE = cv2.FONT_HERSHEY_SIMPLEX
FONT_COLOR = (0, 0, 255)

#FONT_LOCATION_TIME = (255, 20)
FONT_LOCATION_TIME = (25, 440)
FONT_COLOR_TIME = (255, 255, 255)
FONT_SCALE_TIME = cv2.FONT_HERSHEY_PLAIN

print("opencv:", cv2.__version__)  # opencv 버전 출력
realsense_check = os.system("lsusb -d8086:0b07")
if (realsense_check == 0):  # realsense 가 0이면 usb3.0 연결됨
    device_bool = True
    print("> usb3.0 connect realsense")
else:  # 아니면 python3 시스템 exit
    device_bool = False
    print("> NOT connect realsense ! \n> python3 system exit !!!")
    sys.exit()

print("> Configure depth and color streams")
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
# Start streaming
profile = pipeline.start(config)
# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()  # 뎁스 센서의 뎁스 스케일 받는 변수 선언
print("> Depth Scale is: ",depth_scale)  # 뎁스 스케일 출력
clipping_distance = clipping_distance_in_meters / depth_scale
align_to = rs.stream.color
align = rs.align(align_to)

#Create socket and wait for client connection
serv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #소켓 생성
serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket created!')
serv_sock.bind((HOST, PORT))                                                    #소켓 연결 바인드
print('Socket bind complete!')
serv_sock.listen(5)
print('Socket now listening!')

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
    goods_roi = dst_th[y_roi_goods:y_roi_goods+h_roi_goods, x_roi_goods: x_roi_goods+w_roi_goods]
    move_check = cv2.countNonZero(dst_roi)
    if move_check < move_value and move_check > 10:
        print("ROI_move_value :", move_check)
    goods_check = cv2.countNonZero(goods_roi)
    #print("ROI_move_value :", move_check)
    return dst, move_check,goods_check

#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
kernel3 = np.ones((3,3),np.uint8)
kernel5 = np.ones((5,5),np.uint8)
kernel11 = np.ones((11,11),np.uint8)

def open_close_dilate(src) :
    dst = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel11)
    dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel5)
    dst = cv2.dilate(dst, kernel3, iterations=3)
    return dst

# returns a frame that is the average of all the provided frames
def bg_average(average, images,count):
    cv2.accumulate(images, average)
    average = average / count
    average = np.uint8(average)
    return average

try:
    while device_bool:
        first_frame = None
        # 평균 배경
        '''
        a_h = 720
        a_w = 720
        TH= 20
        # acc_gray = np.zeros(shape=(height, width),dtype=np.float32)
        acc_bgr = np.zeros(shape=(a_h, a_w, 3), dtype=np.float32)
        acc_gray = np.zeros(shape=(a_h, a_w), dtype=np.float32)
        t = 0
        '''
        a_h = 720
        a_w = 720
        t = 0
        acc_bgr = np.zeros(shape=(a_h, a_w, 3), dtype=np.float32)

        clnt_sock, addr = serv_sock.accept()
        print(str(addr)+' Socket client accepted!')

        #fgbg = cv2.createBackgroundSubtractorMOG2(history=mog_history, varThreshold=mog_varTh, detectShadows=False)
        fgbg = cv2.createBackgroundSubtractorMOG2(history=mog_history, detectShadows=False)

        while clnt_sock is not None:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()  # 뎁스 프레임 받는 변수 선언
            aligned_frames = align.process(frames)

            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()  # 컬러 프레임 받는 변수 선언
            if not aligned_depth_frame or not color_frame:  # 지정된 변수내용이 없으면 반복문 continue
                continue

            depth_a = np.asanyarray(aligned_depth_frame.get_data())  # np = numpy
            color_a = np.asanyarray(color_frame.get_data())

            color_a = color_a[roi_y:roi_y+roi_h,roi_x:roi_x+roi_w]

            #기계 이동 체크
            dst, move_check,goods_check = active_check(first_frame, color_a)

            fgmask = fgbg.apply(color_a)
            fgmask = open_close_dilate(fgmask)

            time += 1

            # 평균 배경
            t += 1
            bg = bg_average(acc_bgr, color_a, t)
            '''
            #평균 배경
            t += 1

            cv2.accumulate(color_a,acc_bgr)
            avg_bgr = acc_bgr/t
            dst_bgr = cv2.convertScaleAbs(avg_bgr)
            diff_bgr = cv2.absdiff(color_a, dst_bgr)

            db, dg, dr = cv2.split(diff_bgr)
            ret, bb = cv2.threshold(db, TH, 255, cv2.THRESH_BINARY)
            ret, bg = cv2.threshold(dg, TH, 255, cv2.THRESH_BINARY)
            ret, br = cv2.threshold(dr, TH, 255, cv2.THRESH_BINARY)

            bImage = cv2.bitwise_or(bb, bg)
            bImage = cv2.bitwise_or(br, bImage)

            bImage = cv2.erode(bImage, None, 5)
            bImage = cv2.dilate(bImage, None, 5)
            bImage = cv2.erode(bImage, None, 7)
            #bImage = open_close_dilate(bImage)
            #bImage = cv2.morphologyEx(bImage, cv2.MORPH_OPEN, kernel)


            mask = cv2.bitwise_or(fgmask,bImage)
            '''
            mask = fgmask
            #mask = bImage

            no_bg = cv2.bitwise_and(color_a, color_a, mask=mask)
            # 이전프레임에 현재프레임 복사
            first_frame = color_a


            #no_bg = no_bg[0:600,200:1100]
            #cv2.rectangle(no_bg, (x_roi, y_roi), (x_roi + w_roi, y_roi + h_roi), (255, 255, 255))


            # 기계 작동 안할 시 배경 초기화
            if active_flag != active_flag_old :
                #fgbg = cv2.createBackgroundSubtractorMOG2(history=mog_history, varThreshold=mog_varTh, detectShadows=False)
                fgbg = cv2.createBackgroundSubtractorMOG2(history=mog_history, detectShadows=False)

                '''
                acc_bgr = np.zeros(shape=(a_h, a_w, 3), dtype=np.float32)
                acc_gray = np.zeros(shape=(a_h, a_w), dtype=np.float32)
                t = 0
                '''

            if active_flag == False :
                print("machine stop")

            #현재시간표시
            img_date = datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
            # 기계 동작 유무
            if move_check > move_value:
                #cv2.putText(no_bg,"Active", FONT_LOCATION, FONT_SCALE, FONT_SIZE, FONT_COLOR)
                #cv2.putText(no_bg, img_date , FONT_LOCATION_TIME, FONT_SCALE_TIME, FONT_SIZE, FONT_COLOR_TIME)
                active_flag = True
                active_state = 'A'
                #print("> machine activing ")
            else :
                #cv2.putText(no_bg, "STOP", FONT_LOCATION, FONT_SCALE, FONT_SIZE, FONT_COLOR)
                #cv2.putText(no_bg, img_date , FONT_LOCATION_TIME, FONT_SCALE_TIME, FONT_SIZE, FONT_COLOR_TIME)
                active_flag = False
                active_state = 'S'
                #print("> machine stop")

            if goods_check > goods_value:
                goods_bool = True
                goods_state = 'Y'
            else:
                goods_bool = False
                goods_state = 'N'
                if goods_check != 0 :
                    print("goods_check : " + str(goods_check))

            active_flag_old = active_flag

            # Encoding the image and sending data
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # jpg의 별도 파라미터, 0~100 품질 높을수록 좋음 90설정
            color_result, color_img_encode = cv2.imencode('.jpg', color_a, encode_param)  # encode결과 result에 별도로 저장
            if color_result == False:
                print('could not encode image!')
                quit()

            depth_result, depth_img_encode = cv2.imencode('.jpg', no_bg, encode_param)  # encode결과 result에 별도로 저장
            if depth_result == False:
                print('could not encode image!')
                quit()

            try:
                if time == time_val :
                    state = active_state+"@"+goods_state
                    state = state.encode()
                    color_array_data = np.array(color_img_encode)
                    if color_array_data is None:
                        print('There is no color img data!')
                        break
                    color_stringData = color_array_data.tostring()
                    clnt_sock.sendall(state+(str(len(color_stringData))).encode().ljust(16) + color_stringData)
                    #clnt_sock.sendall(state+"@C"+(str(len(color_stringData))).encode().ljust(16) + color_stringData)
                    depth_array_data = np.array(depth_img_encode)
                    if depth_array_data is None :
                        print('There is no depth img data!')
                        break
                    depth_stringData = depth_array_data.tostring()
                    clnt_sock.sendall(state+"@D"(str(len(depth_stringData))).encode().ljust(16) + depth_stringData )

                    time = 0
            except ConnectionResetError as e:
                print('Disconnected by '+str(addr))
                break
            #print("sleep start")
            #sleep(sleep_time)
            #print("sleep end")

finally:
    # Stop streaming
    pipeline.stop()
    serv_sock.close()


