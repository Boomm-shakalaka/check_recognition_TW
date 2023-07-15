import os
import cv2
from CTPN.main.demo import text_detect
from MICR.bank_check_ocr_2 import micr_ocr
from CRNN.demo import crnn_ocr2
class Check_recognition:
    def __init__(self,check):
        #使用CPU
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        # 使用GPU
        #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
        #sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        self.check = check
        self.ctpn_path='CTPN_model/checkpoints_mlt/'#
        self.micr_path = 'MICR_model/micr_reference.png'
        self.crnn_number_model = 'CRNN_model/netCRNN_number.pth'
        self.crnn_capitalnum_model = 'CRNN_model/netCRNN_chi.pth'
        self.crnn_datenum_model = 'CRNN_model/netCRNN_date.pth'
        self.chi_alphabet = '零壹貳叁肆伍陸柒捌玖拾佰仟萬億整元'
        self.alphabet = '0123456789'
        self.date_alphabet = '中華民國年月日0123456789'

    def rec_(self):
        micr_reference=cv2.imread(self.micr_path)
        self.check=cv2.resize(self.check,(1300,600))
        account_pos=self.check[20:74,853:1080]#賬戶位置
        check_pos=self.check[75:110,882:1080]#支票賬號位置
        chi_pos=self.check[150:220,320:1100]#大寫數字位置
        date_pos = self.check[110:145, 815:1090]#日期位置
        boxes=text_detect(chi_pos,self.ctpn_path)#CTPN獲取識別區域
        x1,y1,x2,y2,x3,y3,x4,y4=0,0,0,0,0,0,0,0
        for i, box in enumerate(boxes):
            x1, y1 = box[0], box[1]
            #x2, y2 = box[2], box[3]
            x3, y3 = box[4], box[5]
            #x4, y4 = box[6], box[7]
        if x1 == 0 and y1 == 0 and x3 == 0 and x4 == 0:
            self.chi_amount = "無内容"
        else:
            chi_pos = self.check[y1 + 150:y3 + 150, x1 + 320:x3 + 320]#獲取大寫數字位置
            self.chi_amount = crnn_ocr2(self.crnn_capitalnum_model, chi_pos, self.chi_alphabet)#CRNN辨識大寫數字
            self.check = cv2.rectangle(self.check, (x1 + 320, y1 + 150), (x3 + 320, y3 + 150), (0, 0, 255),2)
        self.account = crnn_ocr2(self.crnn_number_model, account_pos, self.alphabet)#辨識賬戶金額
        self.check_account = crnn_ocr2(self.crnn_number_model, check_pos, self.alphabet)#辨識支票賬號金額
        self.check_date = crnn_ocr2(self.crnn_datenum_model, date_pos, self.date_alphabet)#辨識日期
        if self.check_date=='':
            self.check_date='無法識別'
        else:
            self.check=cv2.rectangle(self.check, (815, 110), (1090, 145), (0, 0, 255), 2)
        if self.account=='':
            self.account='無法識別'
        else:
            self.check = cv2.rectangle(self.check, (853, 20), (1080, 74), (0, 0, 255), 2)
        if self.check_account=='':
            self.check_account='無法識別'
        else:
            self.check = cv2.rectangle(self.check, (882, 75), (1080, 110), (0, 0, 255), 2)
        self.check, self.num_amount = micr_ocr(micr_reference, self.check)
        if len(self.num_amount)==0:
            self.num_amount='無法識別'
        else:
            self.num_amount=self.num_amount[-1]
            self.num_amount=''.join(filter(str.isdigit, self.num_amount))#MICR處理
            for i in range(len(self.num_amount)):
                if int(self.num_amount[i])!=0:
                    self.num_amount=self.num_amount[i:]
                    break
        return self.check,self.account, self.check_account,self.chi_amount,self.num_amount,self.check_date


# if __name__ == '__main__':
#     check=cv2.imread('1-20/5.png')
#     t1=Check_recognition(check)
#     x1,x2,x3,x4,x5,x6=t1.rec_()
#     print(x5,x2,x3,x4,x6)