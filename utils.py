# -*- coding:utf-8 -*-
import time
from io import BytesIO

import cv2
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def denoise(inputimg, threshold=5, savepath="all_type/dx/temp_denoise_demo.png"):
    img = Image.open(inputimg)
    img = img.convert("RGBA")
    # 获取图像像素
    pixdata = img.load()
    # 遍历图片中的像素
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            # 这个阈值也是试出来的
            if pixdata[x, y][0] < threshold and pixdata[x, y][1] < threshold and pixdata[x, y][2] < threshold:
                # 设置像素为白色透明
                pixdata[x, y] = (255, 255, 255, 0)
    # 保存图片
    img.save(savepath, "PNG")


def denoise2(inputimg, threshold=15, savepath="all_type/dx/temp_reverse_demo.png"):
    img = Image.open(inputimg)
    img = img.convert("RGBA")
    # 获取图像像素
    pixdata = img.load()
    # 遍历图片中的像素
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][3] == 0 or (pixdata[x, y][0] < threshold and pixdata[x, y][1] < threshold and pixdata[x, y][2] < threshold):
                # 设置像素为白色
                pixdata[x, y] = (255, 255, 255, 0)
    # 保存图片
    img.save(savepath, "PNG")


# 判断颜色是否相近，计算色差
# 两张原始图的大小都是相同的260*116，那就通过两个for循环依次对比每个像素点的RGB值，如果相差超过50则就认为找到了缺口的位置：
def is_similar_color(x_pixel, y_pixel, threshold=20):
    for i, pixel in enumerate(x_pixel):
        if abs(y_pixel[i] - pixel) > threshold:
            print("像素差：%d" % (y_pixel[i] - pixel))
            return False
    return True


# 计算距离
def get_offset_distance(cut_image, full_image, parentdir="all_type/jy/", threshold=20):
    for x in range(cut_image.width):
        for y in range(cut_image.height):
            cpx = cut_image.getpixel((x, y))
            fpx = full_image.getpixel((x, y))
            if not is_similar_color(cpx, fpx, threshold):
                img = cut_image.crop((x, y, x + 53, y + 53))
                # 保存一下计算出来位置图片，看看是不是缺口部分，如果上面有缺口，那么就会截不到了，因为是固定x递增y，最先找到靠左的不同像素，但这不是关键
                # 关键是找出最靠左的位置就行
                img.save(parentdir + "gap.png")
                return x


def get_screenshot(browser):
    """
    获取网页截图
    :return: 截图对象
    """
    screenshot = browser.get_screenshot_as_png()
    # browser.get_screenshot_as_file(
    #     "E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML/FasterRCNN/Faster-RCNN-TensorFlow-Python3.5-master/all_type/page.png")
    screenshot = Image.open(BytesIO(screenshot))
    return screenshot


def get_position(browser, class_name):
    """
    获取验证码位置
    :return: 验证码位置元组
    """
    # time.sleep(2)
    img = WebDriverWait(browser, 10, 0.5).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name)))  # geetest_canvas_slice

    location = img.location
    size = img.size

    # 由于先点击refresh，又多向上滚动50pixel，所以全部一样
    location['y'] -= 4768  # 多减去50pixel从而精确定位
    top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
        'width']
    return left


# 极验
def get_shake(img):
    for x in range(img.width):
        for y in range(img.height):
            px1 = img.getpixel((x, y))
            px2 = img.getpixel((5, 5))
            if not is_similar_color(px1, px2):
                return x
