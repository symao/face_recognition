import sys
import cv2
import os
import time
import face_recognition
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QPixmap,QImage,QPalette,QFont
from PyQt5.QtCore import Qt, QTimer

############# face algorithm api #####################
FACE_WIDTH,FACE_HEIGHT = 100,100
# detect faces with small image for acceleration
def detect_faces(img):
    k=0.5
    small_img = cv2.resize(img, None, fx=k,fy=k)
    face_locations = face_recognition.face_locations(small_img, model="cnn")
    return [[int(i/k) for i in x] for x in face_locations]

# load faces in face dir and encoding
def load_faces(loaddir):
    filelist = os.listdir(loaddir)
    fimg_list, face_list, name_list = [],[],[]
    for f in filelist:
        name,ext = os.path.splitext(f)
        if ext not in ['.jpg','.png','.jpeg','.bmp','.pgm']:
            continue
        img = cv2.imread(os.path.join(loaddir, f))
        encodes = face_recognition.face_encodings(img)
        if encodes:
            fimg_list.append(cv2.resize(img,(FACE_WIDTH,FACE_HEIGHT)))
            face_list.append(encodes[0])
            name_list.append(name)
        else:
            print('Warning: No face in %s',f)
    return fimg_list,face_list,name_list

# recognize faces
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

#######################################################


def get_cur_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

##################### qt5 GUI #########################
class FaceAttendanceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # init camera
        self.camcap = cv2.VideoCapture(0)
        if not self.camcap.isOpened():
            reply = QMessageBox.warning(self, "警告", "打开相机失败，请确保已连接USB相机。")
            exit()
        # init savedir
        self.facedir = 'register'
        if not os.path.exists(self.facedir):
            os.makedirs(self.facedir)
        # init params
        self.fw,self.fh = FACE_WIDTH,FACE_HEIGHT
        self.max_face_cnt = 5
        self.fimg_list,self.face_list,self.name_list = load_faces(self.facedir)
        self.attendance_dict = {}

        # init ui
        self.initUI()

        # init timer
        self.timer = QTimer()
        self.timer.start()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.capture)

        # start run
        self.run = True

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

        self.statusBar().showMessage(get_cur_time())
        
        # # init toolbar
        # self.toolbar = self.addToolBar('退出')
        # self.toolbar.addAction(exitAction) 

        # init image show
        title_height = 40
        img = self.grab_img()
        self.camwin = QLabel(self)
        self.camwin.setFixedWidth(img.shape[1])  
        self.camwin.setFixedHeight(img.shape[0])
        self.camwin.move(0,title_height)
        self.show_img(self.camwin, img)

        self.facewin = QLabel(self)
        self.facewin.setFixedWidth(self.fw)  
        self.facewin.setFixedHeight(self.fh*self.max_face_cnt)
        self.facewin.move(img.shape[1],title_height)

        self.title = QLabel(self)
        self.title.setFixedWidth(img.shape[1])  
        self.title.setFixedHeight(title_height)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setText('人脸考勤系统')
        pe = QPalette()  
        pe.setColor(QPalette.WindowText,Qt.green)  
        self.title.setPalette(pe)  
        self.title.setFont(QFont("Roman times",25))

        self.setGeometry(300, 300, img.shape[1]+self.fw+10, title_height+img.shape[0]+20)
        self.setWindowTitle('人脸考勤系统')   
        self.show()

    def show_about(self):
        reply = QMessageBox.about(self, "关于", "人脸考勤系统v1.0  by symao<maoshuyuan123@gmail.com>")

    def show_img(self, label, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h,w,c = img.shape
        qimg = QImage(img.data, w, h, c*w, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qimg))

    def check_attendance(self,img):
        cur_time = time.time()
        face_locations, face_names = face_recog(img,self.face_list,self.name_list)
        for loc,name in zip(face_locations,face_names):
            top,right,bottom,left = loc
            if name == 'Unknown':
                cv2.rectangle(img, (left,top), (right,bottom), (0,0,255), 1)
            else:
                cv2.rectangle(img, (left,top), (right,bottom), (55,255,155), 1)
                cv2.putText(img, name, (left, top - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 255), 1)
                if name not in self.attendance_dict:
                    self.attendance_dict[name] = [cur_time,cur_time]
                elif cur_time > self.attendance_dict[name][1]:
                        self.attendance_dict[name][1] = cur_time

        print_names = [t[0] for t in sorted([(x,y[1]) for x,y in self.attendance_dict.items() if cur_time - y[1] < 10], key=lambda x:x[1])]

        self.show_img(self.camwin, img)
        if print_names:
            self.statusBar().showMessage(get_cur_time()+' 签到成功: '+ ','.join(print_names))
            self.show_img(self.facewin,
                np.vstack([self.fimg_list[self.name_list.index(name)] for name in print_names[-self.max_face_cnt:]]))
        else:
            self.statusBar().showMessage(get_cur_time())
            self.facewin.clear()

    def capture(self):
        if not self.run:
            return
        img = self.grab_img()
        self.check_attendance(img)

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