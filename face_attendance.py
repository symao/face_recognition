import sys
import cv2
import os
import face_recognition
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QPixmap,QImage
from PyQt5.QtCore import Qt, QTimer

def detect_faces(img):
    k=0.5
    small_img = cv2.resize(img, None, fx=k,fy=k)
    face_locations = face_recognition.face_locations(small_img, model="cnn")
    return [[int(i/k) for i in x] for x in face_locations]

def load_faces(loaddir):
    filelist = os.listdir(loaddir)
    fimg_list = [cv2.imread(os.path.join(loaddir, x)) for x in filelist]
    face_list = [face_recognition.face_encodings(x)[0] for x in fimg_list]
    name_list = [os.path.splitext(os.path.basename(x))[0] for x in filelist]
    fimg_list = [cv2.resize(x,(100,100)) for x in fimg_list]
    return fimg_list,face_list,name_list

def face_recog(img, face_list, name_list):
    k=0.5
    small_img = cv2.resize(img, None, fx=0.5,fy=0.5)
    face_locations = face_recognition.face_locations(small_img, model="cnn")
    face_encodings = face_recognition.face_encodings(small_img, face_locations)
    face_names = []
    for en in face_encodings:
        match = face_recognition.compare_faces(face_list, en)
        name = 'Unknown' if True not in match else name_list[match.index(True)]
        face_names.append(name)
    return [[int(i/k) for i in x] for x in face_locations], face_names
 
class FaceAttendanceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # init camera
        self.camcap = cv2.VideoCapture(0)
        if not self.camcap.isOpened():
            reply = QMessageBox.warning(self, "警告", "打开相机失败，请确保已连接USB相机。")
            exit()

        self.facedir = 'register'
        if not os.path.exists(self.facedir):
            os.makedirs(self.facedir)

        self.fh, self.fw=100,100
        self.max_face_cnt = 5
        self.fimg_list,self.face_list,self.name_list = load_faces(self.facedir)
        self.run = True

        self.initUI()
         
    def initUI(self):
        # init menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')
        helpMenu = menubar.addMenu('&帮助')

        registAction = QAction(QIcon('regist.png'),'&注册', self)
        registAction.setShortcut('Ctrl+N')
        registAction.setStatusTip('人脸注册')
        registAction.triggered.connect(self.insert)
        fileMenu.addAction(registAction)

        exitAction = QAction(QIcon('exit.png'), '&退出', self)       
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('退出')
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

        aboutAction = QAction(QIcon(), '&关于', self) 
        aboutAction.triggered.connect(self.show_about)
        helpMenu.addAction(aboutAction)
        
        # # init toolbar
        # self.toolbar = self.addToolBar('退出')
        # self.toolbar.addAction(exitAction) 

        # init status bar
        self.statusBar().showMessage('Ready')
 
        # init image show
        img = self.grab_img()
        self.camwin = QLabel(self)
        self.camwin.setFixedWidth(img.shape[1])  
        self.camwin.setFixedHeight(img.shape[0])
        self.camwin.move(0,40)
        self.show_img(self.camwin, img)

        self.facewin = QLabel(self)
        self.facewin.setFixedWidth(self.fw)  
        self.facewin.setFixedHeight(self.fh*self.max_face_cnt)
        self.facewin.move(img.shape[1],40)

        self.timer = QTimer()
        self.timer.start()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.capture)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('人脸考勤系统')   
        self.show()

    def show_about(self):
        reply = QMessageBox.about(self, "关于", "人脸考勤系统v1.0  by symao<maoshuyuan123@gmail.com>")

    def show_img(self, label, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h,w,c = img.shape
        qimg = QImage(img.data, w, h, c*w, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qimg))

    def capture(self):
        if not self.run:
            return
        img = self.grab_img()
        face_locations, face_names = face_recog(img,self.face_list,self.name_list)

        known_faces = []
        known_names = []
        for loc,name in zip(face_locations,face_names):
            top,right,bottom,left = loc
            if name == 'Unknown':
                cv2.rectangle(img, (left,top), (right,bottom), (0,0,255), 1)
                self.facewin.clear()
            else:
                cv2.rectangle(img, (left,top), (right,bottom), (55,255,155), 1)
                cv2.putText(img, name, (left, top - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 255), 1)
                known_faces.append(self.fimg_list[self.name_list.index(name)])
                known_names.append(name)

        self.show_img(self.camwin, img)
        if known_faces:
            # known_faces += [np.ones_like(known_faces[0])*255]*(self.max_face_cnt-len(known_faces))
            timg = np.vstack(known_faces)
            self.show_img(self.facewin, timg)
            self.statusBar().showMessage('签到成功: '+ ','.join(known_names))
        else:
            self.facewin.clear()
            self.statusBar().showMessage('')

    def grab_img(self):
        ret,img = self.camcap.read()
        if not ret:
            QMessageBox.warning(self, "警告", "读取图像失败。")
            exit()
        return img

    def insert(self):
        reply = QMessageBox.question(self, "人脸采集", "调整人脸后点击确定")
        if reply==QMessageBox.Yes:
            img = self.grab_img()
            face_locations = detect_faces(img)
            if not face_locations:
                QMessageBox.warning(self, "警告", "未发现人脸，请重新调整姿态采集。")
                return
            self.run = False
            top,right,bottom,left = face_locations[0]
            face_img = img[top:bottom,left:right]
            self.show_img(self.facewin, cv2.resize(face_img,(self.fw,self.fh)))

            name, ok = QInputDialog.getText(self, "输入姓名", "请输入姓名:", QLineEdit.Normal, "")
            if name and ok:
                cv2.imwrite(os.path.join(self.facedir,name+'.png'), face_img)
                reply = QMessageBox.about(self, "注册成功", "'%s'注册成功"%name)
            elif ok:
                QMessageBox.warning(self, "警告", "非法姓名输入，请重新注册。")

        self.fimg_list,self.face_list,self.name_list = load_faces(self.facedir)
        self.facewin.clear()
        self.run = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FaceAttendanceGUI()
    sys.exit(app.exec_())