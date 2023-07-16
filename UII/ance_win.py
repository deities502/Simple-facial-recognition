# 参考之前的代码框架。
# 创建人脸视窗注册类，实例化reg对象。实现人脸打卡考勤系统的界面设计
import sys
import csv
import cv2
import dlib
import time
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QLineEdit, QPushButton,QMessageBox
import threading
import numpy as np
from new_put_text import cv2_chinese_text
from PyQt5.QtCore import pyqtSignal
import datetime
import pymysql
from database_op import insert_face,fetch_data_from_database

class attendanceWin(QWidget):
    exit_singal = pyqtSignal()

    # 创建一个空字典来存储每个人的上次打卡时间
    last_check_time = {}
    # 添加一个变量来存储图书馆内的人数
    people_in_library = 0
    # 创建一个空字典来存储每个人的状态
    people_status = {}

    def __init__(self):  # 构造函数
        super(attendanceWin, self).__init__()  # 调用父类的构造函数
        # 就可以设计或者初始化界面
        # 初始化predict_name.防止一开始摄像头开启该参数为空；
        self.priedict_name = ""
        # 设置图标
        self.setWindowIcon(QIcon("../img/recognize.png"))
        # 设置窗口的标题
        self.setWindowTitle("人脸考勤打卡界面")
        # 重新设置界面的大小
        self.resize(1000, 800)
        # 调用界面初始化的函数
        self.flag=0
        self.win_init()

    def win_init(self):
         '''

         :return:
         '''
         # 准备界面上需要用到的组件
         # 准备一个实时显示摄像头画面信息的标签
         self.pic_lab = QLabel(self)
         # 设置位置以及大小
         self.pic_lab.setGeometry(100, 80, 780, 482) # 长/宽 = 1.618
         # 给标签设置图片信息, 让图片自适应标签的大小
         self.pic_lab.setPixmap(QPixmap("../img/recognize.png").scaled(self.pic_lab.size()))

         # 准备一个打开摄像头的按钮
         self.open_btn = QPushButton(self)
         # 设置文本内容
         self.open_btn.setText("Open Camera")
         # 设置位置
         self.open_btn.setGeometry(100, 650, 200, 40)
         # 信号与槽函数关联
         self.open_btn.clicked.connect(self.show_pic)


         # 添加一个attendace按钮，触发人脸比对算法
         self.attendace_btn = QPushButton(self)
         # 设置文本内容
         self.attendace_btn.setText("Attendance")
         # 设置位置
         self.attendace_btn.setGeometry(350,650,200,40)
         # 关联槽函数
         self.attendace_btn.clicked.connect(self.attendance_slot)  # 设置文本内容


         # 准备一个退出按钮
         self.exit_btn = QPushButton(self)
         # 设置文本内容
         self.exit_btn.setText("Exit")
         # 设置位置
         self.exit_btn.setGeometry(600, 650, 200, 40)
         # 信号与槽函数关联
         self.exit_btn.clicked.connect(self.exit_pic)

    import pymysql
    import numpy as np

    def get_feature(self):
        '''
        从数据库中获取ID, NAME, 人脸特征值。
        生成一个n行*128的numpy类型的数组  self.feature_list
        数据库中的字符串---组装到对应的列表中labelID_list   name_list  feature_list
        :return:
        '''
        self.labelID_list = []
        self.name_list = []
        self.feature_list = None
        # 连接到数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='java',
            database='database_face',
            charset='utf8'
        )

        # 创建一个游标对象来执行SQL语句
        cursor = conn.cursor()

        # 查询数据
        select_data_query = '''
        SELECT ID, NAME, FACEINFO
        FROM face
        '''
        cursor.execute(select_data_query)


        # 遍历查询结果

        for line in cursor.fetchall():
            self.labelID_str = line[0]  #
            self.name_str = line[1]  # 按行读取的姓名符串
            print(line[0])
            self.labelID_list.append(self.labelID_str)
            self.name_list.append(self.name_str)  # 姓名字符串存入列表中
            self.face_descriptor = eval(line[2])  # 人脸特征数值保存到face_descriptor

            # 范数计算 一维的face_descritptor转置为n*128
            self.face_descriptor = np.asarray(self.face_descriptor, dtype=np.float64)
            self.face_descriptor = np.reshape(self.face_descriptor, (1, -1))
            print("dddddddddddddddddddddddddddd")
            print(self.face_descriptor)

            if self.feature_list is None:  # 首次初始化feature_list 异常判断，不能在空的条件下进行拼接
                self.feature_list = self.face_descriptor

            else:  # 两个矩阵进行拼接，拼接的时候要求矩阵的维度是一样的
                self.feature_list = np.concatenate((self.feature_list, self.face_descriptor), axis=0)
            print(self.feature_list)
        return


    def attendance_slot(self):

        if self.people_in_library >= 2:
            # 使用QMessageBox显示一个警告弹窗
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("自习室人数已满")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return

        #1. 调用get_ feature()函数，采集CSV中的人脸特征值
        self.get_feature()

        self.load_hog_doctor()

        #  3.计算实时人脸特征值 输出归一化的数据  （入口参数 这一帧画面的人脸图像，人脸68个坐标点对象）
        face_descriptor = self.face_descriptor_extractor.compute_face_descriptor(self.rgb_img,self.landmarks)

        #  3.1  先把face_descriptor vector转换为list
        face_descriptor_list = [f for f in face_descriptor]

        #  3.2  face_descriptor_list 转换为numpy
        face_descriptor_array = np.asarray(face_descriptor_list,dtype=np.float64)
        # print(face_descriptor_array)
        print("sssssssssssssssssssssssssss")
        distance = np.linalg.norm((face_descriptor_array - self.feature_list),axis = 1)
        print(face_descriptor_array)



        min_index = np.argmin(distance)
        print(min_index)
        min_distance = distance[min_index]
        print(min_distance)
        threadhold = 0.7

        #  创建打卡考勤文本


        # 获取当前时间
        current_time = datetime.datetime.now()



        # 检查是否已经超过晚上10点
        if current_time.hour >= 22 or current_time.hour <= 7:
            # 使用QMessageBox显示一个警告弹窗
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("自习室已经关闭")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return

        #7.依据满足阈值条件，通过索引值输出ID号和姓名 predict_id   self.priedict_name
        if min_distance < threadhold:
            predict_id = self.labelID_list[min_index]
            self.priedict_name = self.name_list[min_index]

            # 判断该人员的上次打卡时间与当前时间的间隔是否超过5分钟
            if predict_id not in self.last_check_time or (
                    current_time - self.last_check_time[predict_id]).seconds >= 1:
                # 判断此人是否已经在图书馆内
                if predict_id in self.people_status and self.people_status[predict_id] == 'in':
                    # 此人正在图书馆内，现在是签离状态
                    self.people_status[predict_id] = 'out'
                    msgBox = QMessageBox()
                    msgBox.setIcon(QMessageBox.Warning)
                    msgBox.setText("签离成功")
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    self.people_in_library -= 1
                else:
                    # 此人不在图书馆内，现在是签到状态
                    self.people_status[predict_id] = 'in'
                    msgBox = QMessageBox()
                    msgBox.setIcon(QMessageBox.Warning)
                    msgBox.setText("签到成功")
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    self.people_in_library += 1

                # 更新该人员的上次打卡时间
                self.last_check_time[predict_id] = current_time

                # 获取当前的时间，id号和name值都写入到attendace.csv中 打卡考勤文本
                now = time.time()
                time_str = time.strftime('%Y-%m-%d,%H:%M:%S', time.localtime(now))

                # 打卡的时间需要写入 注意时间的格式符合人基本阅读习惯2023/10/1 9:04

                da = insert_face(predict_id, self.priedict_name, time_str)

                print("{time}:写入成功，{name}".format(name=self.priedict_name, time=time_str))

        else:
            # 使用QMessageBox显示一个警告弹窗
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("未识别的人脸，请先进行注册")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()

    def exit_pic(self):
        '''
        退出按钮触发的事件
        :return:
        '''
        print("关闭摄像头")
        self.flag=1  # 摄像头的视频流关闭
        self.exit_singal.emit()
        self.close()            # 视窗reg对象直接关闭

    def load_hog_doctor(self):
        '''
        加载hog的相关数据人脸模型对象
        :return:
        '''
        # 加载人脸检测模型
        self.face_detect = dlib.get_frontal_face_detector()
        # 加载68个核心特征点
        self.shape_desp = dlib.shape_predictor("../resource/shape_predictor_68_face_landmarks.dat")
        # 加载特征描述符实例图像
        self.face_descriptor_extractor = dlib.face_recognition_model_v1("../resource/dlib_face_recognition_resnet_model_v1.dat")

    def show_pic(self):
        self.load_hog_doctor()
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if self.capture.isOpened(): #打开成功
            # 读取画面数据
            while True:
                ret, frame = self.capture.read()
                if ret: #ret 表示是否有都到画面数据，如果有，就可以去做显示
                    # 灰度处理
                    frame = cv2.flip(frame, 1)
                    self.gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # 人脸检测
                    faces = self.face_detect(self.gray_img)
                    # 遍历得到的人脸，进行人脸区域绘制

                    for face in faces:
                        self.x1 = face.left()
                        self.y1 = face.top()
                        self.x2 = face.right()
                        self.y2 = face.bottom()

                    # 获取当前人脸的68个特征点
                        self.landmarks = self.shape_desp(self.gray_img, box=face)
                        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2)
                    frame = cv2_chinese_text(frame, self.priedict_name, (self.x1, self.y2 + 20), (255, 255, 0), 20)
                        # opencv 得到的像素数据的通道 bgr   图像像素数据通道：rgb
                    self.rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转成rgb的像素数数   m
                    # 借助标签去显示图像  需要把mat矩阵数据转成QImage类型的，再转成QPixmap类型
                    # 参数1：就是图像的像素数据值   参数2：图像的宽度   参数3：图像的高度   参数4：格式
                    self.q_img = QImage(self.rgb_img.data, self.rgb_img.shape[1], self.rgb_img.shape[0], QImage.Format_RGB888)  # shape  (行，列，通道数)
                    self.pic_lab.setPixmap(QPixmap.fromImage(self.q_img).scaled(self.pic_lab.size()))
                    key = cv2.waitKey(1)



# main函数程序的入口
if __name__ == '__main__':
    # 创建对象的
    app = QApplication(sys.argv)  # 需要系统参数
    # 创建了注册类的对象
    att = attendanceWin()
    # 如何显示界面
    att.show()
    sys.exit(app.exec_()) # 让你的程序进入到一个事件循环机制中，有任务来处理任务，
                        # 没有任务产生，进行等待，直到exit()函数被调用整个程序才会结束


