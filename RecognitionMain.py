import glob
import numpy as np
import os
from PyQt5.Qt import *
import sys
import cv2
import RecognitionModel
import pandas as pd
import time
import pandas.io.formats.excel
'''單張辨識子綫程'''
class Thread(QThread):
    _signal =pyqtSignal(np.ndarray,str,str,str,str,str)
    def __init__(self,pic):
        super().__init__()
        self.pic=pic

    def run(self):
        check_rec = RecognitionModel.Check_recognition(self.pic)
        self.check, self.account, self.check_account, self.chi_amount, self.num_amount,self.date = check_rec.rec_()  # 获取账号，支票账号
        time.sleep(1)
        self._signal.emit(self.check,self.account, self.num_amount, self.chi_amount, self.check_account,self.date)

'''多張辨識子綫程'''
class Thread_batch(QThread):
    _startsignal = pyqtSignal(np.ndarray,str,str,str,str,str,int)
    _stopsignal=pyqtSignal()
    _finishsignal=pyqtSignal()
    def __init__(self,pic_list):
        super().__init__()
        self.pic_list=pic_list
        self.check=None
        self.pic=np.ndarray
        self.stop_signal=True

    def stop(self):
        self.stop_signal = False

    def run(self):
        num=0
        for filepath in self.pic_list:
            if self.stop_signal==False:
                self._stopsignal.emit()
                return
            else:
                num+=1
                self.pic = cv2.imread(filepath)
                check_rec = RecognitionModel.Check_recognition(self.pic)
                self.check, self.account, self.check_account, self.chi_amount, self.num_amount,self.date = check_rec.rec_()  # 获取账号，支票账号
                time.sleep(1)
                self._startsignal.emit(self.check, self.account, self.num_amount, self.chi_amount,
                                       self.check_account,self.date,num)
        self._finishsignal.emit()

class recWin(QMainWindow):
    def __init__(self):
        super().__init__()
        _startPos = None
        _endPos = None
        _isTracking = False
        self.flag_batch = False  #判斷是否需要多張辨識，True是多張
        self.cwd = os.getcwd()  # 获獲取當前程式文件位置
        self.pic_list = []  # 保存圖片的路徑
        self.string_tips = '雙擊下方目錄，選擇所要識別的支票(*.jpg,*.png,*.JPG)'  # 提示資料
        self.account = ""
        self.num_amount = ""
        self.chi_amount = ""
        self.check_account = ""
        self.check_date=""
        self.Pic = cv2.imread('icon/check_sample.jpg')
        self.fileName = ""
        self.filePath = ""
        self.txt = None
        self.threads_batch = Thread_batch(self.pic_list)#不能刪
        self.info=[]
        self._excel = pd.DataFrame(columns =['路徑','名稱','支票號碼','賬號','漢字金額','數字金額','日期'])
        self.init_ui()

    def init_ui(self):
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
            #top_left_button::hover{
                background-color:rgb(176,196,222); color:black;}
            #top_widget{
                background-color:rgb(54, 54, 54);
                border-top:1px darkGray;border-bottom:1px darkGray;
                border-right:1px darkGray;border-left:1px darkGray;
                border-top-left-radius:15px;border-top-right-radius:15px;}
            #bottomleft_widget{
                background:gray;}
            #bottomright_widget{
                background:white;border-radius:15px;}
            #bottom_widget{
                background:gray;
                border-bottom:1px darkGray;
                border-left:1px darkGray;border-right:1px darkGray;
                border-bottom-right-radius:15px;border-bottom-left-radius:15px;}  
            #chi_text_edit{
                background:rgb(248,248,255);font-size:18px;
                border:1px solid gray;width:300px;
                border-radius:10px;padding:2px 4px;font-weight:600;}
            #num_text_edit{
                background:rgb(248,248,255);font-size:20px;
                border:1px solid gray;width:300px;
                border-radius:10px;padding:2px 4px;font-weight:600;}
            #label_edit{
                color:rgb(0,0,0);font-size:24px;font-weight:700;}
            #title_label{
                color:rgb(255,255,255);font-size:35px;font-weight:bold;}
            #Output_label{
                color:rgb(255,255,255);
                border:none;border-bottom:1px solid white;
                font-size:30px;font-weight:700;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;}
            #radio_button{
                color:rgb(0,0,0);font-size:18px;font-weight:500;}
            #func_bt{
               background-color:#FFFFFF;border:none;border-radius:7px;
               font-size:25px;font-weight:700;}
            #func_bt::hover{
                background-color:rgb(176,196,222); color:black;}
            #tipEdit{
                border-top-left-radius:15px;border-bottom-left-radius:15px;}
            #treeView{
                border-bottom-left-radius:15px;border-bottom-right-radius:15px;}}          
        ''')
        self.setGeometry(50, 200, 1280, 500)
        self.setWindowTitle('CheckRecognition')
        self.setWindowIcon(QIcon('icon/control.png'))
        self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明

        '''左上按鈕'''
        self.top_back = QPushButton("注銷", self)
        self.top_back.setObjectName('top_left_button')
        self.top_back.setFixedSize(80, 30)
        self.top_pushout = QPushButton("匯出", self)
        self.top_pushout.setObjectName('top_left_button')
        self.top_pushout.setFixedSize(80, 30)
        self.top_restart = QPushButton("重置", self)
        self.top_restart.setObjectName('top_left_button')
        self.top_restart.setFixedSize(80, 30)

        '''文字輸出'''
        self.Output_label = QLabel('輸出結果')
        self.Output_label.setObjectName('Output_label')
        self.Control_label = QLabel('控制臺')
        self.Control_label.setObjectName('Output_label')

        self.CAmount_label = QLabel('金額(中文):')  # 中文金額
        self.CAmount_label.setObjectName('label_edit')
        self.CAmount_text = QTextEdit()  # 中文金額
        self.CAmount_text.setObjectName('chi_text_edit')
        self.CAmount_text.setFixedWidth(230)
        self.CAmount_text.setFixedHeight(50)

        self.Amount_label = QLabel('金額(數字):')  # 數字金額
        self.Amount_label.setObjectName('label_edit')
        self.Amount_text = QTextEdit()  # 數字金額
        self.Amount_text.setObjectName('num_text_edit')
        self.Amount_text.setFixedWidth(230)
        self.Amount_text.setFixedHeight(50)

        self.Bank_label = QLabel('支票號碼:')  # 支票號碼
        self.Bank_label.setObjectName('label_edit')
        self.Bank_text = QTextEdit()
        self.Bank_text.setObjectName('num_text_edit')
        self.Bank_text.setFixedWidth(230)
        self.Bank_text.setFixedHeight(50)

        self.Account_label = QLabel('支票賬戶:')  # 賬戶
        self.Account_label.setObjectName('label_edit')
        self.Account_text = QTextEdit()  # 數字金額
        self.Account_text.setObjectName('num_text_edit')
        self.Account_text.setFixedWidth(230)
        self.Account_text.setFixedHeight(50)

        self.Date_label = QLabel('日期:')  # 日期
        self.Date_label.setObjectName('label_edit')
        self.Date_text = QTextEdit()  # 日期
        self.Date_text.setObjectName('chi_text_edit')
        self.Date_text.setFixedWidth(230)
        self.Date_text.setFixedHeight(50)

        '''定義提示框部件'''
        self.textEdit = QTextEdit()
        self.textEdit.setFixedSize(200, 250)  # 窗口大小
        self.textEdit.setObjectName('tipEdit')
        self.textEdit.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.textEdit.setText(self.string_tips)
        self.textEdit.setReadOnly(True)  # 设置为只读，即可以在代码中向textEdit里面输入，但不能从界面上输入,没有这行代码即可以从界面输入

        '''定义創建Tree部件'''
        self.model = QFileSystemModel()
        print(QDir.currentPath())
        self.model.setRootPath(QDir.currentPath())
        self.treeView = QTreeView(self)
        self.treeView.setObjectName('treeView')
        self.treeView.setFixedSize(200,310)
        self.treeView.setModel(self.model)
        self.treeView.setColumnWidth(0, 400)  # 欄位寬度，一定要放在setModel()後面
        for col in range(1, 4):
            self.treeView.setColumnHidden(col, True)

        '''圖片部件'''
        self.ori_label = QLabel('支票顯示區域')
        self.ori_label.setFrameShape(QFrame.Box)
        self.ori_label.setObjectName('ori_label')
        self.ori_label.setFrameShadow(QFrame.Raised)  # 設置陰影，只有加了這步才能設置邊框顔色
        self.ori_label.setLineWidth(1)
        self.ori_label.setFixedSize(960, 480)
        self.ori_label.setAlignment(Qt.AlignCenter)
        self.ori_label.setPixmap( QPixmap("icon/image.png").scaled(200,200))  # 設置圖片的顯示

        '''路徑部件'''
        self.path_label = QLabel('路徑:')
        self.path_label.setFrameShape(QFrame.Box)  # 邊框樣式
        self.path_label.setFrameShadow(QFrame.Plain)  # 邊框樣式
        self.path_label.setObjectName('path_label')
        self.path_label.setStyleSheet("QLabel{border:2px groove gray;border-radius:10px;padding:2px 4px;}")
        self.path_label.setFixedSize(960, 30)  # 窗口大小

        '''Radio部件'''
        self.rbtn1 = QRadioButton('單張辨識')
        self.rbtn1.setObjectName('radio_button')
        self.rbtn2 = QRadioButton('批量辨識')
        self.rbtn2.setObjectName('radio_button')
        self.btngroup1 = QButtonGroup()
        self.btngroup1.addButton(self.rbtn1,1)
        self.btngroup1.addButton(self.rbtn2,2)

        '''右上按鈕'''
        self.title = QLabel("支票自動識別系統", self)
        self.title.setObjectName('title_label')
        self.smallscreen = QPushButton("-", self)
        self.smallscreen.setObjectName('top_right1_button')
        self.quitscreen = QPushButton("X", self)
        self.quitscreen.setObjectName('top_right2_button')
        self.smallscreen.setFixedSize(30, 30)
        self.quitscreen.setFixedSize(30, 30)

        '''功能按鈕'''
        self.start_bt = QPushButton('開始識別', self)
        self.start_bt.setObjectName('func_bt')
        self.start_bt.setFixedSize(120, 50)
        self.open_bt = QPushButton('選擇文件', self)
        self.open_bt.setObjectName('func_bt')
        self.open_bt.setFixedSize(120, 50)
        self.save_bt = QPushButton('保存信息', self)
        self.save_bt.setObjectName('func_bt')
        self.save_bt.setFixedSize(120, 50)

        '''主佈局'''
        self.main_widget = QWidget()
        self.main_widget.setObjectName('main_widget')
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)

        '''顶部布局'''
        self.top_widget = QWidget()
        self.top_widget.setObjectName('top_widget')
        self.top_layout = QHBoxLayout()
        self.top_layout.setAlignment(Qt.AlignTop)
        self.top_layout.setObjectName('top_layout')
        self.top_widget.setLayout(self.top_layout)

        '''底部左側佈局'''
        self.bottomleft_widget = QWidget()
        self.bottomleft_widget.setObjectName('bottomleft_widget')
        self.bottomleft_layout = QVBoxLayout()
        self.bottomleft_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.bottomleft_layout.setObjectName('bottom_layout')
        self.bottomleft_widget.setLayout(self.bottomleft_layout)

        '''底部右侧佈局'''
        self.bottomright_widget = QWidget()
        self.bottomright_widget.setObjectName('bottomright_widget')
        self.bottomright_layout = QHBoxLayout()
        self.bottomright_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.bottomright_layout.setObjectName('bottomright_layout')
        self.bottomright_widget.setLayout(self.bottomright_layout)

        '''添加頂部部件'''
        self.top_layout.addWidget(self.top_back)
        self.top_layout.addWidget(self.top_pushout)
        self.top_layout.addWidget(self.top_restart)
        self.top_layout.addStretch(2)
        self.top_layout.addWidget(self.title)
        self.top_layout.addStretch(2)
        self.top_layout.addWidget(self.smallscreen)
        self.top_layout.addWidget(self.quitscreen)
        self.top_layout.setAlignment(Qt.AlignTop|Qt.AlignCenter)

        '''添加左侧部件'''
        self.left1_box = QHBoxLayout()
        self.left2_box = QHBoxLayout()
        self.left3_box = QHBoxLayout()
        self.left4_box = QHBoxLayout()
        self.left5_box = QHBoxLayout()
        self.left6_box = QHBoxLayout()
        self.left7_box = QHBoxLayout()
        self.left8_box = QHBoxLayout()
        self.left9_box = QHBoxLayout()
        self.left10_box = QHBoxLayout()
        self.left11_box = QHBoxLayout()
        self.left5_box.addWidget(self.Output_label, 0, Qt.AlignCenter)
        self.left1_box.addWidget(self.CAmount_label,0,Qt.AlignLeft)
        self.left1_box.addWidget(self.CAmount_text,0,Qt.AlignLeft|Qt.AlignTop)
        self.left2_box.addWidget(self.Bank_label,0,Qt.AlignLeft)
        self.left2_box.addWidget(self.Bank_text,0,Qt.AlignLeft|Qt.AlignTop)
        self.left3_box.addWidget(self.Amount_label,0,Qt.AlignLeft)
        self.left3_box.addWidget(self.Amount_text,0,Qt.AlignLeft|Qt.AlignTop)
        self.left4_box.addWidget(self.Account_label,0,Qt.AlignLeft)
        self.left4_box.addWidget(self.Account_text,0,Qt.AlignLeft|Qt.AlignTop)
        self.left11_box.addWidget(self.Date_label,0,Qt.AlignLeft)
        self.left11_box.addWidget(self.Date_text, 0, Qt.AlignLeft | Qt.AlignTop)
        self.left9_box.addWidget(self.Control_label, 0, Qt.AlignCenter)
        self.left6_box.addStretch(2)
        self.left6_box.addWidget(self.rbtn1,0,Qt.AlignCenter)
        self.left6_box.addStretch(1)
        self.left6_box.addWidget(self.rbtn2,0, Qt.AlignCenter)
        self.left6_box.addStretch(2)
        self.left7_box.addWidget(self.start_bt,0,Qt.AlignCenter)
        self.left8_box.addWidget(self.open_bt, 0, Qt.AlignCenter)
        self.left10_box.addWidget(self.save_bt, 0, Qt.AlignCenter)
        self.bottomleft_layout.addLayout(self.left5_box)
        self.bottomleft_layout.addStretch(1)
        self.bottomleft_layout.addLayout(self.left1_box)
        self.bottomleft_layout.addLayout(self.left2_box)
        self.bottomleft_layout.addLayout(self.left3_box)
        self.bottomleft_layout.addLayout(self.left4_box)
        self.bottomleft_layout.addLayout(self.left11_box)
        self.bottomleft_layout.addStretch(1)
        self.bottomleft_layout.addLayout(self.left9_box)
        self.bottomleft_layout.addStretch(1)
        self.bottomleft_layout.addLayout(self.left6_box)
        self.bottomleft_layout.addLayout(self.left7_box)
        self.bottomleft_layout.addLayout(self.left8_box)
        self.bottomleft_layout.addLayout(self.left10_box)
        self.bottomleft_layout.addStretch(1)

        '''添加右侧部件'''
        self.mid_box = QVBoxLayout()
        self.right_box = QVBoxLayout()
        self.mid_box.addWidget(self.textEdit)
        self.mid_box.addWidget(self.treeView)
        self.right_box.addWidget(self.ori_label)
        self.right_box.addWidget(self.path_label)
        self.bottomright_layout.addLayout(self.mid_box)
        self.bottomright_layout.addLayout(self.right_box)

        '''底部总佈局'''
        self.bottom_widget = QWidget()
        self.bottom_widget.setObjectName('bottom_widget')
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setAlignment(Qt.AlignTop)
        self.bottom_layout.setObjectName('bottom_layout')
        self.bottom_layout.addWidget(self.bottomleft_widget)
        self.bottom_layout.addWidget(self.bottomright_widget)
        self.bottom_widget.setLayout(self.bottom_layout)

        '''主佈局添加'''
        self.main_layout.addWidget(self.top_widget)
        self.main_layout.addWidget(self.bottom_widget)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.top_pushout.setEnabled(False)
        self.start_bt.setEnabled(False)
        self.open_bt.setEnabled(False)
        self.rbtn1.setChecked(True)
        self.save_bt.setEnabled(False)

        '''按鈕事件'''
        self.smallscreen.clicked.connect(self.minium_Windows)
        self.quitscreen.clicked.connect(self.close_Windows)
        self.top_back.clicked.connect(self.back_Load)
        self.btngroup1.buttonClicked.connect(self.rbt_Clicked)
        self.treeView.doubleClicked.connect(self.open_Pic)
        self.start_bt.clicked.connect(self.start)
        self.top_restart.clicked.connect(self.reset)
        self.open_bt.clicked.connect(self.open_file)
        self.save_bt.clicked.connect(self.save_file)
        self.top_pushout.clicked.connect(self.out_file)

    '''選擇單張辨識還是批量辨識'''
    def rbt_Clicked(self):
        sender = self.sender()
        if sender == self.btngroup1:
            if self.btngroup1.checkedId() == 1 :
                self.textEdit.append('---------------')
                self.textEdit.append('已選擇單張識別模式')
                self.flag_batch=False
                self.start_bt.setEnabled(False)
                self.open_bt.setEnabled(False)
                self.treeView.setEnabled(True)
                self.save_bt.setEnabled(False)
            elif  self.btngroup1.checkedId() == 2 :
                self.re_flag = 2
                self.flag_batch =True
                self.textEdit.append('---------------')
                self.textEdit.append('已選擇多張識別模式')
                self.open_bt.setEnabled(True)
                self.start_bt.setEnabled(False)
                self.treeView.setEnabled(False)
                self.save_bt.setEnabled(False)

    '''打開支票圖片路徑'''
    def open_Pic(self, Qmodelidx):
        self.pic_list.clear()
        self.save_bt.setEnabled(False)
        self.Account_text.setText("")
        self.Bank_text.setText("")
        self.CAmount_text.setText("")
        self.Amount_text.setText("")
        self.Date_text.setText("")
        self.filePath = self.model.filePath(Qmodelidx)#獲取圖像路徑
        self.fileName = self.model.fileName(Qmodelidx)#獲取圖像名稱
        if self.filePath != None and self.fileName != 0:
            if self.fileName[-3:] == 'jpg' or self.fileName[-3:] == 'JPG' or self.fileName[-3:] == 'png':
                self.pic_list.append(self.filePath)
                self.path_label.setText(self.filePath)
                self.Pic = cv2.imread(self.filePath)
                self.start_bt.setEnabled(True)
                self.Pic_refreshShow()
                self.textEdit.append('---------------')
                self.textEdit.append('打開成功，準備識別！')
            else:
                self.textEdit.append('---------------')
                self.textEdit.append('請選擇圖片檔！')
        else:
            self.textEdit.append('---------------')
            self.path_label.setText("路劲错误！")

    '''圖像展示'''
    def Pic_refreshShow(self):
        height, width, channel = self.Pic.shape
        bytesPerline = 3 * width
        self.qImg = QImage(self.Pic, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        self.ori_label.setPixmap(QPixmap.fromImage(self.qImg).scaled(QSize(960, 480)))
        self.ori_label.setAlignment(Qt.AlignCenter)

    '''打開文件夾'''
    def open_file(self):
        self.save_bt.setEnabled(False)
        self.pic_list.clear()
        dir_choose = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      self.cwd)
        if dir_choose == "":
            self.textEdit.append('---------------')
            self.textEdit.append('選擇失敗')
            self.start_bt.setEnabled(False)
        else:
            self.textEdit.append('---------------')
            self.textEdit.append('您選擇的路徑為：')
            self.textEdit.append(dir_choose)
            img_file=glob.glob(dir_choose+'/*.[jpg][png][JPG]')
            num=0
            for img_path in img_file:
                if img_path != None:
                    filename = img_path.split('\\')[-1].split('.')[-1]
                    if filename == 'jpg' or filename == 'JPG' or filename == 'png' or filename == 'PNG':
                        num+=1
                        self.pic_list.append(img_path)
                        self.textEdit.append(img_path.split('\\')[-1])
            self.textEdit.append('---------------')
            self.textEdit.append('共發現{}張圖片。準備開始批量識別'.format(str(num)))
            self.ori_label.setPixmap(QPixmap("icon/image.png").scaled(200, 200))
            self.flag_list =True
            self.start_bt.setEnabled(True)
        self.Account_text.setText("")
        self.Date_text.setText("")
        self.Bank_text.setText("")
        self.CAmount_text.setText("")
        self.Amount_text.setText("")
        self.path_label.clear()
        self.open_bt.setEnabled(True)

    '''開始辨識動作'''
    def start(self):
        if self.flag_batch == False:#單張辨識
            if self.filePath != None and self.fileName != None:
                self.treeView.setEnabled(False)
                self.start_bt.setEnabled(False)
                self.open_bt.setEnabled(False)
                self.top_back.setEnabled(False)
                self.top_pushout.setEnabled(False)
                self.rbtn1.setEnabled(False)
                self.rbtn2.setEnabled(False)
                self.threads = Thread(self.Pic)
                self.textEdit.append('---------------')
                self.textEdit.append('識別中。。。。')
                self.threads._signal.connect(self.set_content)
                self.threads.start()
        else:#批量辨識
            self.treeView.setEnabled(False)
            self.start_bt.setEnabled(False)
            self.open_bt.setEnabled(False)
            self.top_back.setEnabled(False)
            self.top_pushout.setEnabled(False)
            self.rbtn1.setEnabled(False)
            self.rbtn2.setEnabled(False)
            self.threads_batch = Thread_batch(self.pic_list)
            self.threads_batch._startsignal.connect(self.set_content_batch)
            self.threads_batch._stopsignal.connect(self.stop_threads_batch)
            self.threads_batch._finishsignal.connect(self.finish_threads_batch)
            self.threads_batch.start()

    '''結束批量辨識'''
    def finish_threads_batch(self):
        self.open_bt.setEnabled(True)
        self.start_bt.setEnabled(False)
        self.treeView.setEnabled(True)
        self.top_back.setEnabled(True)
       # self.top_pushout.setEnabled(True)
        self.save_bt.setEnabled(True)
        self.rbtn1.setEnabled(True)
        self.rbtn2.setEnabled(True)
        self.textEdit.append('---------------')
        self.textEdit.append('全部識別完成！')

    '''中斷批量辨識'''
    def stop_threads_batch(self):
        self.threads_batch.quit()
        self.threads_batch.wait()
        self.start_bt.setEnabled(True)
        self.treeView.setEnabled(True)
        self.top_back.setEnabled(True)
       # self.top_pushout.setEnabled(True)
        self.save_bt.setEnabled(True)
        self.rbtn1.setEnabled(True)
        self.rbtn2.setEnabled(True)

    '''獲取單張辨識結果'''
    def set_content(self,check, account, num_amount, chi_amount, check_account,check_date):
        height, width, channel =check.shape
        bytesPerline = 3 * width
        self.qImg = QImage(check, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        self.ori_label.setPixmap(QPixmap.fromImage(self.qImg).scaled(QSize(960, 480)))
        self.ori_label.setAlignment(Qt.AlignCenter)
        self.account = account
        self.num_amount = num_amount
        self.chi_amount = chi_amount
        self.check_account =check_account
        self.check_date=check_date
        self.Account_text.setText(self.account)
        self.Bank_text.setText(self.check_account)
        self.CAmount_text.setText(self.chi_amount)
        self.Amount_text.setText( self.num_amount)
        self.Date_text.setText(self.check_date)
        self.textEdit.append('---------------')
        self.textEdit.append('識別完成！')
        self.textEdit.append('點擊保存')
        QApplication.processEvents()
        self.start_bt.setEnabled(True)
        self.treeView.setEnabled(True)
        self.top_back.setEnabled(True)
       # self.top_pushout.setEnabled(True)
        self.save_bt.setEnabled(True)
        self.rbtn1.setEnabled(True)
        self.rbtn2.setEnabled(True)

    '''獲取單張辨識結果'''
    def set_content_batch(self, check, account, num_amount, chi_amount, check_account,check_date,num):
        height, width, channel = check.shape
        bytesPerline = 3 * width
        self.qImg = QImage(check, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        self.ori_label.setPixmap(QPixmap.fromImage(self.qImg).scaled(QSize(960, 480)))
        self.ori_label.setAlignment(Qt.AlignCenter)
        self.account = str(account)
        self.num_amount = str(num_amount)
        self.chi_amount = str(chi_amount)
        self.check_account = str(check_account)
        self.check_date = str(check_date)
        self.info.append([check_account, account, chi_amount,num_amount,check_date])
        self.Account_text.setText(self.account)
        self.Bank_text.setText(self.check_account)
        self.CAmount_text.setText(self.chi_amount)
        self.Amount_text.setText(self.num_amount)
        self.Date_text.setText(self.check_date)
        self.textEdit.append('---------------')
        self.textEdit.append('第{}張識別完成'.format(str(num)))
        QApplication.processEvents()
        time.sleep(1)

    '''保存支票信息到後臺'''
    def save_file(self):
        if len(self.pic_list)==1:
            self._excel.loc[len(self._excel)] = [self.pic_list[0].rsplit('/',1)[0],self.pic_list[0].rsplit('/',1)[1],
                                                 self.check_account,self.account,self.chi_amount,self.num_amount,self.check_date]

        else:
            for i in range(len(self.pic_list)):
                pathlist=self.pic_list[i].split('\\')
                self._excel.loc[len(self._excel)] = [pathlist[0],pathlist[1],self.info[i][0],self.info[i][1],
                                                     self.info[i][2],self.info[i][3],self.info[i][4]]
        self.textEdit.append('---------------')
        self.save_bt.setEnabled(False)
        self.top_pushout.setEnabled(True)
        self.textEdit.append('保存成功')
        print(self._excel)

    '''輸出信息，保存成excel'''
    def out_file(self):
        pandas.io.formats.excel.header_style = None
        localtime =time.strftime("%H%M%S")
        writer = pd.ExcelWriter("{}.xlsx".format(str(localtime)))
        self._excel.to_excel(writer, 'Sheet1',encoding="utf_8_sig")
        writer.save()
        writer.close()
        self.reset()
        self.textEdit.append('---------------')
        self.textEdit.append('已匯出')

    '''重置excel'''
    def reset_excel(self):
        for i in range(len(self._excel)):
            self._excel=self._excel.drop(index=i)

    '''重置整個系統'''
    def reset(self):
        self.threads_batch.stop()
        self.rbtn1.setChecked(True)
        self.save_bt.setEnabled(False)
        self.top_pushout.setEnabled(False)
        self.start_bt.setEnabled(False)
        self.open_bt.setEnabled(False)
        self.rbtn1.setChecked(True)
        self.treeView.setEnabled(True)
        self.pic_list = []
        self.ori_label.setPixmap(QPixmap("icon/image.png").scaled(200, 200))
        self.flag_batch = False
        self.Pic = cv2.imread('icon/check_sample.jpg')
        self.fileName = ""
        self.filePath = ""
        self.txt = None
        self.path_label.setText("路徑:")
        self.Account_text.setText("")
        self.Date_text.setText("")
        self.Bank_text.setText("")
        self.CAmount_text.setText("")
        self.Amount_text.setText("")
        self.textEdit.clear()
        self.textEdit.setText(self.string_tips)
        self.reset_excel()



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

    @pyqtSlot()
    def back_Load(self):
        from RecognitionLoad import loadWin
        self.load_win = loadWin()
        self.load_win.show()
        self.close()




if __name__ == '__main__':
    a = QApplication(sys.argv)
    w = recWin()
    w.show()
    sys.exit(a.exec_())