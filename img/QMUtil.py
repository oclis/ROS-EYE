from PyQt5.QtCore import QDir, Qt,QRect,QSize,pyqtSignal,QObject
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap,QColor
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy,QWidget,QRubberBand,QToolTip)
import cv2      
import numpy as np

class Signal(QObject):  
    cut_signal = pyqtSignal(np.ndarray,int,int)

class ImageViewer(QLabel):
    def __init__(self):
        super(ImageViewer, self).__init__()
        self.crop = Signal() 
        pixmap = QPixmap(600, 480)
        self.setPixmap(pixmap)

        self.first_x, self.first_y = None, None
        self.last_x, self.last_y = None, None
        self.pen_color = QColor('#000000')        
        self.scaleFactor = 0.0
        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setScaledContents(True)
        self.setGeometry(QRect(60, 0, 640, 480))
        self.setText("Feature")        
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setWordWrap(False)

        self.createActions()
        self.show()


    def setImage(self, q_img):        
        self.setPixmap(q_img)
        self.scaleFactor = 1.0
        self.fitToWindowAct.setEnabled(True)
        self.updateActions()

        if not self.fitToWindowAct.isChecked():
            self.adjustSize()

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                QDir.currentPath())
        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return

            self.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.adjustSize()


    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()


    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++",
                enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-",
                enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S",
                enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
                checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)


    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.resize(self.scaleFactor * self.pixmap().size())
        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)


    def mousePressEvent (self, eventQMouseEvent):
        self.originQPoint = self.mapFrom(self, eventQMouseEvent.pos())
        self.first_x = int(eventQMouseEvent.x())
        self.first_y = int(eventQMouseEvent.y())
        self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.currentQRubberBand.setGeometry(QRect(self.originQPoint, QSize()))
        self.currentQRubberBand.show()


    def mouseMoveEvent (self, eventQMouseEvent):
        self.x = int(eventQMouseEvent.x())
        self.y = int(eventQMouseEvent.y())
        text1 = str(self.x)
        text2 = str(self.y)
        p = self.mapToGlobal(eventQMouseEvent.pos())
        #QToolTip.showText(eventQMouseEvent.pos() , "X: "+text1+" "+"Y: "+text2,self)
        QToolTip.showText(p, "X: "+text1+" "+"Y: "+text2,self)
        # print ('mouse QToolTip 1') 전체장에서의 위젯 시작점의 좌표가 오리진 포인트가 되어야 함.
        if self.currentQRubberBand.isVisible():
            self.currentQRubberBand.setGeometry(QRect(self.originQPoint, eventQMouseEvent.pos()).normalized() & self.pixmap().rect())

    def mouseReleaseEvent (self, eventQMouseEvent):
        self.last_x = int(eventQMouseEvent.x())
        self.last_y = int(eventQMouseEvent.y())
        self.currentQRubberBand.hide()
        currentQRect = self.currentQRubberBand.geometry()
        self.currentQRubberBand.deleteLater()
        cropQPixmap = self.pixmap().copy(currentQRect)
        #size = cropQPixmap.size() 
        # 직접변환 해서 저장하는 코드... 나중에 
        #s = cropQPixmap.bits().asstring(size.width() * size.height() * image.depth() // 8)  # format 0xffRRGGBB
        #arr = np.fromstring(s, dtype=np.uint8).reshape((size.height(), size.width(), cropQPixmap.depth() // 8))
        #new_image = Image.fromarray(array)
        cropQPixmap.save('output.png') 
        img = cv2.imread("output.png", cv2.IMREAD_COLOR)
        h, w = self.cut_imgSize()
        self.crop.cut_signal.emit(img, h, w)

    def cut_imgSize (self) :
        h = abs(self.last_y - self.first_y)
        w = abs(self.last_x - self.first_x)
        return h,w