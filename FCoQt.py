import sys
from PyQt5.QtWidgets import QWidget, QShortcut, QDesktopWidget, QApplication, QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QKeySequence, QMovie, QImage, QPixmap
import cv2
    
    
#####################
#   Display config
#####################
class Window(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        
        #WIN CONFIG
        self.setWindowTitle('FInQt')
        self.resize(200,200)
        self.centralize()
        
        #KEY INPUT
        self.videoShortcuts = []
        self.videoShortcuts += [QShortcut(QKeySequence("up"), self)]
        self.videoShortcuts[0].activated.connect(self.showSource1)
        self.videoShortcuts += [QShortcut(QKeySequence("down"), self)]
        self.videoShortcuts[1].activated.connect(self.showSource2)
        self.videoShortcuts += [QShortcut(QKeySequence("right"), self)]
        self.videoShortcuts[2].activated.connect(self.nextFrame)
        self.videoShortcuts += [QShortcut(QKeySequence("left"), self)]
        self.videoShortcuts[3].activated.connect(self.prevFrame)
        self.toggleVideoShortcuts(False)
        #-
        QShortcut(QKeySequence("c"), self).activated.connect(self.centralize)
        QShortcut(QKeySequence("s"), self).activated.connect(self.resizeToSource)
        QShortcut(QKeySequence("a"), self).activated.connect(self.toggleAspectRatio)
        #-
        QShortcut(QKeySequence("q"), self).activated.connect(self.exit)
        
        #ETC
        self.label = QLabel(self)   
        self.keepAspectRatio = True
        self.hasVideo = False
        self.videoCount1 = False
        self.setAcceptDrops(True)
        
        #DISPLAY
        self.show()
    
    
    #KEYBOARD INPUT
    def toggleVideoShortcuts(self, toggle):
        for shortcut in self.videoShortcuts:
            shortcut.setEnabled(toggle)
    

    #FILE INPUT
    def addFiles(self, file1, file2):
        self.video1 = cv2.VideoCapture(file1)
        self.file1 = file1
        self.video2 = cv2.VideoCapture(file2)  
        self.file2 = file2
        
        self.curFrame = 0
        self.lastFrame = int(self.video1.get(cv2.CAP_PROP_FRAME_COUNT))  
        
        self.v1Selected = True
        self.hasVideo = True
        self.nextFrame()
        self.resizeToSource()
        self.centralize()
        self.refreshFrame()
        self.toggleVideoShortcuts(True)
    #-
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            print(event.mimeData().text())
            event.accept()
    #-
    def dropEvent(self, event):
        filenames = event.mimeData().text().split('\n')
        
        #set path for video1
        if(not self.videoCount1):
            self.file1 = filenames[0]
            if(self.file1[:8] == 'file:///'):
                self.file1 = self.file1[8:]
            #get path for video2 if there's multiple files
            if(len(filenames)>1):
                file2 = filenames[1]
            else:
                self.toggleVideoShortcuts(False)
                self.videoCount1 = True
                return
        #get path for video2 if video1 already exists
        else:
            self.videoCount1 = False
            file2 = filenames[0]
            
        if(file2[:8] == 'file:///'):
            file2 = file2[8:]
        self.addFiles(self.file1, file2)


    #CHANGE SOURCE
    def scalePixmap(self, pixmap):
        if(self.keepAspectRatio):
            scaledP = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)    
            self.resize(scaledP.width(), scaledP.height())
            return scaledP
        else:
            return pixmap.scaled(self.width(), self.height())
    #-
    @pyqtSlot()
    def showSource1(self):
        self.label.setPixmap(self.scalePixmap(self.frame1))
        self.label.adjustSize()
        self.v1Selected = True
        self.setWindowTitle('FInQt - A['+str(self.curFrame)+'/'+str(self.lastFrame)+']\t  '+self.file1)
    #-    
    @pyqtSlot()
    def showSource2(self):
        self.label.setPixmap(self.scalePixmap(self.frame2))
        self.label.adjustSize()
        self.v1Selected = False
        self.setWindowTitle('FInQt - B['+str(self.curFrame)+'/'+str(self.lastFrame)+']\t  '+self.file2)


    #CHANGE FRAME        
    def cvFrameToPixmap(self, input):
        frameC = cv2.cvtColor(input, cv2.COLOR_BGR2RGB)
        h,w,c = frameC.shape
        return QPixmap.fromImage(QImage(frameC.data, w, h, w*3, QImage.Format_RGB888))
    #-    
    def refreshFrame(self):
        if(self.v1Selected):
            self.showSource1()
        else:
            self.showSource2()
    #-
    @pyqtSlot()
    def nextFrame(self):
        if(self.curFrame == self.lastFrame):
            return
            
        self.curFrame+=1
        self.frame1 = self.cvFrameToPixmap(self.video1.read()[1])
        self.frame2 = self.cvFrameToPixmap(self.video2.read()[1])
        self.refreshFrame()
    #-        
    @pyqtSlot()
    def prevFrame(self):
        if(self.curFrame <= 0):
            return
            
        self.curFrame-=1
        self.video1.set(cv2.CAP_PROP_POS_FRAMES, self.curFrame)
        self.video2.set(cv2.CAP_PROP_POS_FRAMES, self.curFrame)
        
        self.frame1 = self.cvFrameToPixmap(self.video1.read()[1])
        self.frame2 = self.cvFrameToPixmap(self.video2.read()[1])
        self.refreshFrame()

    
    #SCREEN
    @pyqtSlot()
    def centralize(self):
        centralizedRect = self.frameGeometry()
        centralizedRect.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(centralizedRect.topLeft())
    #-    
    @pyqtSlot()
    def resizeToSource(self):
        self.resize(self.frame1.width(),self.frame1.height())
        self.refreshFrame()
    #-    
    @pyqtSlot()
    def toggleAspectRatio(self):
        self.keepAspectRatio = not self.keepAspectRatio
        if(self.hasVideo):
            self.refreshFrame()
    #-
    def resizeEvent(self, event):
        #refreshes frame on window resize
        if(self.hasVideo):
            self.refreshFrame()


    #EXIT
    def closeEvent(self, event):
        #override default exit to close video files
        self.exit()
    #-
    @pyqtSlot()
    def exit(self):
        try:
            self.video1.release()
            self.video2.release()
        except:
            pass
        app.quit()


##########
#   RUN
##########
if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    if len(sys.argv)>3:
        window.addFiles(sys.argv[1], sys.argv[2])
    sys.exit(app.exec_())
