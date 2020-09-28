'''
DB명 : maviz  
user : mgt
pass : aA!12345

partname table
+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| pid   | int(11)      | NO   | PRI | NULL    | auto_increment |
| name  | varchar(128) | NO   |     | NULL    |                |
| ccode | varchar(12)  | YES  |     | NULL    |                |
| pcode | varchar(12)  | YES  |     | NULL    |                |
| class | tinyint(4)   | YES  |     | NULL    |                |
| grade | tinyint(4)   | YES  |     | NULL    |                |
+-------+--------------+------+-----+---------+----------------+
+-------+------------+------+-----+---------+----------------+
| Field | Type       | Null | Key | Default | Extra          |
+-------+------------+------+-----+---------+----------------+
| idx   | int(11)    | NO   | PRI | NULL    | auto_increment |
| pid   | int(11)    | NO   |     | NULL    |                |
| image | mediumblob | NO   |     | NULL    |                |
| size  | int(11)    | YES  |     | NULL    |                |
| code  | tinyint(4) | YES  |     | NULL    |                |
| grade | tinyint(4) | YES  |     | NULL    |                |
+-------+------------+------+-----+---------+----------------+


'''

import pymysql
import sys
import cv2
import numpy as np
import base64

class MysqlController:
    def __init__(self, host, id, pw, db_name):
        self.conn = pymysql.connect(host=host, user= id, password=pw, db=db_name,charset='utf8')
        self.curs = self.conn.cursor()
        self.bConnect = True
        self.bMode = False

    def check_data(self, pcode):
        if self.bConnect :
            try:
                check_result = True
                sql = """SELECT count(*) FROM partname WHERE pcode = %s"""
                args = (pcode)
                self.curs.execute(sql,args)
                rows = self.curs.fetchall()
                result = rows[0][0]
                if result > 0 :
                    check_result = False
                else :
                    check_result = True
                return check_result
            finally:
                #self.conn.close()
                pass
        else :
            # send message to parent
            print('DB is Not connected!!!1')


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

    def insert_partimage(self, pcode, frame):
        # 이미지 데이터를 업로드 하는 부분이 String으로 바꾸어 주어야 함.

        if self.bConnect :
            try:
                result, e_img = cv2.imencode('.jpg', frame)
                e_img = np.array(e_img)
                e_img_array_data = e_img.tostring()
                e_img_stringData = base64.b64encode(e_img_array_data)
                e_img_stringData = e_img_stringData.decode()
                h, w, sz = frame.shape

                #sql = """SELECT pid FROM partname WHERE name = %s"""
                sql = """SELECT pid FROM partname WHERE pcode = %s"""
                args = (pcode)
                self.curs.execute(sql, args)
                rows = self.curs.fetchall()
                pid = rows[0][0]
                print(pid)
                sql = """INSERT INTO partimage (pid,image,size) VALUES (%s,%s,%s)"""
                args = (pid,e_img_stringData,sz)
                self.curs.execute(sql,args)
                self.conn.commit()
            finally:
                #self.conn.close()
                pass
        else : 
            # send message to parent 
            print('DB is Not connected!!!1')

    def select_partimage(self, pcode):
        # 이미지 데이터를 업로드 하는 부분이 String으로 바꾸어 주어야 함.

        if self.bConnect :
            try:
                #sql = """SELECT image FROM partimage WHERE pid = (SELECT pid FROM partname where name = %s)"""
                #sql = """SELECT image FROM partimage WHERE pid = (SELECT pid FROM partname where pcode = %s)"""
                sql = """SELECT A.image, B.name, B.ccode FROM partimage as A, partname as B WHERE A.pid = B.pid AND A.pid = (SELECT pid FROM partname where pcode = %s)"""
                args = (pcode)
                self.curs.execute(sql,args)
                rows = self.curs.fetchall()
                img = rows[0][0]
                name = rows[0][1]
                color = rows[0][2]
                d_img = base64.decodebytes(img)
                d_img = np.fromstring(d_img,np.uint8)
                decode_img = cv2.imdecode(d_img, 1)

                return decode_img,name,color
            finally:
                #self.conn.close()
                pass
        else :
            # send message to parent
            print('DB is Not connected!!!1')
