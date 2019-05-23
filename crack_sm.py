# -*-coding:utf-8-*-
import os

import requests
import time
from io import BytesIO

import cv2
import numpy as np
import random
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import demo
import slide
from lib.config import config as cfg


class CrackSM(object):
    """docstring for Crack_SM"""

    def __init__(self):
        super(CrackSM, self).__init__()
        self.url = 'https://www.fengkongcloud.com/account/login.html'
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--log-level=3')
        # 不加这一行说明chrome.exe的位置会报错
        options.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        self.driver = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.driver, 5, 0.5)
        self.zoom = 1
        self.targetName = ''
        self.templateName = ''
        self.succ = 0
        self.unsucc = 0
        self.sess = None
        self.net = None

    def open(self):
        self.driver.get(self.url)

    def get_pic(self):
        time.sleep(2)
        # 背景图片
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'shumei_captcha_loaded_img_bg')))
        # 前景拼图
        # template = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'shumei_captcha_loaded_img_fg')))

        target_link = target.get_attribute('src')
        # template_link = template.get_attribute('src')

        target_img = Image.open(BytesIO(requests.get(target_link).content))
        # template_img = Image.open(BytesIO(requests.get(template_link).content))

        self.targetName = 'all_type/sm/target.jpg'
        # self.templateName = 'all_type/sm/template.png'

        # 保留在/data/demo/下一份
        im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', "target_shumei.jpg")
        target_img.save(im_file)

        target_img.save(self.targetName)
        # template_img.save(self.templateName)
        local_img = Image.open(self.targetName)
        # local_img.show()
        size_loc = local_img.size
        # 下载下来的图片应该是600×300
        self.zoom = 300 / int(size_loc[0])
        # print("zoom: ", self.zoom)

    def match_len(self):
        # 读取灰度图像
        global top
        target = cv2.imread(self.targetName, 0)
        template = cv2.imread(self.templateName, 0)
        # cv2.imshow('template', template)
        # 获取图像的长和宽
        w, h = template.shape[::-1]
        temp = 'all_type/sm/temp_gray.png'
        targ = 'all_type/sm/targ_gray.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)

        # template = cv2.cvtColor(cv2.imread(temp), cv2.COLOR_BGR2GRAY)
        # template = abs(255 - t emplate)
        # cv2.imwrite(temp, template)

        # ----------------转化为RGBA色彩模式
        img = Image.open(temp)
        img = img.convert("RGBA")
        # 获取图像像素
        pixdata = img.load()

        for y in range(img.size[1]):
            if pixdata[0, y][0] == 0 and pixdata[0, y][1] == 0 and pixdata[0, y][2] == 0:
                print("1", end=" ")
            else:
                top = y + 1  # 记录从上往下遍历直到不是黑色的那个坐标
                break
        for y in range(img.size[1] - 1, 0, -1):
            if pixdata[0, y][0] == 0 and pixdata[0, y][1] == 0 and pixdata[0, y][2] == 0:
                print("0", end=" ")
            else:
                bottom = y - 1  # 记录从下往上遍历直到不是黑色的那个坐标
                break

        imgg = Image.open(temp)
        # 截取template图像，得到中间的slider
        temp1 = imgg.crop((0, top, 90, bottom))
        # 保存一下计算出来位置图片，看看是不是缺口部分
        temp1.save("all_type/sm/slider.png", "PNG")

        # 下面这几行去掉了灰度图中间黑色的区域，但是发现还没有不删除的时候检测准确率高
        # i = Image.open("slider.png")
        # i = i.convert("RGBA")
        # pdata = i.load()
        # # 遍历图片中的像素
        # for y in range(i.size[1]):
        #     for x in range(i.size[0]):
        #         if pdata[x,y][0]==0 and pdata[x,y][1]==0 and pdata[x,y][2]==0:
        #             # 设置像素为白色透明
        #             pdata[x, y] = (255, 255, 255, 0)
        # # 保存图片
        # i.save("denoised_slider.png", "PNG")
        # # ---------------------
        # # 继续使用OpenCV读取图像
        # template = cv2.imread("denoised_slider.png")

        # 继续使用OpenCV读取图像
        template = cv2.imread("all_type/sm/slider.png")
        # 读取灰图像
        target = cv2.imread(targ)
        # 模板匹配
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        # 展示圈出来的区域
        cv2.rectangle(target, (y, x), (y + w, x + bottom - top), (7, 249, 151), 2)
        cv2.imshow('Show', target)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return y * self.zoom  # 缩放

    def match4(self, target):
        distance = demo.demo_customize(self.sess, self.net, target) * self.zoom
        return distance

    def slide(self, time1):
        length = self.match4("target_shumei.jpg")
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'shumei_captcha_slide_btn')))
        ActionChains(self.driver).click_and_hold(slider).perform()
        # 变加速
        # slide.go_slide_2(length, self.driver, slider)
        # slide.go_slide_uniform(length, self.driver, slider, 2)
        slide.go_slide_direct(length, self.driver, slider)
        time2 = time.time()
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'slide_success')))
            self.succ += 1
            print("success! 次数：", self.succ)
            print("用时：", time2-time1)
            self.go()
        except:
            self.unsucc += 1
            print("Failed! 次数：", self.unsucc)
            print("用时：", time2 - time1)
            time1 = time.time()
            self.get_pic()
            self.slide(time1)
            # pass

        # finally:
        # self.go()
        # self.driver.close()

    def go(self):
        self.open()
        time1 = time.time()
        self.get_pic()
        self.slide(time1)


if __name__ == '__main__':
    csm = CrackSM()
    csm.sess, csm.net = demo.faster_detect()
    csm.go()
