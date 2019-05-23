# -*-coding:utf-8 -*-
import random
import time

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# i代表的是index，测试定位准确率的时候传入：dx_crawler.py
# for i in range(0, 100):
#     match.match_1("all_type/dx/", 'all_type/dx/bg/target' + str(i) + '.jpg',
#                   'all_type/dx/blk/template' + str(i) + '.png', str(i),
#                   "demo")
# def match_1(parentdir, targetimg, templateimg, i, _type='demo'):
import demo


def match_1(parentdir, targetimg, templateimg, _type='demo'):
    """
    :param parentdir:
    :param targetimg: path of the bg image
    :param templateimg: path of the slide block
    :param _type:
    :return: distance
    """
    """
        flags = -1：imread按解码得到的方式读入图像
        flags = 0：imread按单通道的方式读入图像，即灰白图像
        flags = 1：imread按三通道方式读入图像，即彩色图像
    """
    # rgb
    img_rgb = cv2.imread(targetimg, 1)
    # gray
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    temp_gray = cv2.imread(templateimg, 0)
    temp_gray_path = parentdir + 'temp_gray_' + _type + '.png'
    cv2.imwrite(temp_gray_path, temp_gray)

    import utils
    reverseimg = parentdir + 'temp_reverse_' + _type + '.png'
    utils.denoise2(templateimg, 15, reverseimg)
    # gray
    template = cv2.imread(templateimg, 0)
    w, h = template.shape[::-1]
    template = cv2.imread(reverseimg, 0)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    # result参数表示匹配结果图像，必须是单通道32位浮点。如果image的尺寸为W x H，
    # templ的尺寸为w x h，则result的尺寸为(W-w+1)x(H-h+1)。
    L = 0
    R = 1
    count = 0
    while count < 20:
        threshold = (L + R) / 2
        count += 1
        if threshold < 0:
            print('Error')
            return None
        # 返回的是数组的列表，如果是二维，则有两个数组，一个表示横行，意义是图片中的从坐标，一个表示纵列，表示图片中横坐标
        loc = np.where(res >= threshold)
        # 大于1说明匹配了多个目标模板，而我们只需要确定一个
        if len(loc[0]) > 1:
            L += (R - L) / 2
        elif len(loc[0]) == 1:
            pt = loc[::-1]
            print('目标区域的左上角坐标：', pt[0], pt[1])
            print('次数: ', count)
            print('阈值: ', threshold)
            break
        elif len(loc[0]) < 1:
            R -= (R - L) / 2

    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (34, 139, 34), 2)
    cv2.imshow('processed result', img_rgb)
    cv2.imshow('reverse template', template)
    # cv2.imwrite(parentdir + 'mark1/target' + i + _type + '.jpg', img_rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return pt[0][0]


# 和4的区别是不保存图像
def match_2(parentdir, targetimg, templateimg, _type='demo', denoise=True):
    """
    :param parentdir: the directory to save the image
    :param targetimg: target -> bg image
    :param templateimg: template -> block
    :param _type: demo or login or register
    :param denoise: True or False
    :return: distance to the left of the north
    """

    target = cv2.imread(targetimg, 0)
    template = cv2.imread(templateimg, 0)
    # image_arr_rgb.shape
    # (H, W, C)
    w, h = template.shape[::-1]
    temp = parentdir + 'temp_gray_' + _type + '.png'
    targ = parentdir + 'targ_gray_' + _type + '.jpg'
    cv2.imwrite(temp, template)
    cv2.imwrite(targ, target)
    template = cv2.imread(temp)
    target = cv2.imread(targ)
    if denoise:
        import utils
        noisename = parentdir + 'temp_denoise_' + _type + '.png'
        utils.denoise(temp, 15, noisename)
        # noisename = cv1.mean_blur(noisename)
        template = cv2.imread(noisename)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    # result.shape形状的矩阵，第result.argmax()个元素的展开的坐标，第一个参数是一种整数数组，其元素是维度数组dims的扁平版本的索引。
    # 例子：
    # Consider a (6,7,8) shape array, what is the index (x,y,z) of the 100th element ?
    # >>> print np.unravel_index(100,(6,7,8))
    # (1, 5, 4)

    # 解释：
    # 给定一个矩阵，shape=（6,7,8），即3维的矩阵，求第n个元素的下标是什么？矩阵各维的下标从0开始
    # 如果indices参数是一个标量，那么返回的是一个向量，维数=矩阵的维数，向量的值其实就是在矩阵中对应的下标。如6*7*8*9的矩阵，
    # 1621/(7*8*9)=3，(1621-3*7*8*9)/(8*9)=1，(1621-3*7*8*9-1*8*9)/9=4，(1621-3*7*8*9-1*8*9-4*9)=1。
    # 所以返回的向量为array(3,1,4,1)

    # 如果indices参数是一个向量的，那么通过该向量中值求出对应的下标。下标的个数就是矩阵的维数，每一维下标组成一个向量，
    # 所以返回的向量的个数=矩阵维数。如7*6的矩阵，第22个元素是 3*6+4，所以对应的下标是(3,4)，那么返回的值是 array([3]),array([4]
    # ---------------------
    # 原文：https://blog.csdn.net/dn_mug/article/details/70256109

    x, y = np.unravel_index(result.argmax(), result.shape)  # shape:(H,W)
    # 展示圈出来的区域
    cv2.rectangle(target, (y, x), (y + w, x + h), (7, 249, 151), 2)
    cv2.imshow('Show', target)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return y


# i是便于生成index的图像名称
# def match_3(parentdir, targetimg, templateimg, i, _type="demo", denoise=True):
def match_3(parentdir, targetimg, templateimg, _type="demo", denoise=True):
    """
    :param parentdir:
    :param _type: demo or login or regist
    :param denoise: True or False
    :param targetimg: path of the bg image
    :param templateimg: path of the slide block
    :return: distance
    """
    # 参考https://blog.csdn.net/weixin_42081389/article/details/87935735
    # a=np.array([[2,3,4,5],[5,6,78,9],[1,3,4,5]])
    # print(a)
    # # 函数功能：假设有一个矩阵a,现在需要求这个矩阵的最小值，最大值，并得到最大值，最小值的索引，注意是先x后y，先列之间距离，再横向行距。
    # min_val,max_val,min_indx,max_indx=cv2.minMaxLoc(a)
    # print(min_val,max_val,min_indx,max_indx)

    img = cv2.imread(targetimg, 0)
    # img2 = img.copy()
    template = cv2.imread(templateimg, 0)
    temp = parentdir + 'temp_gray_' + _type + '.png'
    targ = parentdir + 'targ_gray_' + _type + '.jpg'
    cv2.imwrite(targ, img)
    # cv2.imshow('messi', img)
    # cv2.imshow('face', template)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # 也可以写作： h, w = template.shape[:2]，因为shape是(H,W,C)
    w, h = template.shape[::-1]
    # All the 6 methods for comparison in a list
    # methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
    #            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

    # 这个要不要翻转颜色很关键，试试就知道
    # template = abs(255 - template)

    meth = 'cv2.TM_CCOEFF_NORMED'
    # img = img2.copy()
    '''
    exec可以用来执行储存在字符串文件中的python语句
    例如可以在运行时生成一个包含python代码的字符串
    然后使用exec语句执行这些语句
    eval语句用来计算存储在字符串中的有效python表达式
    '''
    cv2.imwrite(temp, template)
    target = cv2.imread(targ)
    template = cv2.imread(temp)
    method = eval(meth)
    if denoise:
        import utils
        noisename = parentdir + 'temp_denoise_' + _type + '.png'
        utils.denoise(temp, 15, noisename)
        # noisename = cv1.mean_blur(noisename)
        template = cv2.imread(noisename)
    # 匹配应用
    res = cv2.matchTemplate(target, template, method)
    # print(res)
    # print(np.array(res))
    # print("res.shape: ", res.shape)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # 使用不同的方法，对结果的解释不同
    # 方法判断
    # if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
    #     top_left = min_loc
    # else:
    #     top_left = max_loc

    # 最大值的坐标就是距离左边界和上边界的距离
    top_left = max_loc
    # print('偏移像素', top_left[0])

    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img, top_left, bottom_right, 255, 2)
    cv2.imshow('Show', img)
    plt.subplot(121), plt.imshow(res, cmap='gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(img, cmap='gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle('method: ' + meth)
    plt.savefig(parentdir + 'mark3/target_res.jpg')
    plt.show()
    # cv2.imwrite(parentdir + 'mark3/target' + i + _type + '.jpg', img)
    cv2.imwrite(parentdir + 'mark3/target' + _type + '.jpg', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return top_left[0]


def match_4(parentdir, targetimg, templateimg, _type, denoise=True):
    template = cv2.imread(templateimg, 0)
    target = cv2.imread(targetimg, 0)
    # 获取图像的长和宽
    w, h = template.shape[::-1]

    temp = parentdir + 'temp_gray_' + _type + '.png'
    targ = parentdir + 'targ_gray_' + _type + '.jpg'
    cv2.imwrite(temp, template)
    cv2.imwrite(targ, target)

    # template = abs(255 - template)
    # cv2.imwrite(temp, template)

    template = cv2.imread(temp)
    target = cv2.imread(targ)
    if denoise:
        import utils
        noisename = parentdir + 'temp_denoise_' + _type + '.png'
        # 15不错
        utils.denoise(temp, 18, noisename)
        # noisename = cv1.mean_blur(noisename)
        template = cv2.imread(noisename)

    # 模板匹配
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)

    t = cv2.imread(targetimg, 1)
    # 展示圈出来的区域
    cv2.rectangle(t, (y, x), (y + w, x + h), (0, 0, 255), 2)
    font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
    cv2.putText(t, 'notch 1.000', (y, x - 2), font, 0.4, (255, 0, 0), 1)
    # 图像，文字内容， 坐标 ，字体，大小，颜色，字体厚度
    # cv2.imshow('Show', t)
    cv2.imwrite(parentdir + 'targ_rect_' + _type + '.jpg', t)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return y


# 为了测试顶象的定位准确性
def match_4_for_crawler(parentdir, targetimg, templateimg, _type, i, denoise=True):
    template = cv2.imread(templateimg, 0)
    target = cv2.imread(targetimg, 0)
    # 获取图像的长和宽
    w, h = template.shape[::-1]

    temp = parentdir + 'temp_gray_' + _type + '.png'
    targ = parentdir + 'targ_gray_' + _type + '.jpg'
    cv2.imwrite(temp, template)
    cv2.imwrite(targ, target)

    # template = abs(255 - template)
    # cv2.imwrite(temp, template)

    template = cv2.imread(temp)
    target = cv2.imread(targ)
    if denoise:
        import utils
        noisename = parentdir + 'temp_denoise_' + _type + '.png'
        # 15不错
        utils.denoise(temp, 13, noisename)
        # noisename = cv1.mean_blur(noisename)
        template = cv2.imread(noisename)

    # 模板匹配
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)

    t = cv2.imread(targetimg, 1)
    # 展示圈出来的区域
    cv2.rectangle(t, (y, x), (y + w, x + h), (0, 0, 255), 2)
    font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
    cv2.putText(t, 'notch 1.000', (y, x - 2), font, 0.4, (255, 0, 0), 1)
    # 图像，文字内容， 坐标 ，字体，大小，颜色，字体厚度
    # cv2.imshow('Show', t)
    cv2.imwrite(parentdir + 'mark/target' + i + _type + '.jpg', t)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return y


# jy:模板匹配找到凹槽距离左边界位置，由于template左边自带5pixel距离，所以算出来的就是准的，不用减去初始距离，因为为0
def match_255(parentdir, target, template, _type):
    template = cv2.imread(template, 0)
    target = cv2.imread(target, 0)
    w, h = template.shape[::-1]
    temp = parentdir + 'temp_gray_' + _type + '.png'
    targ = parentdir + 'targ_gray_' + _type + '.jpg'
    cv2.imwrite(temp, template)
    cv2.imwrite(targ, target)
    # 255代表这个翻转，用在极验上定位准确率很高
    template = abs(255 - template)
    cv2.imwrite(temp, template)

    template = cv2.imread(temp)
    target = cv2.imread(targ)

    result = cv2.matchTemplate(template, target, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)
    # 展示圈出来的区域
    cv2.rectangle(target, (y, x), (y + w, x + h), (7, 249, 151), 2)
    cv2.imshow('Show', target)
    # 自动点击右上角叉号，关闭预览窗口
    # time.sleep(random.uniform(0.4, 1.2))
    # crack_tb.CrackTaobao().mouse_click(1380, 730)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return y


if __name__ == "__main__":
    # match_3('all_type/dx/', 'all_type/dx/target_demo.jpg', 'all_type/dx/template_demo.png', 'demo', True)
    # match_4('all_type/dx/', 'all_type/dx/target_regist.png', 'all_type/dx/template_regist.png', 'regist', True)
    # match_2('all_type/dx/', 'all_type/dx/target_regist.png', 'all_type/dx/template_regist.png', 'regist', True)
    match_1("all_type/dx/", 'all_type/dx/target_regist.png', 'all_type/dx/template_regist.png', 'regist')
