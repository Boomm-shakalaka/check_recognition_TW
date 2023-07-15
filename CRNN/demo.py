import cv2
def script_method(fn, _rcb=None):
    return fn
def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj
import torch.jit
script_method1 = torch.jit.script_method
script1 = torch.jit.script
torch.jit.script_method = script_method
torch.jit.script = script
import torch
from torch.autograd import Variable
from CRNN import utils
from CRNN import dataset
from PIL import Image
import collections
from CRNN.models import crnn
def crnn_ocr2(model_path,img,alphabet):
    nclass = len(alphabet) + 1
    model = crnn.CRNN(32, 1, nclass, 256)  # model = crnn.CRNN(32, 1, 37, 256)
    #選擇設備，是否用GPU
    if torch.cuda.is_available():
        model = model.cuda()
        load_model_ = torch.load(model_path)
    else:
        load_model_ = torch.load(model_path,map_location='cpu')

    state_dict_rename = collections.OrderedDict()
    for k, v in load_model_.items():
        name = k[7:]  # remove `module.`
        state_dict_rename[name] = v

    #加載模型
    model.load_state_dict(state_dict_rename)
    #創建轉換器，用於將ctc生成的路徑轉換成最終序列，讀入的alphabet的索引，最後輸出再轉換成字符
    converter = utils.strLabelConverter(alphabet)
    #圖像大小轉換
    transformer = dataset.resizeNormalize((100, 32))
    #讀入圖片，轉成灰度圖
    image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert('L')
    # 圖像大小轉換
    image = transformer(image)
    if torch.cuda.is_available():
        image = image.cuda()
    image = image.view(1, *image.size())# (1,1,32,100)
    #image = Variable(image)
    model.eval()
    preds = model(image)   #(time_step,batch_size,nclass)
    #print(preds)#輸出所有的置信度
    _, preds = preds.max(2)#(time_step,batch_size,nclass),nclass最大的,_是值
    preds = preds.transpose(1, 0).contiguous().view(-1)#轉換成索引列表
    #preds_size = Variable(torch.IntTensor([preds.size(0)]))
    #轉換成字符序列
    preds_size = torch.IntTensor([preds.size(0)])
    raw_pred = converter.decode(preds.data, preds_size.data, raw=True)#不經過CTC
    sim_pred = converter.decode(preds.data, preds_size.data, raw=False)
    print('%-20s => %-20s' % (raw_pred, sim_pred))
    return sim_pred
