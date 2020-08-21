#!/usr/bin/python
class cmd_State():
    def __init__(self):
        self.operate = False
        self.moving = False
        self.enable = False

    def isOperate(self):
        return self.operate

    def isMoving(self):
        return self.moving

    def isEnable(self,_cmd):
        if _cmd == 'd' or 'D':
            if self.isOperate()==False or self.isMoving()==False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

        elif _cmd == 's' or 'S':
            if self.isMoving()==False:
                self.enable = True
                print("s cmd- True" )
            else:
                self.enable = False
                print("s cmd- False" )
            return self.enable

        elif _cmd == 'e' or 'E':
            if self.isOperate() == False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

        elif _cmd == 'v' or 'V':
#            print('0924_v')
            if self.isOperate()== False or self.isMoving()==False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

        elif _cmd == 't' or 'T':
#            print('0924_t')
            if self.isOperate() == False or self.isMoving()==False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

        elif _cmd == 'r' or 'R':
#            print('0924_r')
            if self.isOperate() == False or self.isMoving()==False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

        elif _cmd == 'i' or 'I':
            if self.isOperate() == False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

        elif _cmd == 'h' or 'H':
            if self.isOperate() == False or self.isMoving()==False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

        elif _cmd == 'p' or 'P':
            if self.isOperate() == False:
                self.enable = True
            else:
                self.enable = False
            return self.enable

    def set_operate(self,_bool):
        self.operate = _bool
#        print 'set_Operate', _bool

    def set_moving(self,_bool):
        self.moving = _bool
 #       print 'set_Moving', _bool
