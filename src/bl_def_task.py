import queue
import datetime

class Bl_Def_Task():
    def __init__(self):
        self.job_Number = ''
        self.job_Add_Time = datetime.datetime.now()
        self.job_Pose_List = []
        self.job_Move_Times = []
        self.job_Move_Radius = []
        self.job_Gripper_Motions = []
        self.job_Queue = queue.Queue()
