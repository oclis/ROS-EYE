#!/usr/bin/python

import pyrealsense2 as rs
import numpy as np
import socket
import time
import copy
import cv2
import sys
import os

device_bool = False
fileCounter = 0

print("opencv:", cv2.__version__)
realsense_check = os.system("lsusb -d8086:0b07")
if(realsense_check==0):     #device 연결 됐을 경우
	device_bool = True
	print("> usb3.0 connect realsense")
else:
	device_bool = False     #device 연결 안 됐을 경우
	print("> NOT connect realsense ! \n> python3 system exit !!!")
	sys.exit()

print ("> Configure depth and color streams")
# Configure depth and color streams
pipeline = rs.pipeline()    #카메라 구성 및 스트리밍, 비전 모듈 트리거링 미치 스레딩 추상화
config = rs.config()        #파이프 라인 스트림과 장치 선택 및 구성에 대한 필터를 요청
#스트림 유형 및 해상도, 가능한형식, 프레임 속도
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8,15)

# Start streaming
'''
구성에 따라 파이프라인 스트리밍 시작
파이프 라인 스트리밍 루프는 장치에서 샘플을 캡처 
'''
profile = pipeline.start(config)
# Getting the depth sensor's depth scale (see rs-align example for explanation)
'''
get_device() = 파이프 라인에서 사용하는 장치 검색
카메라 추가 설정을 제어하기 위한 애플리케이션 액세스 제공
파이프 라인이 장치 스트림 구성, 활성화 상태 및 프레임 읽기를 제어
'''
depth_sensor= profile.get_device().first_depth_sensor()
'''
get_depth_scale() = 깊이 이미지의 단위와 미터 간의 매핑 검색
'''
depth_scale = depth_sensor.get_depth_scale()
print("> Depth Scale is: " , depth_scale)

'''
깊이 이미지의 정렬 수행하기위해 align_to 매개 변수를 다른 스트림 유형으로 설정
'''
align_to = rs.stream.color
#align_to = rs.stream.depth
align = rs.align(align_to)

try:
    while device_bool:
        start_t = time.time()
        # Wait for a coherent pair of frames: depth and color
        '''
        wait_for_frames()
        프레임 세트에는 파이프 라인에서 활성화 된 각 스트림의 시간 동기화 프레임이 포함
        스트림의 프레임 레이트가 다른 경우, 프레임 세트는 이전 프레임 세트에 포함될 수 있는 느린 스트림의 매칭 프레임 포함
        '''
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()  #get_depth_frame = 첫번째 깊이 프레임 검색 프레임 없을 시 빈 프레임 인스턴스 반환
        aligned_frames = align.process(frames)  #지정된 프레임에서 정렬프로세스 실행 정렬된 프레임 세트 가져옴
        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()
        if not aligned_depth_frame or not color_frame:
            continue
        #print(start_t)

        # depth test
        '''
        color_scheme의 가능한 값 : 0-Jet 1-Classic 2-WhiteToBlack 3-BlackToWhite 4-Bio
        5-Cold 6-Warm 7-Quantized 8-Pattern
        '''
        colorizer = rs.colorizer()
        colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        #images = np.hstack((color_image, depth_colormap))
        images = np.hstack((color_image, colorized_depth))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)

        key = cv2.waitKey(1)
        if key == ord('q'):
            print("quit process!!!")
            cv2.destroyAllWindows()
            break
        elif key == ord('a'):
            print("start save image")
            #color_image 이미지 저장
            filename = f'cimg%i.jpg' % fileCounter
            cv2.imwrite(filename,color_image)
            #depth_image 이미미지 저장
            filename = f'dimg%i.jpg' % fileCounter
            cv2.imwrite(filename,depth_image)
            #depth_colormap 이미지 저장
            filename = f'd_c_img%i.jpg' % fileCounter
            cv2.imwrite(filename, depth_colormap)
            #colorized_depth 이미지 저장
            filename = f'c_d_img%i.jpg' % fileCounter
            cv2.imwrite(filename, colorized_depth)
            print('* {filename} saved')
            fileCounter += 1
        else:
            pass
finally:
	# Stop streaming
	pipeline.stop()
