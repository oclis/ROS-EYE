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

realsense_check = os.system("lsusb -d8086:0b07")
if(realsense_check==0):     #device 연결 됐을 경우
    device_bool = True
    print("> usb3.0 connect realsense")
else:
    device_bool = False     #device 연결 안 됐을 경우
    print("> NOT connect realsense ! \n> python3 system exit !!!")
    sys.exit()

'''
# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
'''
#ROI setting
x_roi = 100
y_roi = 40
w_roi = 440
h_roi = 400

#aruco
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()

def aruco_detect(src_img):
    gray_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)
    # Detect Aruco markers
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray_img, aruco_dict, parameters=parameters)
    #print("corners:",corners)
    #print("ids:",ids)
    frame_markers = cv2.aruco.drawDetectedMarkers(src_img.copy(), corners, ids)

    '''
    if np.all(ids != None):
        frame_markers = cv2.aruco.drawDetectedMarkers(src_img.copy(), corners, ids)
        x1 = (corners[0][0][0][0], corners[0][0][0][1])
        x2 = (corners[0][0][1][0], corners[0][0][1][1])
        x3 = (corners[0][0][2][0], corners[0][0][2][1])
        x4 = (corners[0][0][3][0], corners[0][0][3][1])

        im_dst = src_img
        im_src = cv2.imread("test.jpeg")
        size = im_dst.shape
        pts_dst = np.array([x1, x2, x3, x4])
        pts_src = np.array(
            [
                [0, 0],
                [size[1] - 1, 0],
                [size[1] - 1, size[0] - 1],
                [0, size[0] - 1]
            ], dtype=float
        )
        h, status = cv2.findHomography(pts_src, pts_dst)
        temp = cv2.warpPerspective(
            im_src, h, (im_dst.shape[1], im_dst.shape[0]))
        cv2.fillConvexPoly(im_dst, pts_dst.astype(int), 0, 16)
        im_dst = im_dst + temp
        cv2.imshow('Display', im_dst)
    else:
        display = src_img
        cv2.imshow('Display', display)
    '''
    cv2.namedWindow('frame_markers', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('frame_markers', frame_markers)

    #return frame_markers

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
    diff_value = cv2.countNonZero(dst_roi)
    #print(dst.shape)
    #print(dst.size)
    #print(dst.dtype)
    cv2.namedWindow('ROI_diff', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('ROI_diff', dst)
    '''
    p0 = cv2.goodFeaturesToTrack(gray_src1, mask=None, **feature_params)
    # Create a mask image for drawing purposes
    mask = np.zeros_like(src1)
    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(gray_src1, gray_src2, p0, None, **lk_params)

    # Select good points
    good_new = p1[st == 1]
    good_old = p0[st == 1]

    # draw the tracks
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        mask = cv2.line(mask, (a, b), (c, d), (255, 0, 0), 2)
        frame = cv2.circle(src2, (a, b), 5, (255, 0, 0), -1)
    img = cv2.add(frame, mask)

    cv2.namedWindow('img', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('img', img)
    p0 = good_new.reshape(-1, 1, 2)
    '''
    #calcOpticalFlowFarneback
    flow = cv2.calcOpticalFlowFarneback(gray_src1, gray_src2, None, 0.5, 3, 13, 3, 5, 1.1, 0)
    #print(flow)
    img = draw_flow(gray_src2, flow)
    cv2.namedWindow('img', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('img', img)
    print(diff_value)
    return diff_value

#calcOpticalFlowFarneback
def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(int)
    fx, fy = flow[y, x].T
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
        #colorized_depth = np.asanyarray(colorizer.coloqrize(depth_frame).get_data())
        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        aruco_detect(color_image)
        diff_value = diff(first_frame, color_image)
        first_frame = color_image

        if diff_value > 20000:
            print("start save image")
            # color_image 이미지 저장
            '''
            filename = f'cimg%i.jpg' % fileCounter
            cv2.imwrite(filename, color_image)
            # depth_image 이미미지 저장
            filename = f'dimg%i.jpg' q% fileCounter
            cv2.imwrite(filename, depth_image)
            # depth_colormap 이미지 저장
            # filename = f'd_c_img%i.jpg' % fileCounter
            # cv2.imwrite(filename, depth_colormap)
            # colorized_depth 이미지 저장
            # filename = f'c_d_img%i.jpg' % fileCounter
            # cv2.imwrite(filename, colorized_depth)
            print('* {filename} saved')
            fileCounter += 1
            '''
        else:
            print("stop")

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
