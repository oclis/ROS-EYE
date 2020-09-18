import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal,QObject

class Signal(QObject):  
    msg_signal = pyqtSignal(str)

class featureMatcher:

    def __init__(self):
        self.bMode = False  
        self.report = Signal() 
        
    def get_corrected_img(self, img1, img2):
        MIN_MATCHES = 20
        self.report.msg_signal.emit('start processing')
        orb = cv2.ORB_create(nfeatures=500)
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        index_params = dict(algorithm=6,
                            table_number=6,
                            key_size=12,
                            multi_probe_level=2)
        search_params = {}
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        # Need to draw only good matches, so create a mask
        matchesMask = [[0,0] for i in range(len(matches))]
        self.report.msg_signal.emit('match =')
        # As per Lowe's ratio test to filter good matches
        # ratio test as per Lowe's paper
        for i,(m,n) in enumerate(matches):
            if m.distance < 0.3*n.distance:
                matchesMask[i]=[1,0]
        draw_params = dict(matchColor = (0,255,0),
                        singlePointColor = (255,0,0),
                        matchesMask = matchesMask,
                        flags = 0)
        img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)        

        self.report.msg_signal.emit('end processing')            
        return img3

'''
ORB feature matcher
        #good_matches = []

        for m, n in matches:
            if m.distance < 0.55 * n.distance:
                good_matches.append(m)


        if len(good_matches) > MIN_MATCHES:
            src_points = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_points = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            m, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)
            cv.rectangle(img3, src_points, dst_points), (255, 0, 0), -1)

            corrected_img = cv2.warpPerspective(img1, m, (img2.shape[1], img2.shape[0]))
            self.report.msg_signal.emit('return corrected image')   
            #return corrected_img
'''