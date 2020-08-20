## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################
#!/usr/bin/python
import pyrealsense2 as rs
import numpy as np
import socket
import time
import copy
import cv2

print("opencv:", cv2.__version__)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.bind(('127.0.0.1', 7788))
server_socket.bind(('192.168.0.3', 30002))
server_socket.listen(5)

fps = 15
z_rate = 1.57
imgRate = 2
arcRate = 0.012
min_area = 900 #2**9=512
x_roi = 200
y_roi = 160
w_roi = 320
h_roi = 240
clipping_distance_in_meters = 3 #meter
arr_data=[]
arr_send=[]
aruco_centers = np.zeros((4,2),np.uint16)
dist_img = np.zeros((480,640,3),np.uint8)
#dist_img= np.zeros((240,320,3),np.uint8)
#encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),80]
aruco_bool = False

def nothing(x):
	pass
#def end

#cv2.namedWindow('test')
#cv2.createTrackbar('Z','test',1000, 2000, nothing)
#cv2.setTrackbarPos('Z','test',1500)

cv2.namedWindow('Magenta Robotics')
cv2.createTrackbar('Z','Magenta Robotics', 1000, 2000, nothing)
cv2.setTrackbarPos('Z','Magenta Robotics', 1500)

#cv2.namedWindow('Magenta Robotics')
#cv2.createTrackbar('Z','Magenta Robotics',60,255, nothing)
#cv2.setTrackbarPos('Z','Magenta Robotics',220)

# Constant parameters used in Aruco methods
ARUCO_PARAMETERS = cv2.aruco.DetectorParameters_create()
#ARUCO_DICT = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
ARUCO_DICT = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)

def aruco_detect(src_img):
	#dir(cv2.aruco) ['Board_create', 'CharucoBoard_create', 'DICT_4X4_100', 'DICT_4X4_1000', 'DICT_4X4_250', 'DICT_4X4_50', 'DICT_5X5_100', 'DICT_5X5_1000', 'DICT_5X5_250', 'DICT_5X5_50', 'DICT_6X6_100', 'DICT_6X6_1000', 'DICT_6X6_250', 'DICT_6X6_50', 'DICT_7X7_100', 'DICT_7X7_1000', 'DICT_7X7_250', 'DICT_7X7_50', 'DICT_ARUCO_ORIGINAL', 'DetectorParameters_create', 'Dictionary_create', 'Dictionary_create_from', 'Dictionary_get', 'GridBoard_create', '__doc__', '__loader__', '__name__', '__package__', '__spec__', 'calibrateCameraAruco', 'calibrateCameraArucoExtended', 'calibrateCameraCharuco', 'calibrateCameraCharucoExtended', 'custom_dictionary', 'custom_dictionary_from', 'detectCharucoDiamond', 'detectMarkers', 'drawAxis', 'drawDetectedCornersCharuco', 'drawDetectedDiamonds', 'drawDetectedMarkers', 'drawMarker', 'drawPlanarBoard', 'estimatePoseBoard', 'estimatePoseCharucoBoard', 'estimatePoseSingleMarkers', 'getPredefinedDictionary', 'interpolateCornersCharuco', 'refineDetectedMarkers']

	gray_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)
	# Detect Aruco markers - cv2.detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedImgPoints]]]]) -> corners, ids, rejectedImgPoints
	corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray_img, ARUCO_DICT, parameters=ARUCO_PARAMETERS)
	#print("corners:",corners)
	#print("ids:",ids)
	
	if ids is not None:
		for i, corner in zip(ids, corners):
			#print('{}\n{}'.format(i, corner))
			#print(corner[0])
			#print(corner[0].T)
			cornerT = corner[0].T
			#print(np.average(cornerT))
			#print( (int)np.average(cornerT[0]), (int)np.average(cornerT[1]) )
			nCX = int(np.average(cornerT[0]))
			nCY = int(np.average(cornerT[1]))
			#src_img = cv2.circle(src_img, (nCX, nCY), 5,(255,0,0),2)
		
			if i==0:
				aruco_centers[0] = [nCX, nCY]
			elif i==14:
				aruco_centers[1] = [nCX, nCY]
			elif i==46:
				aruco_centers[2] = [nCX, nCY]
			elif i==47:
				aruco_centers[3] = [nCX, nCY]
			else:
				pass
		#for end
	else:
		print("> None Marker")
	#for end

    #dst_img = cv2.aruco.drawDetectedMarkers(src_img, corners, borderColor=(0, 0, 255))
	dst_img = cv2.aruco.drawDetectedMarkers(src_img, corners, ids, (0, 0, 255))
	
	for i in range(0,4):
		j = (i+1)%4
		#cv2.line(dst_img,(aruco_centers[i,0],aruco_centers[i,1]),(aruco_centers[j,0],aruco_centers[j,1]),(255,0,255*(i//3)),2)
		cv2.line(dst_img,(aruco_centers[i,0],aruco_centers[i,1]),(aruco_centers[j,0],aruco_centers[j,1]),(255,0,0),2)
		avx = int(np.average([aruco_centers[i,0],320]))
		avy = int(np.average([aruco_centers[i,1],240]))

		#cv2.putText(dst_img, "%d,%d" %aruco_centers[i,0] %aruco_centers[i,1], (avx,avy), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
		cv2.putText(dst_img, '{},{}'.format(aruco_centers[i,0],aruco_centers[i,1]), (avx,avy), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
	#for end

	print(aruco_centers)

	global x_roi 
	global y_roi 
	global w_roi 
	global h_roi 

	x_roi = np.min(aruco_centers.T[0])
	y_roi = np.min(aruco_centers.T[1])
	w_roi = np.max(aruco_centers.T[0]) - np.min(aruco_centers.T[0])
	h_roi = np.max(aruco_centers.T[1]) - np.min(aruco_centers.T[1])

	print(x_roi,y_roi,w_roi,h_roi)

	cv2.rectangle(dst_img, (x_roi,y_roi),(x_roi+w_roi,y_roi+h_roi),(0,255,255),1)
	#'rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]]) -> img'

	return dst_img
#def end

def detection_3ch(src_img):
	# src_img #3ch
	# dst_img #3ch
	'''
	imgB,imgG,imgR = cv2.split(src_img)
	imgR = np.zeros((src_img.shape[0],src_img.shape[1],1),dtype=np.uint8)
	#cv2.imshow('RealSense-client G', imgG)
	#cv2.imshow('RealSense-client B', imgB)
	BGZ_img = cv2.merge((imgB,imgG,imgR))
	#mask_img  = cv2.inRange(BGZ_img, lower_obj, upper_obj)
	'''

	#b_get = cv2.getTrackbarPos('B','Magenta Robotics')
	b_get = 255
	g_get = cv2.getTrackbarPos('G','Magenta Robotics')

	lower_obj = np.array([b_get-60, g_get-60,0]) #[B,G,R]
	upper_obj = np.array([b_get, g_get,0]) #[B,G,R]

	mask_img = cv2.inRange(src_img, lower_obj, upper_obj)

	rang_img = cv2.bitwise_and(src_img, src_img, mask=mask_img)
	gray_img = cv2.cvtColor(rang_img, cv2.COLOR_BGR2GRAY)
	blur_img = cv2.GaussianBlur(gray_img, (5,5), 0)
	ret, thresh_img = cv2.threshold(blur_img,63,255, cv2.THRESH_TOZERO)
	thresh_img = cv2.erode(thresh_img, None, iterations=2)
	thresh_img = cv2.dilate(thresh_img, None, iterations=2)
	#cv2.imshow('THRESH_TOZERO', thresh_img)

	_, contours, hierachy = cv2.findContours(thresh_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	#3.2.0'findContours(image, mode, method[, contours[, hierarchy[, offset]]]) -> image, contours, hierarchy'

	cnt_contours = len(contours)
	dst_img = rang_img.copy()
	#print("contours :",cnt_contours)
	if cnt_contours>0:
		#dst_img = cv2.drawContours(rang_img, contours, -1, (0,255,255), 2)
		for i in range(cnt_contours):
			contour_area = cv2.contourArea(contours[i])
			#center, radius = cv2.minEnclosingCircle(contours[i])
			#print(i, contours[i].shape[0], approx.shape[0], contour_area,  center, radius)
	
			if contour_area > min_area:
				dst_img = cv2.drawContours(dst_img, contours, i, (0,255,255), 2)
				epsilon = arcRate*cv2.arcLength(contours[i],True)
				approx = cv2.approxPolyDP(contours[i],epsilon,True)
				#dst_img = cv2.drawContours(dst_img, [approx], -1, (0,0,255), 1)
				#dst_img = cv2.arrowedLine(dst_img, (int(center[0]),int(center[1])), (approx[0,0,0],approx[0,0,1]), (0,0,255), thickness=2,tipLength=0.2)

				cnt_approx = approx.shape[0]
				for j in range(cnt_approx):
					apx = approx[j,0,0]
					apy = approx[j,0,1]
					if j<1:
						arr_data.append([apx,h_roi-apy,blur_img[apy,apx],0])
						arr_data.append([apx,h_roi-apy,blur_img[apy,apx],1])
					elif j==(cnt_approx-1):
						arr_data.append([apx,h_roi-apy,blur_img[apy,apx],1])
						arr_data.append([approx[0,0,0],h_roi-approx[0,0,1],blur_img[apy,apx],1])
					else:
						arr_data.append([apx,h_roi-apy,blur_img[apy,apx],1])

					#cv2.circle(dst_img, (apx,apy), 3, (0,0,255), -1 )
					#cv2.putText(dst_img, "%d" %j, (apx,apy), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
				#for end
				#print(">",i, contour_area, contours[i].shape[0], cnt_approx)
			else:
				#print(">",i, contour_area, contours[i].shape[0])
				pass
			
		#for end

	else:
		pass

	#dst_img = src_img.copy()
	return dst_img
#def end

def detection_1ch(src_img, depth16_img):
	# src_img #1ch
	# dst_img #3ch
	#ret, thresh_img = cv2.threshold(src_img, 16,255, cv2.THRESH_BINARY)
	blur_img = cv2.GaussianBlur(src_img, (3,3), 0)
	ret, thresh_img = cv2.threshold(blur_img, 16,255, cv2.THRESH_BINARY)
 	#'THRESH_BINARY', 'THRESH_BINARY_INV', 'THRESH_MASK', 'THRESH_OTSU', 'THRESH_TOZERO', 'THRESH_TOZERO_INV', 'THRESH_TRIANGLE', 'THRESH_TRUNC'
	thresh1_img = cv2.dilate(thresh_img, (5,5), iterations=2)
	thresh2_img = cv2.erode(thresh1_img, (5,5), iterations=3)

	_, contours, hierachy = cv2.findContours(thresh2_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	cnt_contours = len(contours)
	dst_img= np.dstack((src_img, src_img, src_img))

	if cnt_contours>0:
		for i in range(cnt_contours):
			contour_area = cv2.contourArea(contours[i])
			#print(i, contours[i].shape[0], contour_area)	
			if contour_area > min_area:
				dst_img = cv2.drawContours(dst_img, contours, i, (0,255,255), 2)
				epsilon = arcRate*cv2.arcLength(contours[i],True)
				approx = cv2.approxPolyDP(contours[i],epsilon,True)

				cnt_approx = approx.shape[0]
				for j in range(cnt_approx):
					apx = approx[j,0,0]
					apy = approx[j,0,1]
					#apz = blur_img[apy,apx]
					apz = depth16_img[apy,apx]
					if j<1:
						arr_data.append([apx, h_roi-apy, apz, 0])
						arr_data.append([apx, h_roi-apy, apz, 1])
					elif j==(cnt_approx-1):
						arr_data.append([apx, h_roi-apy, apz, 1])
						arr_data.append([approx[0,0,0], h_roi-approx[0,0,1], apz, 1])
					else:
						arr_data.append([apx, h_roi-apy, apz, 1])

				#for end
			else:
				pass
	
		#for end
	else:
		pass

	return dst_img
#def end


print ("> Configure depth and color streams")
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, fps)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8,fps)

# Start streaming
profile = pipeline.start(config)
# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("> Depth Scale is: " , depth_scale)

# We will be removing the background of objects more than  clipping_distance_in_meters meters away
clipping_distance = clipping_distance_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

print ("> TCPServer Waiting for client on port")
client_socket, address = server_socket.accept()

try:
	while True:
		start_t = time.time()
		# Wait for a coherent pair of frames: depth and color
		frames = pipeline.wait_for_frames()
		depth_frame = frames.get_depth_frame()
		#color_frame = frames.get_color_frame()
		#color_image = np.asanyarray(color_frame.get_data())
		#cv2.imshow('color image', color_image)

		# Align the depth frame to color frame
		aligned_frames = align.process(frames)
		# Get aligned frames
		aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
		color_frame = aligned_frames.get_color_frame()

		# Validate that both frames are valid
		if not aligned_depth_frame or not color_frame:
			continue

		depth_align = np.asanyarray(aligned_depth_frame.get_data())
		color_align = np.asanyarray(color_frame.get_data())

		# Remove background - Set pixels further than clipping_distance to grey
		depth_image_3d= np.dstack((depth_align, depth_align, depth_align)) #depth image is 1 channel, color is 3 channels
		color_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), 0, color_align)

		# Apply colormap on depth image (image must be converted to 8-bit per pixel first)
		#depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_align, alpha=0.03), cv2.COLORMAP_JET)
		depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_align, alpha=0.05), cv2.COLORMAP_JET)

		# Convert images to numpy arrays
		#depth_image = np.asanyarray(depth_frame.get_data()) # (y=480,x=640,np.uint16)
		#depthZ_img = depth_image.copy()
		depthZ_img = depth_align.copy()
		'''
		# uint16 to uint8
		depthA_img = (depthZ_img//256).astype(np.uint8) # A = 16bit//256
		depthB_img = depthZ_img.astype(np.uint8) # A = 16bit % 256
		depthZ_img[depthZ_img>0]=255
		depthC_img = depthZ_img.astype(np.uint8) # C = (data=255, zero=0)
		check_img  = np.hstack((depthA_img, depthB_img,depthC_img))
		cv2.imshow('check_img', check_img)
		'''
		z_get = cv2.getTrackbarPos('Z','Magenta Robotics')
		lower_z = np.array([z_get])
		upper_z = np.array([z_get+255]) 

		maskZ_img = cv2.inRange(depthZ_img, lower_z, upper_z)
		#test8_img = testZ_img.astype(np.uint8)
		testZ_img = cv2.bitwise_and(depthZ_img, depthZ_img, mask=maskZ_img)
		testZ_img[testZ_img < z_get] = z_get

		#test16_img= testZ_img - z_get
		test16_img= ((testZ_img - z_get)/z_rate).astype(np.uint16)
		test8_img = (test16_img%256).astype(np.uint8)
		#cv2.imshow('test', test8_img)
		#test8_3ch_img = np.dstack((test8_img, test8_img, test8_img))
		#align_images = np.hstack((color_removed, depth_colormap, test8_3ch_img))
		#cv2.imshow('test', align_images)

		# Stack both images horizontally
		#images = np.hstack((color_image, depth_colormap))

		# Show images
		#cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
		#cv2.imshow('RealSense', images)

		depth_color = cv2.resize(depth_colormap,dsize=(0,0),fx=0.5,fy=0.5)

		depth_roi = depth_colormap[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
		#detect_img = detection_3ch(depth_roi)

		test8_roi = test8_img[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
		dep16_roi = depth_align[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
		detect_img= detection_1ch(test8_roi,dep16_roi)

		'''
		#-jpg encoding
		result, encode_img = cv2.imencode('.jpg',detect_img,encode_param)
		data = np.array(encode_img)
		stringData = data.tostring()

		#-data send
		stringLen = str(len(stringData)).ljust(16)
		sock.send( stringLen.encode() )
		sock.send( stringData )
		'''
		color_copy= color_align.copy()	
		key = cv2.waitKey(1)
		if key == ord('q'):
			#sock.close() #socket 
			break

		elif key == ord('p'):
			cv2.waitKey(0)

		elif key == ord('a'):
			aruco_img = aruco_detect(color_copy)
			cv2.putText(aruco_img, '({},{})-({},{})'.format(x_roi,y_roi,x_roi+w_roi,y_roi+h_roi), (0,aruco_img.shape[0]), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
			cv2.imshow('aruco_img', aruco_img)
			#aruco_roi = color_copy[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
			#dist_img = cv2.resize(aruco_roi, dsize=(aruco_roi.shape[1]*imgRate, aruco_roi.shape[0]*imgRate))
			aruco_bool = True

		elif key == ord('d'): #detection()
			arr_send = copy.copy(arr_data)
			dist_img = cv2.resize(detect_img, dsize=(detect_img.shape[1]*imgRate,detect_img.shape[0]*imgRate))
			for i in range(0,len(arr_send)):
				#arrx = arr_send[i][0]
				#arry = arr_send[i][1]
				#cv2.circle(dist_img, (arrx,arry), 2, (0,0,255), -1 )

				arrx = arr_send[i][0]*imgRate
				arry = (h_roi-arr_send[i][1])*imgRate
				cv2.circle(dist_img, (arrx,arry), 3, (0,0,255), -1 )
				#cv2.putText(dist_img, "%d" %i, (arrx,arry), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
				
				if arr_send[i][3] <1:
					cv2.putText(dist_img, "%d" %i, (arrx,arry+10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
				else:
					cv2.putText(dist_img, "%d" %i, (arrx,arry), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
				
			#for end

			arr_send.append([0,0,0,0])
			print(len(arr_send),arr_send)
			#cv2.imshow('[s] send', send_img)
			#print(arr_send[0])
			aruco_bool = False

		elif key == ord('s'): #TCP send data
			cnt_send = len(arr_send)
			print(cnt_send,"points -> send data start!")
			for i in range(cnt_send):
				data_arr=','.join(str(e) for e in arr_send[i])
				data='movel('+data_arr+')'
				client_socket.send(data.encode())
				print(">",i, arr_send[i])
				if arr_send[i][3]<1:
					cv2.waitKey(3000)
				else:
					cv2.waitKey(300)
			#for end
			print(cnt_send,"points -> robot send finish!")
			#cv2.waitKey(0)

		else:
			#print("> none key input")
			pass

		arr_data.clear()
		cv2.putText(depth_roi, '{},{},{}-{}'.format(w_roi,h_roi,z_get, int(z_get+255*z_rate)), (0,depth_roi.shape[0]), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
		shom_img  = np.vstack((depth_roi,detect_img))
		#print(shom_img.shape, dist_img.shape)
		#cv2.imshow('Magenta Robotics', shom_img)

		'''
		if shom_img.shape[0] != dist_img.shape[0]:
			dist_img = np.zeros(shom_img.shape,np.uint8)
		else:
			pass
		'''
		if aruco_bool:
			if shom_img.shape[0] == h_roi*imgRate:
				aruco_roi= color_align[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
				dist_img = cv2.resize(aruco_roi, dsize=(aruco_roi.shape[1]*imgRate, aruco_roi.shape[0]*imgRate))
			else:
				dist_img = np.zeros(shom_img.shape,np.uint8)
		else:
			if shom_img.shape[0] == dist_img.shape[0]:
				pass
			else:
				dist_img = np.zeros(shom_img.shape,np.uint8)

		show_img  = np.hstack((shom_img,dist_img))
		cv2.imshow('Magenta Robotics', show_img)
		print(time.time()-start_t,"sec")
	#while end

finally:
	# Stop streaming
	pipeline.stop()
	client_socket.close()
	cv2.destroyAllWindows()
