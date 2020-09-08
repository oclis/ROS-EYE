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
align_to = rs.stream.color
align = rs.align(align_to)

#Create socket and wait for client connection
serv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #소켓 생성
serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket created!')
serv_sock.bind((HOST, PORT))							#소켓 연결 바인드
print('Socket bind complete!')
serv_sock.listen(5)
print('Socket now listening!')
conn, addr = serv_sock.accept()
print('Socket client accepted!')

try:
    while device_bool:
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

        #Encoding the image and sending data
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]		#jpg의 별도 파라미터, 0~100 품질 높을수록 좋음 90설정
        color_result, color_img_encode = cv2.imencode('.jpg', color_a, encode_param) #encode결과 result에 별도로 저장
        if color_result == False:
            print('could not encode image!')
            quit()

        depth_result, depth_img_encode = cv2.imencode('.jpg', depth_a, encode_param)  # encode결과 result에 별도로 저장
        if depth_result == False:
            print('could not encode image!')
            quit()

        data = np.array(color_img_encode)
        color_stringData = data.tostring()
        conn.sendall((str(len(color_stringData))).encode().ljust(16) + color_stringData)

        data = np.array(depth_img_encode)
        depth_stringData = data.tostring()
        conn.sendall((str(len(depth_stringData))).encode().ljust(16) + depth_stringData)

finally:
    # Stop streaming
    pipeline.stop()
    serv_sock.close()



