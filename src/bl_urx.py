#!/usr/bin/env python3

#Mac IP : 192.168.2.6 #subnetmask: 255.255.255.0
#PC IP : 192.168.2.5 #subnetmask: 255.255.255.0
#PORT : 30002

import os
import math
import json

import bpy
import gc
import logging
import socket
import re
import ipaddress

from bl_op_server import *

# logging.basicConfig(filename='/tmp/binder.log')
# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)

default_configuration = {
  'robot': {
    #'script_port': 30002, # Accepts script strings for execution
    'port': 30002,
    #'host': None, # IP address of the robot
    'host': '192.168.2.6' # IP address of the robot
    #'host': '192.168.2.5', # IP address of the robot
  }
}
############################################################


def f_to_s(v):
  return'{0:.5f}'.format(float(v))

def list_to_array(vals):
  #return '[{}]'.format(','.join([f_to_s(v) for v in vals]))
  return '{}'.format(','.join([f_to_s(v) for v in vals]))

class URScript(object):
  def __init__(self):
    self.text = ''

    # Starts inside of a function
    self.indent_level = 0

  def add_line(self, text):
    #print('add_line')
    tabs = ''.join('\t' for i in range(0, self.indent_level))
    #self.text += '{}{}\n'.format(tabs, text.strip())
    self.text += '{}{}'.format(tabs, text.strip())

  def function(self, name, args=[]):
    print('function')
    #self.add_line('def {}({}):'.format(name, ', '.join(args)))
    self.add_line('{}:'.format(name, ', '.join(args)))
    #self.add_line('{}:'.format(name)
    self.indent_level += 1

  def end(self):
    if self.indent_level == 0:
      raise Exception('No structure to end')

    self.indent_level -= 1
    self.add_line('end')

  def set_tool_digital_out(self, index, state):
    self.add_line('set_tool_digital_out({}, {})'.format(index, state))

  def while_loop(self, condition):
    self.add_line('while {}:'.format(condition))
    self.indent_level += 1

  def servoj(self, angles, t=0.008, lookahead_time=0.1, gain=300):
    if not len(angles) == 6:
      raise Exception('Incorrect number of joint angles (need 6)')

    a = 0
    v = 0
    self.add_line('servoj({}, {}, {}, {}, {}, {})'.format(list_to_array(angles), *[f_to_s(v) for v in [a, v, t, lookahead_time, gain]]))
  '''
  def movej(self, angles, a=1.0, v=0.3, t=0.0, r=0.0):
    if not len(angles) == 6:
      raise Exception('Incorrect number of joint angles (need 6)')
    self.add_line('({},{},{})'.format(list_to_array(angles),f_to_s(t)))
    print('({},{},{})'.format(list_to_array(angles),f_to_s(t)))
    '''
##################
  ## 2020-01-30
  def movej(self, angles, t=0, radius = 0, gripper=0):
    #t=0: default, use accel & velo
    #t>0: ignore accel & velo, make motion in t(sec)
    if not len(angles) == 6:
      raise Exception('Incorrect number of joint angles (need 6)')
    self.add_line('movej({}, {}, {}, {}, {})'.format(f_to_s(1), list_to_array(angles), f_to_s(t), f_to_s(radius), f_to_s(gripper)))

  def speedj(self,angles):
    self.add_line('speedj({}, {})'.format(f_to_s(1), list_to_array(angles)))

  def setVelo(self, a=1.4, v=1.05):
    null_7s = [0,0,0,0,0,0,0]
    self.add_line('setVelo({}, {}, {})'.format(f_to_s(2), f_to_s(a), f_to_s(v), list_to_array(null_7s)))

  def stopj(self, a=2):
    null_7s = [0,0,0,0,0,0,0]
    self.add_line('stopj({}, {}, {})'.format(f_to_s(3), f_to_s(a), list_to_array(null_7s)))

  def emergency(self):
    null_8s = [0,0,0,0,0,0,0,0]
    self.add_line('({}, {})'.format(f_to_s(3), list_to_array(null_8s)))

  def server_Alive(self, a=2):
    null_8s = [0,0,0,0,0,0,0,0]
    self.add_line('({}, {})'.format(f_to_s(1), list_to_array(null_8s)))

  def set_digital_out(self, num=1, out=1):
    null_7s = [0,0,0,0,0,0,0]
    self.add_line('set_digital_out({}, {}, {}, {})'.format(f_to_s(0),f_to_s(num), f_to_s(out), list_to_array(null_7s)))

  def set_digital_out_off(self, num=1, out=0):
    null_7s = [0,0,0,0,0,0,0]
    self.add_line('set_digital_out({}, {}, {}, {})'.format(f_to_s(3),f_to_s(num), f_to_s(out), list_to_array(null_7s)))

  def set_digital_out_on(self, num=1, out=1):
    null_7s = [0,0,0,0,0,0,0]
    self.add_line('set_digital_out({}, {}, {}, {})'.format(f_to_s(4),f_to_s(num), f_to_s(out), list_to_array(null_7s)))

  def set_tool_digital_out(self, num=0, out=0):
    null_6s = [0,0,0,0,0,0]
    self.add_line('set_tool_digital_out({}, {}, {}, {})'.format(f_to_s(5),f_to_s(num), f_to_s(out), list_to_array(null_6s)))

  def set_tool_voltage(self, voltage=24):
    null_7s = [0,0,0,0,0,0,0]
    self.add_line('set_tool_digital_out({}, {}, {})'.format(f_to_s(6),f_to_s(voltage), list_to_array(null_7s)))

  def move_home(self):
    null_7s = [0, 0, 0, 0, 0, 0, 0]
    self.add_line('({}, {}, {})'.format(f_to_s(8),f_to_s(1),list_to_array(null_7s)))
    print("move_home clear")

  def end_signal(self, end_signal = 1):
    null_7s = [0,0,0,0,0,0,0]
    self.add_line('end_signal({}, {}, {})'.format(f_to_s(9),f_to_s(end_signal),list_to_array(null_7s)))
    print("end_signal clear")

  def TeachMode(self):
    null_8s = [0, 0, 0, 0, 0, 0, 0, 0]
    self.add_line('({}, {})'.format(f_to_s(10),list_to_array(null_8s)))
    print("TeachMode")

  def offTeachMode(self):
    null_8s = [0, 0, 0, 0, 0, 0, 0, 0]
    self.add_line('({}, {})'.format(f_to_s(11),list_to_array(null_8s)))
    print("offTeachMode")

  def finish_Work(self):
    null_8s = [0, 0, 0, 0, 0, 0, 0, 0]
    self.add_line('({}, {})'.format(f_to_s(12),list_to_array(null_8s)))
    print("finishWork")

############################################################
# Configuration is stored in a JSON formatted file in a Blender user resource directory
#
def get_configuration_path():
  return os.path.join(bpy.utils.user_resource(resource_type='CONFIG', create=True), 'binder-config.json')

def load_configuration():
  config_path = get_configuration_path()

  if not os.path.isfile(config_path):
    save_configuration(default_configuration)
    return default_configuration

  with open(config_path, 'r') as config_file:
    return json.loads(config_file.read())

def save_configuration(config):
  config_path = get_configuration_path()

  with open(config_path, 'w') as config_file:
    config_file.write(json.dumps(config, indent=2))

class Robot(object):
  def __init__(self, host, port):
    self.host = '192.168.0.2'
    self.port = 30002
    self.sock = None

  def connect(self):   
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('socket open')
    self.sock.settimeout(3)
    self.sock.connect((self.host, self.port))
    print('socket connect')      
    

  def send(self, data):
    #client_socket.sendall(bytes(data, encoding='utf8'))
    pass

  #def recv(self, data):
  def recv(self):
    print('recv')
    #msg = client_socket.recv(1024)
    #print('UR5 Torque : ',msg)

  def movejs(self, angles):
    print("movejs")
    script = URScript()
    script.movej(angles)
    print(script.text)

  def movej(self, angles):
    print("movej")
    script = URScript()
    script.movej(angles)
    self.send(script.text)
    self.recv()

  def move_a(self, angles):
    print("movea")
    script = URScript()
    script.movej(angles)
    self.send(script.text)
    print(script.text)
    self.recv()

def get_local_orientation(pose_bone):
  #local_orientation = pose_bone.matrix.to_euler()
  local_orientation = pose_bone.matrix_channel.to_euler()
  #local_orientation = map(degrees, pose_bone.matrix_channe0l.to_euler())
  #local_orientation.x = bpy.data.objects['Armature'].pose.bones[pose_bone.name].rotation_euler
  #local_orientation = pose_bone.rotation_euler
  #print("matrix ",pose_bone.matrix)
  #print("matrix_channel ",pose_bone.matrix_channel)
  return (local_orientation.x, local_orientation.y, local_orientation.z)

def pose_to_ur_joint_angles(bones):
  joint_names = ['Base', 'Shoulder', 'Elbow', 'Wrist1', 'Wrist2', 'Wrist3']

  # Pick which axis is revolute for each joint
  axis_index = {
    'Base': 2,
    'Shoulder': 1,
    'Elbow': 1,
    'Wrist1': 1,
    'Wrist2': 1,
    'Wrist3': 1
  }
  
  # Match direction and start angle for arm
  # (multiplier, offset)
  axis_correction = {
    'Base': (1, 0.0),
    'Shoulder': (1, -90.0),
    'Elbow': (1, 0.0),
    'Wrist1': (1,-90.0),
    'Wrist2': (1, 0.0),#(-1, 0.0),
    'Wrist3': (1, 0.0)#(1, 0.0)
  }

  #print("IK rotation: ", bpy.data.objects["Armature_control"].rotation_euler)

  joint_angles_by_name = {}
  for bone in bones:
    joint_angles_by_name[bone.name] = get_local_orientation(bone)
    #print(bone.name, get_local_orientation(bone))

  joint_angles = []
  for name in joint_names:
    #bl_angle = joint_angles_by_name[name][axis_index[name]]*180/math.pi 
    bl_angle = 0

    if(name == 'Elbow'): #hykim
      checkname='Shoulder'
      bl_angle = (joint_angles_by_name[name][axis_index[name]] - joint_angles_by_name[checkname][axis_index[name]])*180/math.pi
    elif(name == 'Wrist1'):
      checkname='Elbow'
      bl_angle = (joint_angles_by_name[name][axis_index[name]] - joint_angles_by_name[checkname][axis_index[name]])*180/math.pi
    elif(name == 'Wrist2'):
      checkname='Wrist1'
      bl_angle = (joint_angles_by_name[name][axis_index[name]] - joint_angles_by_name[checkname][axis_index[name]])*180/math.pi
    elif(name == 'Wrist3'):
      checkname='Wrist2'
      bl_angle = (joint_angles_by_name[name][axis_index[name]] - joint_angles_by_name[checkname][axis_index[name]])*180/math.pi    
    else:
      bl_angle = joint_angles_by_name[name][axis_index[name]]*180/math.pi

    direction, offset = axis_correction[name]
    joint_angle = direction * bl_angle + offset

    joint_angles.append(joint_angle)
    #print("check: ", name, joint_angle )
    #print('{} : '.format(name), joint_angle)
    #print(joint_angle)
  return joint_angles

def fix_overrotation(fps, current_angle, last_angle):
  def under_speedlimit(current_speed):
    robot_speed_limit = math.radians(191) # radians / second
    speed_limit = robot_speed_limit * 1.02
    return current_speed < speed_limit

  if last_angle == None:
      # FIXME: ideally the first last_angle would be the starting angle for this joint on the robot
      return current_angle

  log.info('{} {} {}'.format(fps, current_angle, last_angle))

  current_speed = math.fabs(current_angle - last_angle) * fps

  if not under_speedlimit(current_speed):
    log.info('Speed limit violated')

    if last_angle < 0 and current_angle > 0:
      # Crossed from negative to positive
      return -2 * math.pi + current_angle
    elif last_angle > 0 and current_angle < 0:
      return 2 * math.pi + current_angle
    else:
      # We are going too fast and it is not because of over-rotation
      # This is a bad animation
      raise Exception('Over speed limit')

  return current_angle

def is_valid_ip(address):
  try:
    ipaddress.ip_address(address)
    return True
  except ValueError:
    return False

def get_robot_ip(self):
  config = load_configuration()
  return config['robot']['host']

def set_robot_ip(self, ip):
  if not is_valid_ip(ip):
    self.error = 'Invalid IP address'
    return

  config = load_configuration()

  if config['robot']['host'] != ip:
    config['robot']['host'] = ip
    save_configuration(config)

class URxExportAnimationOperator(bpy.types.Operator):
  """Exports animation to UR Script and sends to robot arm"""
  bl_idname = 'urx.export'
  bl_label = 'Export to Universal Robots arm'
  bl_options = { 'REGISTER' }

  loop = bpy.props.BoolProperty(name="Loop Animation", default=False)
  robot_ip_address = bpy.props.StringProperty(name="Robot IP Address", get=get_robot_ip, set=set_robot_ip)

  def invoke(self, context, event):
    # Pop up the window with our operators options before executing
    return context.window_manager.invoke_props_dialog(self, width=500)

  def execute(self, context):
    # Check if an error was set in a getter/setter
    if hasattr(self, 'error'):
      self.report({'ERROR'}, self.error)
      return {'CANCELLED'}

    scene = context.scene
    output_type = 'urscript'

    armature_obj = bpy.data.objects['Armature_ik']
    #bpy.context.scene.objects.active = armature_obj
    #bpy.ops.object.mode_set(mode='POSE')

    start_frame_index = scene.frame_current

    last_joint_angles = [None] * 6
    frame_angles = []
    for frame_index in range(scene.frame_start, scene.frame_end):
      scene.frame_set(frame_index)
      joint_angles = pose_to_ur_joint_angles(armature_obj.pose.bones)



      # Fix overrotation
      for i, current_angle in enumerate(joint_angles):
        if i == 0:
          last_angle = last_joint_angles[i]
          joint_angles[i] = fix_overrotation(scene.render.fps, current_angle, last_angle)

      frame_angles.append(joint_angles)
      last_joint_angles = joint_angles

    log.info('Sending {} angles'.format(len(frame_angles)))

    if output_type == 'json':
      with open('/tmp/export.json', 'w') as export_file:
        export_file.write(json.dumps(frame_angles))
    elif output_type == 'urscript':
      time_for_control = 1.0 / scene.render.fps # Seconds

      script = URScript()
      script.function('blender_move')
      script.movej(frame_angles[0])

      if self.loop:
        script.while_loop('True')

      script.set_tool_digital_out(0, False)

      for frame_index, angles in enumerate(frame_angles):
        if frame_index == 150:
          script.set_tool_digital_out(0, True)

        script.servoj(angles, time_for_control)

      script.set_tool_digital_out(0, False)
      
      if self.loop:
        # End for the while loop
        script.end()

      # End for the move function
      script.end()

    # Set the current frame back to what it was originally
    scene.frame_set(start_frame_index)

    config = load_configuration()
    robot = Robot(config['robot']['host'], config['robot']['script_port'])

    log.info('Setup robot at {}:{}'.format(robot.host, robot.port))

    if output_type == 'urscript':
      # FIXME: put this in a proper log directory
      with open('/tmp/export.urscript', 'w') as script_file:
        script_file.write(script.text)

      try:
        robot.send(script.text)
        log.info('Sent script to robot')
      except socket.timeout:
        self.report({'ERROR'}, 'Failed to connect to robot')
        return {'CANCELLED'}

    return {'FINISHED'}

def get_centroid(points):
  if len(points) == 0:
    return None

  x_total, y_total, z_total = points[0]

  for point in points[1:]:
    x, y, z = point

    x_total += x
    y_total += y
    z_total += z

  l = len(points)

  return (x_total / l, y_total / l, z_total / l)

# Adapted from https://blender.stackexchange.com/a/689
def get_spline_points(spline):
  points = []

  if len(spline.bezier_points) >= 2:
    resolution = spline.resolution_u + 1
    segments = len(spline.bezier_points)

    if not spline.use_cyclic_u:
      segments -= 1

    for i in range(segments):
      inext = (i + 1) % len(spline.bezier_points)

      knot1 = spline.bezier_points[i].co
      handle1 = spline.bezier_points[i].handle_right
      handle2 = spline.bezier_points[inext].handle_left
      knot2 = spline.bezier_points[inext].co

      curve_points = bpy.mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, resolution)
      points.extend(curve_points)

  return points

def points_from_curve(obj_path):
  bpy.data.objects[obj_path.name].select = True
  bpy.ops.object.convert(target='MESH', keep_original=True)
  new_obj = bpy.context.object
  points = list(map(lambda p: (p.co.x, p.co.y, p.co.z), new_obj.data.vertices))
  bpy.context.scene.objects.unlink(new_obj)
  return points

def distance(a, b):
  x0, y0, z0 = a
  x1, y1, z1 = b
  return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2)

def group_contiguous_segments(segments):
  if len(segments) <= 1:
    return segments

  # If a point is less than this far away from another point then it might as well be the same point
  def close_enough(a, b):
    return distance(a, b) < 0.01

  polylines = []
  current_polyline = []

  segments_remaining = segments[:]

  while len(segments_remaining) > 0:
    # While we still have segments to sort

    # Use a temp list to avoid mutating while iterating over the main list
    segments_that_will_remain = []

    # If this is still false after checking all segments then we need to start a new polyline
    extended_this_polyline = False

    for segment in segments_remaining:
      start, end = segment

      if len(current_polyline) == 0:
        # Start the new poly line with whatever we get first
        current_polyline.append(start)
        current_polyline.append(end)
        extended_this_polyline = True
      else:
        first_point = current_polyline[0]
        last_point = current_polyline[-1]

        # If this segment is attached to the current poly line at either end then add it on
        if close_enough(last_point, start):
          current_polyline.append(end)
          extended_this_polyline = True
        elif close_enough(last_point, end):
          current_polyline.append(start)
          extended_this_polyline = True
        elif close_enough(first_point, start):
          current_polyline.insert(0, end)
          extended_this_polyline = True
        elif close_enough(first_point, end):
          current_polyline.insert(0, start)
          extended_this_polyline = True
        else:
          segments_that_will_remain.append(segment)

    if not extended_this_polyline:
      # None of the segments were able to fit so we must need to start a new poly line
      polylines.append(current_polyline)
      current_polyline = []
    else:
      segments_remaining = segments_that_will_remain

  # TODO: Minimize the distance between successive poly lines

  if len(current_polyline) > 0:
    polylines.append(current_polyline)

  return polylines

def toolpath_from_polylines(polylines):
  off_x = 0
  off_y = 0
  off_z = 0.5

  toolpath = []

  for polyline in polylines:
    # Move to above the first line
    first_x, first_y, first_z = polyline[0]
    toolpath.append((first_x + off_x, first_y + off_y, first_z + off_z))

    # Move along this polyline
    toolpath += polyline

    # Rise above the end of the polyline
    last_x, last_y, last_z = toolpath[-1]
    toolpath.append((last_x + off_x, last_y + off_y, last_z + off_z))

  return toolpath

def mesh_segments(mesh_obj):
  segments = []

  for edge in mesh_obj.data.edges:
    start_i = edge.vertices[0]
    end_i = edge.vertices[1]

    x1, y1, z1 = mesh_obj.data.vertices[end_i].co
    x2, y2, z2 = mesh_obj.data.vertices[start_i].co

    segments += [((x1, y1, z1), (x2, y2, z2))]
  
  return segments

def mesh_to_toolpath(mesh_obj):
  segments = mesh_segments(mesh_obj)
  contiguous_sections = group_contiguous_segments(segments)
  return toolpath_from_polylines(contiguous_sections)

class GenerateLightPathOperator(bpy.types.Operator):
  """Object to light path"""
  bl_idname = "binder.object_to_toolpath"
  bl_label = "Object to light path"
  bl_options = {"REGISTER", "UNDO"}

  def execute(self, context):
    # Validate selection
    for obj in bpy.context.selected_objects:
      if not obj.type == 'MESH':
        self.report({'ERROR'}, 'Selection must only include meshes')
        return {'CANCELLED'}

    toolpaths = [mesh_to_toolpath(mesh) for mesh in bpy.context.selected_objects]

    # Build script for light path

    script = URScript()
    script.function('blender_move')

    complete_toolpath = []
    for toolpath in toolpaths:
      x0, y0, z0 = toolpath[0]
      script.movej()

    script.end()

    return {'FINISHED'}


