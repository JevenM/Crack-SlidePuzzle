# -*- coding:utf-8 -*-
# coding=utf-8
import cv2
import numpy as np
from matplotlib import pyplot as plt


def handle(imgname, grayname):
    img = cv2.imread(imgname)  # 载入图像
    h, w = img.shape[:2]  # 获取图像的高和宽
    # cv2.imshow("Origin", img)  # 显示原始图像

    blured = cv2.blur(img, (5, 5))  # 进行滤波去掉噪声
    # cv2.imshow("Blur", blured)  # 显示低通滤波后的图像

    mask = np.zeros((h + 2, w + 2), np.uint8)  # 掩码长和宽都比输入图像多两个像素点，满水填充不会超出掩码的非零边缘
    # 进行泛洪填充
    cv2.floodFill(blured, mask, (w - 1, h - 1), (255, 255, 255), (2, 2, 2), (3, 3, 3), 8)
    # cv2.imshow("floodfill", blured)

    # 得到灰度图
    gray = cv2.cvtColor(blured, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray", gray)

    # 定义结构元素
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
    # 开闭运算，先开运算去除背景噪声，再继续闭运算填充目标内的孔洞
    opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow("closed", closed)

    # 求二值图
    ret, binary = cv2.threshold(closed, 250, 255, cv2.THRESH_BINARY)
    # cv2.imshow("binary", binary)

    # 找到轮廓
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 绘制轮廓

    cv2.drawContours(img, contours, -1, (0, 0, 255), 3)
    # 绘制结果
    # cv2.imshow("result", img)
    cv2.imwrite(grayname, img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def bilateral():
    img = cv2.imread('all_type/dx/temp_denoise_demo.png')
    '''
    函数 cv2.bilateralFilter() 能在保持边界清晰的情况下有效的去除噪音。
    但是这种操作与其他滤波器相比会比较慢。我们已经知道高斯滤波器是求
    中心点邻近区域像素的高斯加权平均值。这种高斯滤波器只考虑像素之间的空
    间关系，而不会考虑像素值之间的关系（像素的相似度）。所以这种方法不会考
    虑一个像素是否位于边界。因此边界也会别模糊掉，而这正不是我们想要。
    双边滤波在同时使用空间高斯权重和灰度值相似性高斯权重。空间高斯函
    数确保只有邻近区域的像素对中心点有影响，灰度值相似性高斯函数确保只有
    与中心像素灰度值相近的才会被用来做模糊运算。所以这种方法会确保边界不
    会被模糊掉，因为边界处的灰度值变化比较大。
    '''
    blur = cv2.bilateralFilter(img, 9, 75, 75)
    plt.subplot(121), plt.imshow(img), plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(blur), plt.title('Blurred')
    plt.xticks([]), plt.yticks([])
    plt.show()


def median():
    img = cv2.imread('all_type/dx/temp_denoise_demo.png')
    '''
    用与卷积框对应像素的中值来替代中心像素的值。
    这个滤波器经常用来去除椒盐噪声。
    前面的滤波器都是用计算得到的一个新值来取代中心像素的值，
    而中值滤波是用中心像素周围（也可以使他本身）的值来取代他。
    他能有效的去除噪声。卷积核的大小也应该是一个奇数。
    '''
    median = cv2.medianBlur(img, 5)
    plt.subplot(121), plt.imshow(img), plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(median), plt.title('Blurred')
    plt.xticks([]), plt.yticks([])
    plt.show()


def gaussian():
    img = cv2.imread('all_type/dx/temp_denoise_demo.png')
    # 0 是指根据窗口大小（5,5）来计算高斯函数标准差
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    plt.subplot(121), plt.imshow(img), plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(blur), plt.title('Blurred')
    plt.xticks([]), plt.yticks([])
    plt.show()


def mean_blur(imname='all_type/dx/temp_denoise_demo.png'):
    img = cv2.imread(imname)
    # 用卷积框覆盖区域所有像素的平均值来代替中心元素。
    blur = cv2.blur(img, (3, 3))
    cv2.imwrite(imname, blur)

    # plt.subplot(121), plt.imshow(img), plt.title('Original')
    # plt.xticks([]), plt.yticks([])
    # plt.subplot(122), plt.imshow(blur), plt.title('Blurred')
    # plt.xticks([]), plt.yticks([])
    # plt.show()
    return imname


def conv2d():
    img = cv2.imread('all_type/dx/temp_denoise_demo.png')
    # 低通滤波
    # 将核放在图像的一个像素 A 上，求与核对应的图像上 25（5x5）个像素的和，
    # 再取平均数，用这个平均数替代像素 A 的值。
    kernel = np.ones((5, 5), np.float32) / 25
    # cv.Filter2D(src, dst, kernel, anchor=(-1, -1))
    # ddepth – desired(期望) depth of the destination image;
    # if it is negative(负的,消极的), it will be the same as src.depth();
    # the following combinations of src.depth() and ddepth are supported:
    # src.depth() = CV_8U, ddepth = -1/CV_16S/CV_32F/CV_64F
    # src.depth() = CV_16U/CV_16S, ddepth = -1/CV_32F/CV_64F
    # src.depth() = CV_32F, ddepth = -1/CV_32F/CV_64F
    # src.depth() = CV_64F, ddepth = -1/CV_64F
    # when ddepth=-1, the output image will have the same depth as the source.
    dst = cv2.filter2D(img, -1, kernel)
    plt.subplot(121), plt.imshow(img), plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(dst), plt.title('Averaging')
    plt.xticks([]), plt.yticks([])
    plt.show()

# 以上参考 https://lhchen74.github.io/2019/02/26/opencv-filter/


# 以下参考 https://www.jianshu.com/p/4ae5e8cef9ae
def median_blur():
    img = cv2.imread('all_type/dx/temp_denoise_demo.png')

    # 用 np.hstack，将多个 均值平滑处理后的图像水平合并起来
    blured = np.hstack([
        # img, kernel, std
        cv2.medianBlur(img, 1),
        cv2.medianBlur(img, 3),
        cv2.medianBlur(img, 5)
    ])

    plt.figure(figsize=(10, 8))
    plt.imshow(blured[:, :, ::-1])
    plt.show()


def bilateral_blur():
    img = cv2.imread('all_type/dx/temp_denoise_demo.png')
    # 用 np.hstack，将多个均值平滑处理后的图像水平合并起来
    blured = np.hstack([
        # img,
        # 9 邻域直径，两个 10 分别是空间高斯函数标准差，灰度值相似性高斯函数标准差
        cv2.bilateralFilter(img, 9, 5, 5),
        cv2.bilateralFilter(img, 9, 100, 100),
        cv2.bilateralFilter(img, 9, 30, 30)
    ])

    plt.figure(figsize=(20, 10))
    plt.imshow(blured[:, :, ::-1])
    plt.show()


if __name__ == '__main__':
    median_blur()
