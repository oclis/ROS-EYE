import math
import time
import cv2
import numpy as np
import pyrealsense2 as rs
import bpy

from collections import defaultdict
from realsense_device_manager import DeviceManager
from calibration_kabsch import PoseEstimation
from helper_functions import get_boundary_corners_2D
from measurement_task import calculate_boundingbox_points, calculate_cumulative_pointcloud, visualise_measurements

# 인텔리얼센스 인터페이스 하여 물체를 일단 obj로 등록한다.
class RealSense:
    def __init__(self):
        self.WIN_NAME = 'RealSense'
        self.pitch, self.yaw = math.radians(-10), math.radians(-15)
        self.translation = np.array([0, 0, -1], dtype=np.float32)
        self.distance = 2
        self.paused = False
        self.decimate = 1
        self.scale = True
        self.color = True

        # Define some constants 
        self.resolution_width = 1280 # pixels
        self.resolution_height = 720 # pixels
        self.frame_rate = 15  # fps
        self.dispose_frames_for_stablisation = 25  # frames
        
        self.chessboard_width = 6 # squares
        self.chessboard_height = 9 	# squares
        self.square_size = 0.0253 # meters
        # Allow some frames for the auto-exposure controller to stablise
        self.intrinsics_devices = None
        self.chessboard_params = None
        self.rs_config = rs.config()
        self.rs_config.enable_stream(rs.stream.depth, self.resolution_width, self.resolution_height, rs.format.z16, self.frame_rate)
        self.rs_config.enable_stream(rs.stream.infrared, 1, self.resolution_width, self.resolution_height, rs.format.y8, self.frame_rate)
        self.rs_config.enable_stream(rs.stream.color, self.resolution_width, self.resolution_height, rs.format.bgr8, self.frame_rate)


# Use the device manager class to enable the devices and get the frames
        self.device_manager = DeviceManager(rs.context(), self.rs_config)
        self.device_manager.enable_all_devices()
        print('0')	
        for self.frame in range(self.dispose_frames_for_stablisation):
            self.frames = self.device_manager.poll_frames()
            #print('framm = ',self.frame)				
       # assert( len(self.device_manager._available_devices) > 0 ) 
        print('realsense initialized!!')       

    def calibaration(self):
        self.intrinsics_devices = self.device_manager.get_device_intrinsics(self.frames)
        #print(' Set the chessboard parameters for calibration ')
        self.chessboard_params = [self.chessboard_height, self.chessboard_width, self.square_size] 
		
        # Estimate the pose of the chessboard in the world coordinate using the Kabsch Method
        calibrated_device_count = 0
        while calibrated_device_count < len(self.device_manager._available_devices):
            self.frames = self.device_manager.poll_frames()
            pose_estimator = PoseEstimation(self.frames, self.intrinsics_devices, self.chessboard_params)
            transformation_result_kabsch  = pose_estimator.perform_pose_estimation()
            object_point = pose_estimator.get_chessboard_corners_in3d()
            calibrated_device_count = 0
            for device in self.device_manager._available_devices:
                if not transformation_result_kabsch[device][0]:
                    print("Place the chessboard on the plane where the object needs to be detected..")
                else:
                    calibrated_device_count += 1
        print('calibrated_device_count =',calibrated_device_count)
        # Save the transformation object for all devices in an array to use for measurements
        self.transformation_devices={}
        chessboard_points_cumulative_3d = np.array([-1,-1,-1]).transpose()
        for device in self.device_manager._available_devices:
            self.transformation_devices[device] = transformation_result_kabsch[device][1].inverse()
            points3D = object_point[device][2][:,object_point[device][3]]
            points3D = self.transformation_devices[device].apply_transformation(points3D)
            chessboard_points_cumulative_3d = np.column_stack( (chessboard_points_cumulative_3d,points3D) )

        print(' Extract the bounds between which the objects dimensions are needed')
        # It is necessary for this demo that the object's length and breath is smaller than that of the chessboard
        chessboard_points_cumulative_3d = np.delete(chessboard_points_cumulative_3d, 0, 1)
        self.roi_2D = get_boundary_corners_2D(chessboard_points_cumulative_3d)
        print("Calibration completed... \nPlace the box in the field of view of the devices...")


    def setEmitter(self):
        # print('Enable the emitter of the devices')
        self.device_manager.enable_emitter(True)
        # print('-------Enable the emitter of the devices')
        # Load the JSON settings file in order to enable High Accuracy preset for the realsense
        #self.device_manager.load_settings_json("HighResHighAccuracyPreset.json")

        #print(' Get the extrinsics of the device to be used later')
        extrinsics_devices = self.device_manager.get_depth_to_color_extrinsics(self.frames)

        print(' Get the calibration info as a dictionary to help with display of the measurements onto the color image instead of infra red image')
        self.calibration_info_devices = defaultdict(list)
        for calibration_info in (self.transformation_devices, self.intrinsics_devices, extrinsics_devices):
            for key, value in calibration_info.items():
                self.calibration_info_devices[key].append(value)
        print("CalibrasetEmittertion completed... ")

    def processing(self):
        frames_devices = self.device_manager.poll_frames()
        print('get frames')
        # Calculate the pointcloud using the depth frames from all the devices
        point_cloud = calculate_cumulative_pointcloud(frames_devices, self.calibration_info_devices, self.roi_2D)
        # Get the bounding box for the pointcloud in image coordinates of the color imager
        bounding_box_points_color_image, length, width, height = calculate_boundingbox_points(point_cloud, self.calibration_info_devices )
        print( '길이=' ,length,' 폭=' , width,' 높이' , height )
        # Draw the bounding box points on the color image and visualise the results
        # visualise_measurements(frames_devices, bounding_box_points_color_image, length, width, height)

    def closeSense(self):
        self.device_manager.disable_streams()

#Jun Ha Sohn
 