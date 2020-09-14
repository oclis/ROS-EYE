#!/usr/bin/python
import pyrealsense2 as rs  # SDK에 엑세스하기에 필요한 파이썬 바인딩 C++을 제공함
import numpy as np
import socket
import time
import copy
import cv2
import sys
import os

device_bool = False
fileCounter = 0

HOST = '192.168.10.100'
PORT = 9999

clipping_distance_in_meters = 5 #meter
move_value = 1500

#ROI setting (340 x 340)
x_roi = 205
y_roi = 110
w_roi = 340
h_roi = 340

#Text setting
FONT_LOCATION = (35,420)
FONT_SIZE = 1
FONT_SCALE = cv2.FONT_HERSHEY_SIMPLEX
FONT_COLOR = (0, 0, 255)

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
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

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
conn, addr = serv_sock.accept()
print('Socket client accepted!')

fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
first_frame = None

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
    _, dst = cv2.threshold(dst, 25, 255, cv2.THRESH_BINARY)
    dst_roi = dst[0: 90 , 150: 640]
    move_check = cv2.countNonZero(dst_roi)
    #print("ROI_move_value :", move_check)
    return move_check

try:
    while device_bool:
        print('Socket now listening!')
        clnt_sock, addr = serv_sock.accept()
        print(str(addr)+' Socket client accepted!')

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

            grey_color = 40

            depth_image_3d = np.dstack(
                (depth_a, depth_a, depth_a))  # depth image is 1 channel, color is 3 channels
            bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d < 0), grey_color, color_a)
            # bg_removed = bg_removed[y_roi: y_roi + h_roi, x_roi: x_roi + w_roi]
            # Render images
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_a, alpha=0.03), cv2.COLORMAP_JET)
            #images = np.hstack((bg_removed, depth_colormap))

            fgmask = fgbg.apply(color_a)
            fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_OPEN,kernel)

            no_bg = cv2.bitwise_or(color_a, color_a, mask=fgmask)
            cv2.rectangle(no_bg, (x_roi, y_roi), (x_roi+w_roi, y_roi+h_roi), (255, 255, 255) )

            move_check = active_check(first_frame, color_a)
            first_frame = color_a

            # 기계 동작 유무
            if move_check > move_value:
                cv2.putText(no_bg,"Active", FONT_LOCATION, FONT_SCALE, FONT_SIZE, FONT_COLOR)
                #print("> machine activing ")
            else :
                cv2.putText(no_bg, "STOP", FONT_LOCATION, FONT_SCALE, FONT_SIZE, FONT_COLOR)
                #print("> machine stop")

            #bg_removed = cv2.cvtColor(bg_removed, cv2.COLOR_BGR2GRAY)
            '''
            for y in range(0,480) :
                for x in range(0,640) :
                    if bg_removed[y, x, 0] < 110 :
                        bg_removed[y, x, 0] = 0
                        bg_removed[y, x, 1] = 0
                        bg_removed[y, x, 2] = 0
            '''
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
                color_array_data = np.array(color_img_encode)
                if color_array_data is None:
                    print('There is no color img data!')
                    break
                color_stringData = color_array_data.tostring()
                clnt_sock.sendall((str(len(color_stringData))).encode().ljust(16) + color_stringData)

                depth_array_data = np.array(depth_img_encode)
                if depth_array_data is None :
                    print('There is no depth img data!')
                    break
                depth_stringData = depth_array_data.tostring()
                clnt_sock.sendall((str(len(depth_stringData))).encode().ljust(16) + depth_stringData)

            except ConnectionResetError as e:
                print('Disconnected by '+str(addr))
                break

finally:
    # Stop streaming
    pipeline.stop()
    serv_sock.close()



