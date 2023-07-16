import sys
from PyQt5.QtGui import QIcon,QFont,QPixmap
from PyQt5.QtWidgets import QWidget,QApplication,QLabel,QPushButton,QMessageBox
from ter_win import registerWin
from ance_win import attendanceWin

class IndexWidget(QWidget):

    def __init__(self):
        super(IndexWidget,self).__init__()
        self.setWindowIcon(QIcon("../img/opencamera.png"))
        self.setWindowTitle("基于AI的考勤系统")
        self.resize(1000,600)
        #创建注册类的
        self.reg = registerWin()
        #创建考勤登录类对象
        self.att = attendanceWin()
        #初始化窗口函数
        self.win_init()

    def win_init(self):
        '''
        主菜单界面的组件设计
        :return:
        '''
        # 在窗口加载函数
        self.pic_lab = QLabel(self)
        self.pic_lab.setGeometry(250, 100,700, 400)
        # 给标签设置一个图片信息，让图片适应标签的大小
        self.pic_lab.setPixmap(QPixmap("../img/zixishi.png").scaled(self.pic_lab.size()))
        self.title_lab = QLabel("欢迎使用智能自习室考勤系统", self)
        self.title_lab.setGeometry(350, 20, 980, 100)
        #字体设置
        font = QFont()
        font.setPointSize(24)
        #给标签设置字体
        self.title_lab.setFont(font)

        #人脸考勤打卡登录按钮设置
        self.attlogin_btn = QPushButton(self)
        self.title_lab = QLabel("打卡系统", self)
        self.title_lab.setGeometry(70, 100, 256, 256)
        font = QFont()
        font.setPointSize(14)
        # 给标签设置字体
        self.title_lab.setFont(font)
        # 按钮上面放一张照片
        self.attlogin_btn.setStyleSheet("border-image:url(../img/recognize.png)")
        self.attlogin_btn.setGeometry(50,80,128,128)

        #人脸录入系统的登录
        self.reg_btn = QPushButton(self)
        self.reg_btn.setStyleSheet("border-image:url(../img/opencamera.png)")
        self.reg_btn.setGeometry(50,250,128,128)
        self.title_lab = QLabel("注册系统", self)
        self.title_lab.setGeometry(70, 270, 256, 256)
        font = QFont()
        font.setPointSize(14)
        # 给标签设置字体
        self.title_lab.setFont(font)


        #退出按钮的设置
        self.exit_btn = QPushButton(self)
        self.exit_btn.setText("")
        self.exit_btn.setStyleSheet("border-image:url(../img/exit2.jpg)")
        self.exit_btn.setGeometry(50,420,128,128)
        self.title_lab = QLabel("退出", self)
        self.title_lab.setGeometry(90, 440, 256, 256)
        font = QFont()
        font.setPointSize(14)
        # 给标签设置字体
        self.title_lab.setFont(font)

        #信号关联槽函数
        self.attlogin_btn.clicked.connect(self.attlogin_slot)
        self.reg_btn.clicked.connect(self.reg_slot)
        self.exit_btn.clicked.connect(self.exit_slot)

        #主界面接收来自子菜单的退出信号
        self.reg.exit_singal.connect(self.show)
        self.att.exit_singal.connect(self.show)


    def attlogin_slot(self):
        '''
        点击人脸打卡登录按钮是进入登录界面
        :return:
        '''
        #登录对象展示
        self.att.show()
        #当前的主界面对象隐藏
        self.hide()

    def reg_slot(self):
        # 注册对象展示
        self.reg.show()
        # 当前的主界面对象隐藏
        self.hide()

    def exit_slot(self):
        # 退出对象展示
        res = QMessageBox.question(self,"Library","确定要退出吗？",QMessageBox.Yes|QMessageBox.No)
        if res == QMessageBox.Yes:
            exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    index = IndexWidget()
    index.show()
    sys.exit(app.exec())

