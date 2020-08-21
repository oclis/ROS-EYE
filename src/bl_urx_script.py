import math


def f_to_s(v):
  return'{0:.5f}'.format(float(v))

def list_to_array(vals):
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
    self.add_line('servoj({}, {}, {}, {}, {}, {})'.format(f_to_s(1),list_to_array(angles), *[f_to_s(v) for v in [a, v, t, lookahead_time, gain]]))

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

  # def move_home(self):
  #   null_7s = [0, 0, 0, 0, 0, 0, 0]
  #   self.add_line('({}, {}, {})'.format(f_to_s(8),f_to_s(1),list_to_array(null_7s)))
  #   print("move_home clear")

  def move_home(self):
    # self.add_line('({}, {}, {})'.format(f_to_s(8),f_to_s(1),list_to_array(null_7s)))
    angles = [-(math.pi/2), -(math.pi/2), 0, -(math.pi/2), 0, 0]
    self.add_line('move_home({}, {}, {}, {}, {})'.format(f_to_s(1), list_to_array(angles), 0, 0, 0))

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


