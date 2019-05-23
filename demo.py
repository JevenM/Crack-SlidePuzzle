#!/usr/bin/env python

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os, time

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from lib.config import config as cfg
from lib.utils.nms_wrapper import nms
from lib.utils.test import im_detect
# from nets.resnet_v1 import resnetv1
from lib.nets.vgg16 import vgg16
from lib.utils.timer import Timer

# 修改类别，我们只需要一个类别：notch
CLASSES = ('__background__',
           'notch')

# 将vgg16后面添加自己训练得到的模型名字，附加就行，然后
# tfmodel = os.path.join('output', demonet, DATASETS[dataset][0], 'default', NETS[demonet][1])
# 选的是vgg16_faster_rcnn_iter_20000.ckpt这个最为我最后测试的时候加载的模型，所以这个名字是固定的，也是我自己指定的，
# 因为是我设置最大20000轮，肯定要根据自己实际情况
NETS = {'vgg16': ('vgg16_faster_rcnn_iter_70000.ckpt', 'vgg16_faster_rcnn_iter_10000.ckpt',),
        'res101': ('res101_faster_rcnn_iter_110000.ckpt',)}
DATASETS = {'pascal_voc': ('voc_2007_trainval',), 'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}


def vis_detections(im, class_name, dets, image_name, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return
    _, w, h = im.shape[::-1]
    # BGR改为RGB
    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]
        print("distance: ", bbox[0])
        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=2)
        )
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=8, color='white')

    # ax.set_title(('{} detections with '
    #               'p({} | box) >= {:.1f}').format(class_name, class_name,
    #                                               thresh),
    #              fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    fig = plt.gcf()
    fig.set_size_inches(w / 100.0, h / 100.0)  # 输出width*height像素
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig('rect_' + image_name, format='png')
    # 原文：https: // blog.csdn.net / jifaley / article / details / 79687000
    plt.draw()
    plt.show()


def demo(sess, net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', image_name)
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

    # Visualize detections for each class
    CONF_THRESH = 0.1
    NMS_THRESH = 0.1
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1  # because we skipped background
        cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        vis_detections(im, cls, dets, image_name, thresh=CONF_THRESH)


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    # 这个的默认值是res101，我改为了vgg16，和上面对应
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='vgg16')
    # 下面的default原来是pascal_voc_0712我改为了pascal_voc，因为他对应的是voc_2007_trainval，我自己新建的文件夹也是这个名字，要对应上
    parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc_0712]',
                        choices=DATASETS.keys(), default='pascal_voc')
    args = parser.parse_args()

    return args


def faster_detect():
    '''
    定义一个函数：用来计算凹槽notch左边界的距离
    '''

    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = True

    # init session
    sess = tf.Session(config=tfconfig)
    # 固定死了，就用vgg16作为基础卷积网络
    net = vgg16(batch_size=1)
    net.create_architecture(sess, "TEST", 2,
                            tag='default', anchor_scales=[8, 16, 32])
    saver = tf.train.Saver()
    # 替换掉具体的名字，比如geetest
    # tfmodel = os.path.join('output', "vgg16", "voc_2007_trainval", 'default', 'geetest',
    # "vgg16_faster_rcnn_iter_20000.ckpt")
    tfmodel = os.path.join('output', "vgg16", "voc_2007_trainval", 'default', 'tencent',
                           "vgg16_faster_rcnn_iter_10000.ckpt")
    # 判断模型是否存在
    if not os.path.isfile(tfmodel + '.meta'):
        print(tfmodel)
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # 恢复模型
    saver.restore(sess, tfmodel)
    return sess, net


def demo_customize(sess, net, im_name):
    # Load the demo image
    im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', im_name)
    im = cv2.imread(im_file)
    h, w = im.shape[:2]
    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    # Visualize detections for each class
    CONF_THRESH = 0.5  # 自己修改了
    NMS_THRESH = 0.5  # 自己修改了
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1  # because we skipped background
        cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        inds = np.where(dets[:, -1] >= CONF_THRESH)[0]

        if len(inds) != 0:
            im = im[:, :, (2, 1, 0)]
            fig, ax = plt.subplots(figsize=(12, 12))
            ax.imshow(im, aspect='equal')
            for i in inds:
                bbox = dets[i, :4]
                score = dets[i, -1]
                print("demo_customize distance: ", bbox[0])
                ax.add_patch(
                    plt.Rectangle((bbox[0], bbox[1]),
                                  bbox[2] - bbox[0],
                                  bbox[3] - bbox[1], fill=False,
                                  edgecolor='red', linewidth=1))
                ax.text(bbox[0], bbox[1] - 2,
                        '{:s} {:.3f}'.format("", score),
                        bbox=dict(facecolor='blue', alpha=0.5),
                        fontsize=14, color='white')

            ax.set_title(('{} detections with '
                          'p({} | box) >= {:.1f}').format("", "", 0.5),
                         fontsize=14)

            plt.axis('off')
            plt.tight_layout()
            fig = plt.gcf()
            fig.set_size_inches(w / 100.0, h / 100.0)  # 输出width*height像素
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
            plt.margins(0, 0)
            plt.savefig('mark/' + im_name)
            # 原文：https: // blog.csdn.net / jifaley / article / details / 79687000
            # plt.draw()
            # plt.show()
            return bbox[0]  # 经过观察，xx个像素偏差


if __name__ == '__main__':
    # 解析命令行参数
    args = parse_args()

    # model path
    demonet = args.demo_net  # vgg16
    dataset = args.dataset  # pascal_voc

    # 这里就定义了，你应该把训练好的模型放在./output/vgg16/voc_2007_trainval/default/xxx/下面
    # tfmodel = os.path.join('output', demonet, DATASETS[dataset][0], 'default', 'geetest', NETS[demonet][1])
    tfmodel = os.path.join('output', demonet, DATASETS[dataset][0], 'default', 'tencent', NETS[demonet][1])

    # 判断模型是否存在
    if not os.path.isfile(tfmodel + '.meta'):
        print(tfmodel)
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = True

    # init session
    sess = tf.Session(config=tfconfig)
    # load network，用不起res101，GPU不行
    if demonet == 'vgg16':
        net = vgg16(batch_size=1)
    # elif demonet == 'res101':
    # net = resnetv1(batch_size=1, num_layers=101)
    else:
        raise NotImplementedError

    # 这里的2，原来是21，意思是具有多少个类别标签，由于我只有一个notch，所以加上保留的__background__，就是2啦
    net.create_architecture(sess, "TEST", 2,
                            tag='default', anchor_scales=[8, 16, 32])
    saver = tf.train.Saver()
    # 恢复模型
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))

    # 测试图片肯定也要改啊，将自己的图片找出来放在./data/demo/下面，我随便找了几张
    im_names = ["target.jpg"]
    for im_name in im_names:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Demo for data/demo/{}'.format(im_name))
        demo(sess, net, im_name)

    plt.show()
