import os
import sys
from PyQt5.Qt import *
from RecognitionMain import recWin
from RecognitionRegister import registerWin
from SQL import sqlite
class loadWin(QMainWindow):
    def __init__(self):
        super().__init__()
        _startPos = None #鼠標移動視窗的初始位置
        _endPos = None #鼠標移動視窗的最終位置
        _isTracking = False #是否重構移動事件
        self.db = sqlite.Database('SQL/User.db')#連接資料庫
        self.check_win = recWin()#初始化主視窗
        self.register_win=registerWin()#初始化注冊視窗
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  #使用CPU
        self.initUI()

    def initUI(self):
        self.setStyleSheet('''
            #top_left_button{
                border-radius:5px;
                color:rgb(255,255,255);font-size:15px}
            #top_right1_button{
                background:#F76677;border-radius:15px;
                color:rgb(255,255,255);font-size:15px}
            #top_right1_button:hover{
                background:red;color:black;}      
            #top_right2_button{
                background:#F7D674;border-radius:15px;
                color:rgb(255,255,255);font-size:15px;}  
            #top_right2_button::hover{
                background:yellow;color:black;}     
            #title_label{
                color:rgb(255,255,255);font-size:40px;font-weight:bold;}
            #top_widget{
                background-color:rgb(54, 54, 54);
                border-top:1px darkGray;border-bottom:1px darkGray;
                border-right:1px darkGray;border-left:1px darkGray;
                border-top-left-radius:15px;border-top-right-radius:15px;}
            #mid_widget{
                background-color:rgb(105, 105, 105);}
            #bottom_widget{
                background-color:rgb(181, 181 ,181);
                border-bottom:1px darkGray;
                border-left:1px darkGray;border-right:1px darkGray;
                border-bottom-right-radius:15px;border-bottom-left-radius:15px; }  
            #btn{
                background-color:#F0FFFF;color:#000000;border:none;border-radius:4px;
                font-weight:bold;font-size:20px;}
            #btn::hover{
                background-color:rgb(176,196,222); color:black;}
            #label_edit{
                color:#FFFFFF;font-size:18px;}
            #text_edit{
                background:rgb(193,205 ,193);font-size:15px;
                border:1px solid gray;width:300px;
                border-radius:10px;padding:2px 4px;}
            #text_edit::hover{
                background:rgb(255,255 ,255);}
            #text_edit::click{
                background:rgb(255,255 ,255);}   
        ''')
        self.setFixedSize(650, 420)#定義視窗大小
        self.setWindowIcon(QIcon('icon/control.png'))#設置圖標
        self.setWindowFlag(Qt.FramelessWindowHint) #隱藏邊框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 設置窗口透明度

        '''右上按鈕'''
        self.title = QLabel("支票自動識別系統", self)
        self.title.setFixedHeight(100)
        self.title.setObjectName('title_label')
        self.smallscreen = QPushButton("-", self)#最小化視窗按鈕
        self.smallscreen.setObjectName('top_right1_button')
        self.quitscreen = QPushButton("X", self)#關閉視窗按鈕
        self.quitscreen.setObjectName('top_right2_button')
        self.smallscreen.setFixedSize(30, 30)
        self.quitscreen.setFixedSize(30, 30)

        '''圖片部件'''
        self.pic_label = QLabel()
        self.pic_label.setObjectName('pic_label')
        pixmapa = QPixmap("icon/test_Profilepic.jpg")
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)
        ##使用QPainter將圖片轉化爲圓形##
        painter = QPainter(pixmap)
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        path = QPainterPath()
        path.addEllipse(0, 0, 120, 120)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, 120, 120, pixmapa)
        painter.end()
        ##使用QPainter將圖片轉化爲圓形##
        self.pic_label.setPixmap(pixmap)

        '''登錄部件'''
        self.lbl_workerid = QLabel("用戶名")
        self.lbl_workerid.setObjectName('label_edit')
        self.lbl_workerid.setFont(QFont("Microsoft YaHei"))
        self.led_workerid = QLineEdit()
        self.led_workerid.setObjectName('text_edit')
        self.led_workerid.setText("")
        self.led_workerid.setPlaceholderText("請輸入已注冊的郵箱")
        self.text_letter = QRegExp('[a-zA-z0-9 .@]+$')#正則化表示，規定只能輸入a-zA-z0-9.@
        self.validator = QRegExpValidator(self)#使用正則化構造
        self.validator.setRegExp(self.text_letter)
        self.led_workerid.setValidator(self.validator)
        self.led_workerid.setFixedWidth(270)
        self.led_workerid.setFixedHeight(38)

        self.lbl_pwd = QLabel("密碼")
        self.lbl_pwd.setObjectName('label_edit')
        self.lbl_pwd.setFont(QFont("Microsoft YaHei"))
        self.led_pwd = QLineEdit()
        self.led_pwd.setObjectName('text_edit')
        self.led_pwd.setText("")
        self.led_pwd.setPlaceholderText("請輸入密碼")
        self.text_letter = QRegExp('[a-zA-z0-9]+$')#正則化表示，規定只能輸入a-zA-z0-9
        self.validator = QRegExpValidator(self)#使用正則化構造
        self.validator.setRegExp(self.text_letter)
        self.led_pwd.setValidator(self.validator)
        self.led_pwd.setEchoMode(QLineEdit.Password)#輸入字符會隱藏
        self.led_pwd.setFixedWidth(270)
        self.led_pwd.setFixedHeight(38)

        self.key = QLabel("授權碼")
        self.key.setObjectName('label_edit')
        self.key.setFont(QFont("Microsoft YaHei"))
        self.key_pwd = QLineEdit()#授權碼edit
        self.key_pwd.setObjectName('text_edit')
        self.key_pwd.setText("")
        self.key_pwd.setPlaceholderText("請輸入銀行的授權碼")
        self.text_letter = QRegExp('[a-zA-z0-9]+$')#正則化表示，規定只能輸入a-zA-z0-9
        self.validator = QRegExpValidator(self)#使用正則化構造
        self.validator.setRegExp(self.text_letter)
        self.key_pwd.setValidator(self.validator)
        self.key_pwd.setFixedWidth(270)
        self.key_pwd.setFixedHeight(38)

        self.btn_login = QPushButton("登錄")
        self.btn_login.setFixedWidth(140)
        self.btn_login.setFixedHeight(50)
        self.btn_login.setFont(QFont("Microsoft YaHei"))
        self.btn_login.setObjectName("btn")

        self.btn_Register = QPushButton("注冊")
        self.btn_Register.setFixedWidth(140)
        self.btn_Register.setFixedHeight(50)
        self.btn_Register.setFont(QFont("Microsoft YaHei"))
        self.btn_Register.setObjectName("btn")

        '''主佈局'''
        self.main_widget = QWidget()#定義主畫布QWidget
        self.main_widget.setObjectName('main_widget')
        self.main_layout = QVBoxLayout()#主畫布垂直佈局Layout
        self.main_layout.setSpacing(0)

        '''頂部佈局'''
        self.top_widget = QWidget()#定義頂部畫布QWidget
        self.top_widget.setObjectName('top_widget')
        self.top_layout = QHBoxLayout()#頂部平行佈局Layout
        self.top_layout.setAlignment(Qt.AlignTop)
        self.top_layout.setObjectName('top_layout')
        self.top_widget.setLayout(self.top_layout)#將頂部佈局放入頂部畫布

        '''中間佈局'''
        self.mid_widget = QWidget()#定義中間畫布QWidget
        self.mid_widget.setObjectName('mid_widget')
        self.mid_layout = QHBoxLayout()#中間平行佈局Layout
        self.mid_layout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        self.mid_layout.setObjectName('mid_layout')
        self.mid_widget.setLayout(self.mid_layout)#將中間佈局放入中間畫布


        '''底部佈局'''
        self.bottom_widget = QWidget()#定義底部畫布QWidget
        self.bottom_widget.setObjectName('bottom_widget')
        self.bottom_layout = QHBoxLayout()#底部平行佈局Layout
        self.bottom_layout.setAlignment(Qt.AlignTop)
        self.bottom_layout.setObjectName('bottom_layout')
        self.bottom_widget.setLayout(self.bottom_layout)#將底部佈局放入底部畫布

        '''添加頂部部件'''
        self.top_layout.addStretch(1)#間距伸縮
        self.top_layout.addWidget(self.smallscreen)#將最小化按鈕放入頂部佈局
        self.top_layout.addWidget(self.quitscreen)#將關閉按鈕放入頂部佈局

        '''添加中間部件'''
        self.mid_layout.addWidget(self.title)#將標題放入中間佈局

        '''添加底部部件'''
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch(1)
        self.btn_layout.addWidget(self.btn_login)
        self.btn_layout.addStretch(2)
        self.btn_layout.addWidget(self.btn_Register)
        self.btn_layout.addStretch(1)
        self.fmlayout = QFormLayout()
        self.fmlayout.addRow(self.lbl_workerid, self.led_workerid)
        self.fmlayout.addRow(self.lbl_pwd, self.led_pwd)
        self.fmlayout.addRow(self.key, self.key_pwd)
        self.fmlayout.addRow(self.btn_layout)
        self.fmlayout.setHorizontalSpacing(20) # 調整間距
        self.fmlayout.setVerticalSpacing(15)
        self.bottom_layout.addStretch(1)
        self.bottom_layout.addWidget(self.pic_label, 1, Qt.AlignCenter)
        self.bottom_layout.addStretch(1)
        self.bottom_layout.addLayout(self.fmlayout, 2)
        self.bottom_layout.addStretch(1)

        '''主佈局添加'''
        self.main_layout.addWidget(self.top_widget)#主佈局添加頂部畫布
        self.main_layout.addWidget(self.mid_widget)#主佈局添加中間畫布
        self.main_layout.addWidget(self.bottom_widget)#主佈局添加底部畫布
        self.main_widget.setLayout(self.main_layout)#將主佈局放入主畫布
        self.setCentralWidget(self.main_widget)

        '''按鈕事件'''
        self.smallscreen.clicked.connect(self.minium_Windows)
        self.quitscreen.clicked.connect(self.close_Windows)
        self.btn_login.clicked.connect(self.word_get)
        self.btn_Register.clicked.connect(self.to_register)

    '''點擊登錄按鈕動作，通過輸入的信息比對資料庫中是否正確存在，進入主窗口'''
    def word_get(self):
        login_user = self.led_workerid.text()
        login_password = self.led_pwd.text()
        ret =self.db.sql_search('user',login_user,login_password)
        if login_user=="" or login_password=="" or  self.key_pwd.text=="":
            QMessageBox.warning(self,
                                "警告",
                                "請填入有效信息！",
                                QMessageBox.Yes)
        elif ret is None or (login_user[-4:]!='.com' and login_user!='admin'):
            QMessageBox.warning(self,
                                "警告",
                                "用戶不存在！",
                                QMessageBox.Yes)
        elif ret[0]==login_password and self.key_pwd.text()=='admin':
            self.db.sql_edit('user',self.key_pwd.text() , login_user)
            self.check_win.show()
            self.close()
        else:
            QMessageBox.warning(self,
                                "警告",
                                "錯誤信息！",
                                QMessageBox.Yes)
        self.led_workerid.setFocus()

    '''點擊注冊按鈕，進入注冊視窗'''
    def to_register(self):
        self.register_win.show()
        self.close()

    def mouseMoveEvent(self, e: QMouseEvent):  # 重構移動事件
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):# 重構移動事件
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):# 重構移動事件
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    @pyqtSlot()
    def minium_Windows(self): #窗口最小化事件
        self.showMinimized()

    @pyqtSlot()
    def close_Windows(self):#窗口關閉事件
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.processEvents()
    window = loadWin()
    window.show()
    sys.exit(app.exec_())