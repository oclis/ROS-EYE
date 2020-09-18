import pymysql
import sys
import cv2


class MysqlController:
    def __init__(self, host, id, pw, db_name):
        self.conn = pymysql.connect(host=host, user= id, password=pw, db=db_name,charset='utf8')
        self.curs = self.conn.cursor()
        self.bConnect = True
        self.bMode = False        

    def insert_partname(self, pname, ccode, pcode):    

        if self.bConnect :
            try:
                sql = """INSERT INTO partname (name,ccode,pcode) VALUES (%s,%s,%s)"""
                args = (pname,ccode,pcode)
                self.curs.execute(sql,args)
                self.conn.commit()
            finally:
                pass
                #self.conn.close()
        else :
            # send message to parent 
            print('DB is Not connected!!!1')

    def insert_partimage(self, pname, frame):    
        # 이미지 데이터를 업로드 하는 부분이 String으로 바꾸어 주어야 함.
        if self.bConnect :
            try:
                h, w, sz = frame.shape
                print(h)
                sql = """INSERT INTO partimage (pid,image,size) VALUES (%s,%s,%s)"""
                args = (pname,frame,sz)
                self.curs.execute(sql,args)
                self.conn.commit()
            finally:
                #self.conn.close()
                pass
        else : 
            # send message to parent 
            print('DB is Not connected!!!1')
