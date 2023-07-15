# coding=utf-8
import os
import sys
import numpy as np
import tensorflow as tf
sys.path.append(os.getcwd())
from CTPN.nets import model_train as model
from CTPN.utils.rpn_msr.proposal_layer import proposal_layer
from CTPN.utils.text_connector.detectors import TextDetector
tf.app.flags.DEFINE_string('test_data_path', 'data/demo/', '')
tf.app.flags.DEFINE_string('output_path', 'data/res/', '')
tf.app.flags.DEFINE_string('gpu', '0', '')
tf.app.flags.DEFINE_string('checkpoint_path', 'checkpoints_mlt/', '')
FLAGS = tf.app.flags.FLAGS
def text_detect(image,checkpoint):
    tf.reset_default_graph()
    with tf.get_default_graph().as_default():
        input_image = tf.placeholder(tf.float32, shape=[None, None, None, 3], name='input_image')
        input_im_info = tf.placeholder(tf.float32, shape=[None, 3], name='input_im_info')
        global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)
        bbox_pred, cls_pred, cls_prob = model.model(input_image)
        variable_averages = tf.train.ExponentialMovingAverage(0.997, global_step)
        saver = tf.train.Saver(variable_averages.variables_to_restore())
        with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
            # 加載模型
            ckpt_state = tf.train.get_checkpoint_state(checkpoint)
            model_path = os.path.join(checkpoint, os.path.basename(ckpt_state.model_checkpoint_path))
            saver.restore(sess, model_path)
            # 預測文本框位置
            img = image
            h, w, c = img.shape
            im_info = np.array([h, w, c]).reshape([1, 3])
            bbox_pred_val, cls_prob_val = sess.run([bbox_pred, cls_prob],
                                                   feed_dict={input_image: [img],
                                                              input_im_info: im_info})
            textsegs, _ = proposal_layer(cls_prob_val, bbox_pred_val, im_info)
            scores = textsegs[:, 0]
            textsegs = textsegs[:, 1:5]
            textdetector = TextDetector(DETECT_MODE='H')
            boxes = textdetector.detect(textsegs, scores[:, np.newaxis], img.shape[:2])
            boxes = np.array(boxes, dtype=np.int)
    return boxes

if __name__ == '__main__':
    tf.app.run()
