#!/usr/bin/python
import datetime
import numpy as np
import socket
import time
import copy
import cv2
import sys
import os

#socket에서 수신한 버퍼를 반환하는 함수
def recvall(sock, count):
    # 바이트 문자열
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


HOST = '223.171.46.135'
PORT = 9999

fileCounter = 0

#Create socket and connect to the server
clnt_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket Created')
clnt_sock.connect((HOST, PORT))
print('Socket Connected')


while True:
    #Decode the data and generate an image file
    length = recvall(clnt_sock, 16)

    StringData = recvall(clnt_sock, int(length))
    data = np.fromstring(StringData, dtype='uint8')
    decode_img = cv2.imdecode(data, 1)
    if fileCounter % 2 == 0 :
        cv2.imshow('color_show', decode_img)  # 'show는 윈도우창 제목
    else :
        cv2.imshow('depth_show', decode_img)  # 'show는 윈도우창 제목

    key = cv2.waitKey(200)
    if key == ord('q') :
        print("Quit the process!")
        break
    elif key == ord('s') :
        if fileCounter % 2 == 0 :
            print("Save color image!")
            img_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = img_date+'_color.jpg'	#color 파일생성
            cv2.imwrite(filename, decode_img)
        else:
            print("Save depth image!")
            #filename = f'dimg%i.jpg' % fileCounter
            img_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = img_date + '_depth.jpg'
            cv2.imwrite(filename, decode_img)  #  depth 파일생성
    else:
        pass
    fileCounter += 1
clnt_sock.close()
