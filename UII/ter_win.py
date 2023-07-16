from PyQt5.QtGui import QIcon,QPixmap,QImage
from PyQt5.QtWidgets import QWidget,QApplication,QLabel,QLineEdit,QPushButton,QMessageBox
from PyQt5.QtCore import pyqtSignal
from database_op import insert_face_data,fetch_data_from_database
import sys
import cv2
import dlib
import threading
import time
import csv




class registerWin(QWidget):
    exit_singal = pyqtSignal()
    def __init__(self):
        super(registerWin,self).__init__()  #调用父类的构造函数
        # 窗口设置图标

        self.setWindowIcon(QIcon("../img/reg.jpg"))
        # 窗口的标题
        self.setWindowTitle("人脸考勤注册界面")
        # 窗口的大小
        self.resize(1000,800)
        # 调用界面初始化函数
        self.win_init()
        self.db_manager = insert_face_data
        # 初始化采集次数
        self.count = 0
        self.flag=0

    def win_init(self):
        '''
        准备界面上需要用到的组件
        准备一个实时显示摄像头画面的标签
        :return:
        '''
        # 在窗口加载图片
        self.pic_lab = QLabel(self)
        self.pic_lab.setGeometry(100,80,700,480)
        # 给标签设置一个图片信息  让图片自适应标签的大小
        self.pic_lab.setPixmap(QPixmap('../img/reg.jpg').scaled(self.pic_lab.size()))

        # 设置文本内容
        self.ID_lab = QLabel(self)
        self.ID_lab.setText("ID:")
        self.ID_lab.setGeometry(100,580,200,50)

        # 设置姓名文本内容
        self.name_lab = QLabel(self)
        self.name_lab.setText("Name:")
        self.name_lab.setGeometry(500,580,80,50)

        # 设置文本输入框
        self.name_edit = QLineEdit(self)
        self.name_edit.setGeometry(600,580,200,50)

        self.id_edit = QLineEdit(self)
        self.id_edit.setGeometry(200,580,200,50)

        # 准备一个摄像头打开的按钮
        self.open_btn = QPushButton(self)
        self.open_btn.setText("Open Camera")
        self.open_btn.setGeometry(100, 650, 200, 40)
        # 信号与槽函数关联
        self.open_btn.clicked.connect(self.show_pic)

        # 准备一个人脸录入的按钮
        self.reg_btn = QPushButton(self)
        self.reg_btn.setText("Register")
        self.reg_btn.setGeometry(350,650,200,40)
        self.reg_btn.clicked.connect(self.reg_pic)

        # 准备一个退出按钮
        self.exit_btn = QPushButton(self)
        self.exit_btn .setText("Exit")
        self.exit_btn .setGeometry(600, 650, 200, 40)
        self.exit_btn.clicked.connect(self.exit_pic)



    def show_pic(self):
        '''
        打开摄像头，frame,采集人脸图像image和face，调用load_hog_face_decetor函数
        绘制人脸矩形框，解析人脸坐标，获得人脸128个特征向量
        :return:
        '''

        # 1.加载人脸检测模型
        self.face_hog_decetor = dlib.get_frontal_face_detector()
        # 2.加载68个人脸检测模型
        self.shape_detector = dlib.shape_predictor("../resource/shape_predictor_68_face_landmarks.dat")
        # 3. 加载128个特征人脸向量对象
        self.face_descriptor_ectractor = dlib.face_recognition_model_v1("../resource/dlib_face_recognition_resnet_model_v1.dat")
        # 打开摄像头，创建视频流
        self.capture= cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while (self.capture.isOpened()):
            retval,image = self.capture.read()
            if retval == True:
                # 图像做灰度处理
                image = cv2.flip(image,1)
                self.gray_img = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
                # 人脸矩形框坐标对象的生成
                faces = self.face_hog_decetor(self.gray_img)
                # 遍历人脸解析坐标
                for face in faces:
                    x1 = face.left()
                    y1 = face.top()
                    x2 = face.right()
                    y2 = face.bottom()
                    # 获取当前68个人脸特征点
                    self.landmarks = self.shape_detector(self.gray_img,box = face)

                    # 遍历68个人脸特征点
                    for n in range(0,68):
                        x = self.landmarks.part(n).x
                        y = self.landmarks.part(n).y
                        cv2.circle(image,(x,y),2,(0,255,0),2)
                    cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),2)

                # image图像进行转换，适合在pic_lab对象上面进行展示
                # image转换成RGB
                self.rgb_img = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

                # rgb_img转换成QImage类型 mat矩阵转换成QImage
                # 参数1：self.rgb_img.data 代表是像素的数值 参数2：图像的宽度 参数3,：图像的高度 参数4：格式
                self.q_img = QImage(self.rgb_img.data,self.rgb_img.shape[1],self.rgb_img.shape[0],QImage.Format_RGB888)

                # q_img才能在pic_lab.setPixmap进行展示
                self.pic_lab.setPixmap(QPixmap.fromImage(self.q_img).scaled(self.pic_lab.size()))
                key = cv2.waitKey(1)

    def save_info(self):
        name = self.name_edit.text()
        ID = self.id_edit.text()

        if ID == "" or name == "":
            QMessageBox.warning(self, '警告', 'ID或者用户名不允许有空格数据', QMessageBox.Ok)

            return
        else:
            s,t,y=fetch_data_from_database()

            if str(ID) in s:
                print("verfwsfsrg")
                msg = QMessageBox()
                msg.setWindowTitle("提示")
                msg.setText("该学生经注册过了！")
                msg.setIcon(QMessageBox.Information)
                msg.exec_()
                return False
            else:


                face_feature = self.face_descriptor_ectractor.compute_face_descriptor(self.rgb_img, self.landmarks)

                self.feature_des = [feature for feature in face_feature]
                print(self.feature_des)
                insert_face_data(ID, name, str(self.feature_des))

                return True
    def reg_pic(self):
        '''
        当register按钮按下，发生clicked信号关联的槽函数
        是去定时采集人脸信息，录入到csv中
        :return:
        '''
        # 记录采集的次数
        print("2222")
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        self.count += 1
        if self.count < 2:
            if self.save_info():  # 如果 save_info 返回 True，那么设置定时器
                threading.Timer(3, self.reg_pic).start()
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("注册成功")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
        else:
            self.count = 0



    def exit_pic(self):
        '''
        退出按钮按下去 摄像头关闭
        reg对象关闭
        :return:
        '''

        print("关闭摄像头")
        # 摄像头视频流的关闭
        self.flag=1
        print(self.exit_singal)

        self.exit_singal.emit()
        self.name_edit.clear()
        self.id_edit.clear()

        # 对象窗口的关闭
        self.close()
        # self.db_manager.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 创建一个注册类窗口的对象
    reg = registerWin()
    # 展示
    reg.show()
    sys.exit(app.exec())