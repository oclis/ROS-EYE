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
if(realsense_check==0):
	device_bool = True
	print("> usb3.0 connect realsense")
else:
	device_bool = False
	print("> NOT connect realsense ! \n> python3 system exit !!!")
	sys.exit()

print ("> Configure depth and color streams")
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
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

try:
    while device_bool:
        start_t = time.time()
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        aligned_frames = align.process(frames)
        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()
        if not aligned_depth_frame or not color_frame:
            continue
        print(start_t)
        key = cv2.waitKey(1)
        if key == ord('q'):
            print("quit process!!!")
            break
        elif key == ord('a'):
            print("start save image")
            filename = f'cimg%i.jpg' % fileCounter
            cv2.imwrite(filename,color_frame)
            filename = f'dimg%i.jpg' % fileCounter
            cv2.imwrite(filename,depth_frame)
            print('* {filename} saved')
            fileCounter += 1
        else:
            pass
finally:
	# Stop streaming
	pipeline.stop()
