import queue

class Bl_Def_Robot():
    def __init__(self):
        self.robot_Job = queue.Queue()
        self.robot_Job_Add_Time = 0
        self.robot_Id = ''
        self.robot_Err_Code = 0
        self.robot_Can_Job = 0
        self.robot_Job_State = 0
        self.robot_Comm_State = 0
        self.robot_Moving_State = 0
        self.robot_Gripper_State = 0


    # Curr Ur State
    def robot_Set_Curr_Ur_State(self,value):
        #self.robot_State_Print()
        self.robot_Comm_State = value[0]
        self.robot_Moving_State = value[1]
        self.robot_Gripper_State = value[2]

    def robot_State_Print(self):
        print("robot_Comm_State     : [",self.robot_Comm_State,"]")
        print("robot_Moving_State   : [",self.robot_Moving_State,"]")
        print("robot_Gripper_State  : [",self.robot_Gripper_State,"]")