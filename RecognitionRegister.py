import sys
import random
import re
from PyQt5.Qt import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import time
from SQL import sqlite,CommonUtil
'''發送郵件驗證碼時，通過子綫程進行等待'''
class Thread(QThread):
    _signal =pyqtSignal()
    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(3):#延長3s，防止重複發送驗證碼
            time.sleep(1)
        self._signal.emit()

class registerWin(QMainWindow):
    def __init__(self):
        super().__init__()
        _startPos = None
        _endPos = None
        _isTracking = False
        self.initUI()
        self.idcode = 0
        self.le_ls = [self.mailid, self.led_pwd, self.led_pwd_2, self.mail_key]#用列表先保存注冊信息
        self.db = sqlite.Database('SQL/User.db') # 獲取資料庫

    def initUI(self):
        self.setStyleSheet('''
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
                    color:rgb(255,255,255);font-size:30px;font-weight:bold;}
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
                #btn_send{
                     background-color:#F0FFFF;color:#000000;border:none;
                     border-radius:4px;}
                #btn_send::hover{
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
                #title_label{
                    color:rgb(255,255,255);font-size:45px;font-weight:bold;}
                ''')
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon('icon/control.png'))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        '''右上按鈕'''
        self.title = QLabel("系統注册", self)
        self.title.setFixedHeight(100)
        self.title.setObjectName('title_label')
        self.smallscreen = QPushButton("-", self)
        self.smallscreen.setObjectName('top_right1_button')
        self.quitscreen = QPushButton("X", self)
        self.quitscreen.setObjectName('top_right2_button')
        self.smallscreen.setFixedSize(30, 30)
        self.quitscreen.setFixedSize(30, 30)

        '''注冊部件'''
        self.mail_label = QLabel("輸入郵箱")
        self.mail_label.setObjectName('label_edit')
        self.mail_label.setFont(QFont("Microsoft YaHei"))
        self.mailid = QLineEdit()
        self.mailid.setObjectName('text_edit')
        self.mailid.setPlaceholderText("請輸入注册郵箱")
        self.text_letter = QRegExp('[a-zA-z0-9 .@]+$')
        self.validator = QRegExpValidator(self)
        self.validator.setRegExp(self.text_letter)
        self.mailid.setValidator(self.validator)
        self.mailid.setFixedWidth(270)
        self.mailid.setFixedHeight(38)

        self.lbl_pwd = QLabel("輸入密碼")
        self.lbl_pwd.setObjectName('label_edit')
        self.lbl_pwd.setFont(QFont("Microsoft YaHei"))
        self.led_pwd = QLineEdit()
        self.led_pwd.setObjectName('text_edit')
        self.led_pwd.setPlaceholderText("請輸入密碼")
        self.text_letter = QRegExp('[a-zA-z0-9]+$')
        self.validator = QRegExpValidator(self)
        self.validator.setRegExp(self.text_letter)
        self.led_pwd.setValidator(self.validator)
        self.led_pwd.setFixedWidth(270)
        self.led_pwd.setFixedHeight(38)

        self.lbl_pwd_2 = QLabel("确认密碼")
        self.lbl_pwd_2.setObjectName('label_edit')
        self.lbl_pwd_2.setFont(QFont("Microsoft YaHei"))
        self.led_pwd_2 = QLineEdit()
        self.led_pwd_2.setObjectName('text_edit')
        self.led_pwd_2.setPlaceholderText("請再次輸入密碼")
        self.text_letter = QRegExp('[a-zA-z0-9]+$')
        self.validator = QRegExpValidator(self)
        self.validator.setRegExp(self.text_letter)
        self.led_pwd_2.setValidator(self.validator)
        self.led_pwd_2.setFixedWidth(270)
        self.led_pwd_2.setFixedHeight(38)

        self.mail = QLabel("邮箱驗證碼")
        self.mail.setObjectName('label_edit')
        self.mail.setFont(QFont("Microsoft YaHei"))
        self.mail_key = QLineEdit()
        self.mail_key.setObjectName('text_edit')
        self.mail_key.setPlaceholderText("請輸入驗證碼")
        self.text_letter = QRegExp('[0-9]+$')
        self.validator = QRegExpValidator(self)
        self.validator.setRegExp(self.text_letter)
        self.mail_key.setValidator(self.validator)
        self.mail_key.setFixedWidth(150)
        self.mail_key.setFixedHeight(38)

        self.btn_send = QPushButton("發送驗證")
        self.btn_send.setObjectName("btn_send")
        self.btn_send.setFixedWidth(120)
        self.btn_send.setFixedHeight(30)
        self.btn_send.setFont(QFont("Microsoft YaHei"))

        self.btn_confirm = QPushButton("確認")
        self.btn_confirm.setObjectName("btn")
        self.btn_confirm.setFixedWidth(120)
        self.btn_confirm.setFixedHeight(40)
        self.btn_confirm.setFont(QFont("Microsoft YaHei"))

        self.btn_back = QPushButton("返回")
        self.btn_back.setObjectName("btn")
        self.btn_back.setFixedWidth(120)
        self.btn_back.setFixedHeight(40)
        self.btn_back.setFont(QFont("Microsoft YaHei"))


        '''主佈局'''
        self.main_widget = QWidget()
        self.main_widget.setObjectName('main_widget')
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)

        '''頂部佈局'''
        self.top_widget = QWidget()
        self.top_widget.setObjectName('top_widget')
        self.top_layout = QHBoxLayout()
        self.top_layout.setAlignment(Qt.AlignTop)
        self.top_layout.setObjectName('top_layout')
        self.top_widget.setLayout(self.top_layout)

        '''中部佈局'''
        self.mid_widget = QWidget()
        self.mid_widget.setObjectName('mid_widget')
        self.mid_layout = QHBoxLayout()
        self.mid_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.mid_layout.setObjectName('mid_layout')
        self.mid_widget.setLayout(self.mid_layout)

        '''底部佈局'''
        self.bottom_widget = QWidget()
        self.bottom_widget.setObjectName('bottom_widget')
        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.setAlignment(Qt.AlignTop| Qt.AlignCenter)
        self.bottom_layout.setObjectName('bottom_layout')
        self.bottom_widget.setLayout(self.bottom_layout)

        '''添加頂部部件'''
        self.top_layout.addStretch(1)
        self.top_layout.addWidget(self.smallscreen)
        self.top_layout.addWidget(self.quitscreen)

        '''添加中部部件'''
        self.mid_layout.addWidget(self.title)

        '''添加底部部件'''
        self.mail_layout = QHBoxLayout()
        self.mail_layout.addWidget(self.mail_label)
        self.mail_layout.addStretch(1)
        self.mail_layout.addWidget(self.mailid)
        self.mail_layout.addStretch(1)
        self.pwd_layout = QHBoxLayout()
        self.pwd_layout.addWidget(self.lbl_pwd)
        self.pwd_layout.addStretch(1)
        self.pwd_layout.addWidget(self.led_pwd)
        self.pwd_layout.addStretch(1)
        self.pwd2_layout = QHBoxLayout()
        self.pwd2_layout.addWidget(self.lbl_pwd_2)
        self.pwd2_layout.addStretch(1)
        self.pwd2_layout.addWidget(self.led_pwd_2)
        self.pwd2_layout.addStretch(1)
        self.mailval_layout = QHBoxLayout()
        self.mailval_layout.addWidget(self.mail)
        self.mailval_layout.addWidget(self.mail_key,Qt.AlignTop )
        self.mailval_layout.addWidget(self.btn_send)
        self.mailval_layout.addStretch(1)
        self.bt_layout = QHBoxLayout()
        self.bt_layout.addStretch(1)
        self.bt_layout.addWidget(self.btn_confirm)
        self.bt_layout.addStretch(1)
        self.bt_layout.addWidget(self.btn_back)
        self.bt_layout.addStretch(1)
        self.bottom_layout.addLayout(self.mail_layout)
        self.bottom_layout.addLayout(self.pwd_layout)
        self.bottom_layout.addLayout(self.pwd2_layout)
        self.bottom_layout.addLayout(self.mailval_layout)
        self.bottom_layout.addLayout(self.bt_layout)
        self.bottom_widget.setLayout(self.bottom_layout)

        '''主佈局添加'''
        self.main_layout.addWidget(self.top_widget)
        self.main_layout.addWidget(self.mid_widget)
        self.main_layout.addWidget(self.bottom_widget)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        '''按鈕事件'''
        self.btn_send.clicked.connect(self.to_sendmail)
        self.smallscreen.clicked.connect(self.minium_Windows)
        self.quitscreen.clicked.connect(self.close_Windows)
        self.btn_confirm.clicked.connect(self.to_register)
        self.btn_back.clicked.connect(self.to_back)

    #發送郵件動作
    def send_email(self, idcode, email):
        smtpserver = 'smtp.qq.com'
        username = '3331336919@qq.com'#發送者郵箱
        password = 'fnzqswevmkzkcigi'
        sender = username
        receiver = email  # 收件人郵箱
        idCode = str(idcode)  # 驗證碼
        subject = Header("銀行支票系統注冊", 'utf-8').encode()
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = 'Check-Recognition-System'
        msg['To'] = receiver
        text = "這是你的驗證碼：" + idCode
        text_plain = MIMEText(text, 'plain', 'utf-8')
        msg.attach(text_plain)
        # 發送郵件
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()

    #開始準備發送郵件動作
    def to_sendmail(self):
        if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', self.mailid.text()):#正則化判斷注冊郵件是否格式正確
            self.idcode=random.randint(1000,9999)
            self.send_email(self.idcode,self.mailid.text())
            self.btn_send.setText('已發送！(3秒后重置)')
            self.btn_send.setEnabled(False)
            self.threads = Thread()
            self.threads._signal.connect(self.set_wait)
            self.threads.start()
        else:
            self.btn_send.setText('郵箱錯誤！(3秒后重置)' )
            self.btn_send.setEnabled(False)
            self.threads = Thread()
            self.threads._signal.connect(self.set_wait)
            self.threads.start()

    '''發送郵件按鈕重置'''
    def set_wait(self):
        self.btn_send.setEnabled(True)
        self.btn_send.setText('發送驗證')

    '''進行注冊動作'''
    def to_register(self):
        try:
            for temp in self.le_ls:
                if temp.text() == '':#判斷注冊内容是否有缺失
                    CommonUtil.hint_dialog(self, '提示', '請輸入信息')
                    return
            if self.db.query_super('USER', 'email', self.mailid.text())[0]!= 0:#判斷資料庫中是否有該用戶
                CommonUtil.hint_dialog(self, '提示', '用户已注冊')
                return
            if self.led_pwd.text()!=self.led_pwd_2.text():#判斷兩次密碼是否相同
                CommonUtil.hint_dialog(self, '提示', '兩次密碼不同')
                self.led_pwd_2.setText("")
                self.led_pwd_2.setText("")
                return
            if int(self.mail_key.text())!=self.idcode:#判斷驗證碼是否正確
                CommonUtil.hint_dialog(self, '提示', '驗證碼錯誤')
                return
            pwd=self.led_pwd_2.text()
            user_id = str(CommonUtil.get_uuid1())#從主機ID、序列號和當前時間生成UUID
            user_data = [user_id, self.mailid.text(), pwd, str(0),CommonUtil.get_current_time()]#存入到list
            self.db.insert_user(user_data)#將list存入到資料庫
            QMessageBox.warning(self,
                                "提示",
                                "注冊成功！",
                                QMessageBox.Yes)
            self.to_back()
        except Exception as e:
            print(e.args)

    '''返回動作'''
    def to_back(self):
        from RecognitionLoad import loadWin
        self.load_win = loadWin()
        self.load_win.show()
        self.db.close()
        self.close()

    def mouseMoveEvent(self, e: QMouseEvent):
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    @pyqtSlot()
    def minium_Windows(self):
        self.showMinimized()

    @pyqtSlot()
    def close_Windows(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = registerWin()
    a.show()
    sys.exit(app.exec_())