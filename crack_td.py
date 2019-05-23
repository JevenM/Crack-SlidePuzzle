# -*- coding： utf-8 -*-
import os, demo
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
import time, requests
import cv2
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt

import slide
from lib.config import config as cfg

print(os.getcwd())
'''
2019.04.29 19:59 100%破解率
'''


class Crack:

    def __init__(self):
        self.url = "https://x.tongdun.cn/onlineExperience/slidingPuzzle"
        chrome_option = webdriver.ChromeOptions()
        chrome_option.binary_location = r"D:/Google\Chrome/Application\chrome.exe"
        chrome_option.add_argument('--log-level=3')
        self.browser = webdriver.Chrome(
            executable_path='E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML/Python/tesserocr/netease'
                            '/chromedriver.exe',
            chrome_options=chrome_option)
        self.wait = WebDriverWait(self.browser, 100)
        self.zoom = 1  # 320*180
        self.succ = 0
        self.unsucc = 0
        self.sess = None
        self.net = None

    def open_browser(self):
        self.browser.get(self.url)
        # self.browser.maximize_window()
        WebDriverWait(self.browser, 10, 0.5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="loginBtn"]')))
        # 鼠标移动到拖动按钮，按压显示出图片
        login = self.browser.find_element_by_xpath('//*[@id="loginBtn"]')
        login.click()

    # 为了便于循环，单独提出来
    def doit(self, target, template):
        time_start = time.time()
        self.get_image(target, template)
        # length = self.match4(target)
        length = self.match1()
        print("length: ", length)
        self.slide_pizzle(length)
        time_end = time.time()
        return time_end - time_start

    # target大图，template小图
    def crack(self, target, template):
        self.open_browser()
        t = self.doit(target, template)
        while not self.is_success('td-pop-slide-msg'):
            print('Failed！ Total time: %s. Once Again...' % t)
            self.doit(target, template)
        print('Succeeded! Total time: ', t)
        # self.browser.close()

    # 判断是否破解成功
    def is_success(self, class_con):
        try:
            WebDriverWait(self.browser, 10, 0.5).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, class_con), '验证通过'))
            return True
        except:
            return False

    def slide_pizzle(self, distance):
        # WebDriverWait(self.browser, 10, 0.5).until(EC.element_to_be_clickable((By.XPATH,
        # '//*[@id="dx_captcha_basic_slider-img-animated-wrap_1"]')))
        element = self.browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[3]/div[2]')
        distance -= 10  # 观察得到
        ActionChains(self.browser).click_and_hold(element).perform()
        # slide.go_slide_sigmoid(distance, self.browser, element)
        # slide.go_slide_log(distance, 4, self.browser, element)
        # slide.go_slide_1(distance, self.browser, element)
        # 和极验一样，最后会有一个抖动偏移，大约10像素，只不过它是固定的
        slide.go_slide_uniform(distance, self.browser, element, 2)

        # 当然针对同盾，使用直接拖放更快速，不检测轨迹是否和人类相似
        # ActionChains(self.browser).drag_and_drop_by_offset(element, distance, 0).perform()

    def get_image(self, target, template):
        time.sleep(2.5)
        # 下面的js代码根据canvas文档说明而来
        JS = 'return document.getElementsByClassName("td-bg-img")[0].toDataURL();'
        # 执行 JS 代码并拿到图片 base64 数据
        bg_info = self.browser.execute_script(JS)  # 执行js文件得到带图片信息的图片数据
        bg_base64 = bg_info.split(',')[1]  # 拿到base64编码的图片信息
        bg_bytes = base64.b64decode(bg_base64)  # 转为bytes类型
        # 保留在/data/demo/下一份
        im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', target)
        with open(im_file, 'wb') as f:  # 保存canvas图片到demo
            f.write(bg_bytes)
        with open("all_type/td/" + target, 'wb') as f:  # 保存canvas图片到本地
            f.write(bg_bytes)
        element = self.browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[2]/img')
        template_link = element.get_attribute('src')
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        template_img.save("all_type/td/" + template)

        local_img = Image.open("all_type/td/" + target)
        size = local_img.size
        print("zoom: %f" % (320 / size[0]))

    # 定位准确率100%
    def match1(self, oblk='all_type/td/target.jpg', otemp='all_type/td/template.png'):
        """
        flags = -1：imread按解码得到的方式读入图像
        flags = 0：imread按单通道的方式读入图像，即灰白图像
        flags = 1：imread按三通道方式读入图像，即彩色图像
        """
        target1 = cv2.imread(oblk, 0)
        template = cv2.imread(otemp, 0)
        # 获取图像的长和宽
        w, h = template.shape[::-1]
        temp = 'temp.png'
        targ = 'targ.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target1)
        # template = cv2.imread(temp)
        # template1 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        # template = abs(255 - template)
        # cv2.imwrite(temp, template1)

        # ----------------转化为RGBA色彩模式
        img = Image.open(temp)
        img = img.convert("RGBA")
        # 获取图像像素
        pixdata = img.load()
        # 遍历图片中的像素
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pixdata[x, y][0] < 15 and pixdata[x, y][1] < 15 and pixdata[x, y][2] < 15:
                    # 设置像素为白色透明
                    pixdata[x, y] = (255, 255, 255, 0)
        # 保存图片
        img.save(temp, "PNG")
        # ---------------------
        # 继续使用OpenCV读取图像
        template = cv2.imread(temp)
        target = cv2.imread(targ)
        # 模板匹配
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        # 展示圈出来的区域
        cv2.rectangle(target, (y, x), (y + w, x + h), (7, 249, 151), 1)
        # cv2.imshow('Show', target)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        plt.subplot(221), plt.imshow(Image.open(oblk))
        plt.title('Image RGB'), plt.xticks([]), plt.yticks([])
        plt.subplot(222), plt.imshow(target, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.subplot(223), plt.imshow(template, cmap='gray')
        plt.title('Template Gray'), plt.xticks([]), plt.yticks([])
        plt.subplot(224), plt.imshow(result, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.suptitle('method: cv2.TM_CCOEFF_NORMED')
        plt.show()
        return y / self.zoom

    # 此定位方法不准确
    def match2(self, target, template):
        '''
        输入背景和滑块，输出缺口的横坐标
        '''
        img_rgb = cv2.imread(target, 1)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        '''
        flags = -1：imread按解码得到的方式读入图像
        flags = 0：imread按单通道的方式读入图像，即灰白图像
        flags = 1：imread按三通道方式读入图像，即彩色图像
        '''
        template = cv2.imread(template, 0)

        w, h = template.shape[::-1]
        print("width: %d, height: %d" % (w, h))
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # result参数表示匹配结果图像，必须是单通道32位浮点。如果image的尺寸为W x H，templ的尺寸为w x h，则result的尺寸为(W-w+1)x(H-h+1)。
        run = 1
        # 使用二分法查找阈值的精确值
        L = 0
        R = 1.0
        while run < 30:
            run += 1
            threshold = (R + L) / 2
            print("threshold: %f" % threshold)
            if threshold < 0:
                print('Error')
                return None
            loc = np.where(res >= threshold)
            # 返回的是数组的列表，如果是二维，则有两个数组，一个表示横行，是图片中的纵坐标（第几行），一个表示纵列，表示图片中横坐标（第几列）
            print("loc[1]的长度为：%d" % len(loc[1]))
            if len(loc[1]) > 1:
                # 大于1说明匹配了多个目标模板，而我们只需要确定一个
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                print('目标区域起点x坐标为：%d' % loc[1][0])
                print('loc[0]为: ', loc[0])
                for i in loc[0]:
                    print(i)
                print('loc[1]为: ', loc[1])
                for j in loc[1]:
                    print(j)
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        # cv2.imshow('img_template', template)
        # cv2.imshow('target', img_rgb)
        # cv2.waitKey(0)
        bottom_right = (loc[1][0] + w, loc[0][0] + h)
        cv2.rectangle(img_gray, (loc[1][0], loc[0][0]), bottom_right, 255, 1)

        plt.subplot(221), plt.imshow(Image.open(target))
        plt.title('Image RGB'), plt.xticks([]), plt.yticks([])
        plt.subplot(222), plt.imshow(img_gray, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.subplot(223), plt.imshow(template, cmap='gray')
        plt.title('Template Gray'), plt.xticks([]), plt.yticks([])
        plt.subplot(224), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.suptitle('method: cv2.TM_CCOEFF_NORMED')
        plt.show()
        return loc[1][0]

    # 此方法不准确
    def match3(self, target, template):
        img_rgb = cv2.imread(target, 1)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        mn_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # 使用不同的方法，对结果的解释不同

        # 方法判断
        # if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        #     top_left = min_loc
        # else:
        #     top_left = max_loc

        # 最大值的坐标就是距离左边界和上边界的距离
        top_left = max_loc

        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(img_gray, top_left, bottom_right, 255, 1)

        plt.subplot(221), plt.imshow(Image.open(target))
        plt.title('Image RGB'), plt.xticks([]), plt.yticks([])
        plt.subplot(222), plt.imshow(img_gray)
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.subplot(223), plt.imshow(template, cmap='gray')
        plt.title('Template Gray'), plt.xticks([]), plt.yticks([])
        plt.subplot(224), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.suptitle('method: cv2.TM_CCOEFF_NORMED')
        plt.show()
        return top_left[0]

    # def match4(self, target):
    #     distance = demo.demo_customize(self.sess, self.net, target) * self.zoom
    #     return distance


if __name__ == "__main__":
    Ocrack = Crack()
    # Ocrack.sess, Ocrack.net = demo.faster_detect()
    Ocrack.crack('target.jpg', 'template.png')
    # Ocrack.doit('target.jpg', 'template.png')
