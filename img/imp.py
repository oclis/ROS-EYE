#!/usr/bin/python

import pyrealsense2 as rs
import numpy as np
import socket
import time
import copy
import cv2
import sys
import os

print("opencv:", cv2.__version__)

device_bool = False
fileCounter = 0
diffValue = 30000
clipping_distance_in_meters = 0.5  # meter

realsense_check = os.system("lsusb -d8086:0b07")
if(realsense_check==0):     #device 연결 됐을 경우
    device_bool = True
    print("> usb3.0 connect realsense")
else:
    device_bool = False     #device 연결 안 됐을 경우
    print("> NOT connect realsense ! \n> python3 system exit !!!")
    sys.exit()

#ROI setting
x_roi = 100
y_roi = 40
w_roi = 440
h_roi = 400

#BackgroundSubtractorMOG2
fgbg = cv2.createBackgroundSubtractorMOG2(history=30, detectShadows=False)
#fgbg = cv2.createBackgroundSubtractorKNN()

def diff(src1, src2):
    if src1 is None:
        src1 = src2

    #prev_image
    gray_src1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
    gray_src1 = cv2.GaussianBlur(gray_src1, (0, 0), 1.0)

    #current_image
    gray_src2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
    gray_src2 = cv2.GaussianBlur(gray_src2, (0, 0), 1.0)

    #diff
    dst = cv2.absdiff(gray_src1, gray_src2)
    _, dst = cv2.threshold(dst, 25, 255, cv2.THRESH_BINARY)

    # ROI
    dst_roi = dst[y_roi: y_roi + h_roi, x_roi: x_roi + w_roi]
    cv2.rectangle(dst, (x_roi, y_roi), (x_roi+w_roi, y_roi+h_roi), (255, 0, 0) )
    diff_value = cv2.countNonZero(dst_roi)
    #print(dst.shape)
    #print(dst.size)
    #print(dst.dtype)
    cv2.namedWindow('ROI_diff', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('ROI_diff', dst)

    # calcOpticalFlowFarneback
    flow = cv2.calcOpticalFlowFarneback(gray_src1, gray_src2, None, 0.5, 3, 13, 3, 5, 1.1, 0)
    # print(flow)
    img = draw_flow(gray_src2, flow)
    cv2.namedWindow('img', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('img', img)
    #print(diff_value)
    return diff_value


#calcOpticalFlowFarneback
def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(int)
    fx, fy = flow[y, x].T
    #print("fx",fx)
    #print("fy",fy)
    #print("flow",flow)
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 255), lineType=cv2.LINE_AA)

    for (x1, y1), (_x2, _y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 128, 255), -1, lineType=cv2.LINE_AA)

    return vis

print ("> Configure depth and color streams")
# Configure depth and color streams
pipeline = rs.pipeline()    #카메라 구성 및 스트리밍, 비전 모듈 트리거링 미치 스레딩 추상화
config = rs.config()        #파이프 라인 스트림과 장치 선택 및 구성에 대한 필터를 요청

#스트림 유형 및 해상도, 가능한형식, 프레임 속도
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8,15)

# Start streaming
profile = pipeline.start(config)
# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor= profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("> Depth Scale is: " , depth_scale)
# We will be removing the background of objects more than  clipping_distance_in_meters meters away
clipping_distance = clipping_distance_in_meters / depth_scale
# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

first_frame = None


try:
    while device_bool:
        start_t = time.time()
        # Wait for a coherent pair of frames: depth and color
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
        #colorizer = rs.colorizer()
        #colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
        # Convert images to numpy arrays
        #depth_image = np.asanyarray(depth_frame.get_data())
        #color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack(
            (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        # Render images
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        #images = np.hstack((bg_removed, depth_colormap))
        cv2.namedWindow('bg_removed', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('bg_removed', bg_removed)

        fgmask = fgbg.apply(color_image)
        back = fgbg.getBackgroundImage()


        cv2.imshow('back', back)
        cv2.namedWindow('fgmask', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('fgmask', fgmask)

        #diff_value = diff(back,color_image)
        #diff_value = diff(first_frame, color_image)
        first_frame = color_image

        if diff_value > diffValue:
            print("start save image")
            # color_image 이미지 저장
            #filename = f'cimg%i.jpg' % fileCounter
            #cv2.imwrite(filename, color_image)
            # depth_image 이미미지 저장
            #filename = f'dimg%i.jpg' % fileCounter
            #cv2.imwrite(filename, depth_image)
            # depth_colormap 이미지 저장
            # filename = f'd_c_img%i.jpg' % fileCounter
            # cv2.imwrite(filename, depth_colormap)
            # colorized_depth 이미지 저장
            # filename = f'c_d_img%i.jpg' % fileCounter
            # cv2.imwrite(filename, colorized_depth)
            #print('*{filename} saved')
            fileCounter += 1
        #else:
            #print("stop")

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # Stack both images horizontally
        #images = np.hstack((color_image, depth_colormap))
        #images = np.hstack((color_image, colorized_depth))
        # Show images
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('RealSense', images)


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
            #filename = f'd_c_img%i.jpg' % fileCounter
            #cv2.imwrite(filename, depth_colormap)
            #colorized_depth 이미지 저장
            #filename = f'c_d_img%i.jpg' % fileCounter
            #cv2.imwrite(filename, colorized_depth)
            print('* {filename} saved')
            fileCounter += 1
        else:
            pass
finally:
	# Stop streaming
	pipeline.stop()