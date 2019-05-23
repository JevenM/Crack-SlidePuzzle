# -*- coding:utf-8 -*-
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


# 准确率估计高达90%以上
# 


class CrackSlider:

    def __init__(self):
        self.url = 'http://dun.163.com/trial/jigsaw'
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        # 不加这一行说明chrome.exe的位置会报错
        options.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        self.driver = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.zoom = 1
        self.tracks = {}
        self.success = 0
        self.unsuccess = 0
        self.targname = ''
        self.tempname = ''

    def open(self):
        self.driver.get(self.url)

    def get_pic(self):
        time.sleep(2)
        # 定位到的第一个元素即可，即使页面有多个class也不怕
        # 以下两个条件验证元素是否出现，传入的参数都是元组类型的locator，如(By.ID, ‘kw’) 
        # 顾名思义，一个只要一个符合条件的元素加载出来就通过；另一个必须所有符合条件的元素都加载出来才行 
        # presence_of_element_located 
        # presence_of_all_elements_located
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))
        template = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_jigsaw')))
        target_link = target.get_attribute('src')
        template_link = template.get_attribute('src')
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        self.targname = "all_type/wy/target_demo.jpg"
        self.tempname = 'all_type/wy/template_demo.png'
        target_img.save(self.targname)
        template_img.save(self.tempname)
        local_img = Image.open(self.targname)
        size_loc = local_img.size
        self.zoom = 320 / int(size_loc[0])

    # def get_tracks(self, distance):
    #     print("distance： %f" % distance)
    #     # 这15个像素是为了与后面back_tracks的距离的和抵消
    #     # distance += 15
    #     v = 0
    #     t = 0.2
    #     forward_tracks = []
    #     current = 0
    #     mid = distance * 4 / 6  #减速阀值
    #     mid2 = distance * 3/15
    #     # 这个加速度公式浪费了我一晚上，最终结论，不是之前物理中学的那个公式，这个是在每个时间段累加的，区别不大
    #     # 但是意义是相同的，不必钻牛角尖。还有a设置为2和3还有3/5和2/5先加速后减速是为了让滑动块刚好在准确位置速度为0，如果把正a改小或者把负a减小都不行，
    #     # 会造成重复运动，比如把下面的注释取消，第二个if改为elif即可。
    #     # 本人已经用公示论证，唉就是这一点我糊涂了。
    #     while current < distance:
    #         if current < mid2:
    #             a = 1.5  
    #         elif current < mid:
    #         	a = 2   #加速度为+2
    #         else:
    #             a = -3  #加速度-3
    #         # print("a为: %f" % a)
    #         s  = v * t + 0.5 * a * (t ** 2)
    #         v = v + a * t
    #         current += s
    #         # print("current为: %f" % current)
    #         forward_tracks.append(round(s))

    #     back_tracks = [-3, -2, -2, -0, -2, -2, 0, -1, -1, -2]
    #     return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}

    def get_tracks(self, distance):
        track = []
        # 当前位移
        current = 0
        # 先加速再匀速再减速
        # 匀速运动的位移量
        # over = random.randint(distance, distance + 10)

        x_1 = float('%.4f' % random.uniform(3 / 5, 6 / 8))

        # x_ac加速变匀速， x_de匀速变减速的点
        x_ac = distance * x_1

        # 计算间隔
        t = 0.2
        # 初速度
        v = random.randint(0, 2)

        while current < distance:
            if current < x_ac:
                a = random.randint(2, 4)
            else:
                a = -random.randint(3, 7)
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t

            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return {'forward_tracks': track}

    def match(self, target, template):
        """
        :param target: target image path
        :param template: template image path
        :return: diatance to slide
        """
        img_rgb = cv2.imread(target, 1)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template, 0)
        '''
        flags = -1：imread按解码得到的方式读入图像
        flags = 0：imread按单通道的方式读入图像，即灰白图像
        flags = 1：imread按三通道方式读入图像，即彩色图像
        '''
        # run = 1
        w, h = template.shape[::-1]
        print("width: %d, height: %d" % (w, h))
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # result参数表示匹配结果图像，必须是单通道32位浮点。如果image的尺寸为W x H，
        # templ的尺寸为w x h，则result的尺寸为(W-w+1)x(H-h+1)。
        run = 1

        # 使用二分法查找阈值的精确值
        L = 0
        R = 1.0
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            print("threshold: %f" % threshold)
            if threshold < 0:
                print('Error')
                return None

            loc = np.where(res >= threshold)
            # 返回的是数组的列表，如果是二维，则有两个数组，一个是横坐标一个纵坐标
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
        return loc[1][0]

    def crack_slider(self):
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.driver).click_and_hold(slider).perform()
        print("sum(tracks['forward_tracks']): ", sum(self.tracks['forward_tracks']))
        # 先向前移动
        for track in self.tracks['forward_tracks']:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()

        # time.sleep(0.2)
        # 向后移动
        # for back_tracks in self.tracks['back_tracks']:
        #     ActionChains(self.driver).move_by_offset(xoffset=back_tracks, yoffset=0).perform()
        # 然后前后抖动
        # ActionChains(self.driver).move_by_offset(xoffset=-4, yoffset=0).perform()
        # ActionChains(self.driver).move_by_offset(xoffset=4, yoffset=0).perform()
        time.sleep(0.5)
        # 释放hold操作
        ActionChains(self.driver).release().perform()
        # 必须等待两秒，不然获得不了下面的value值
        time.sleep(2)
        if not self.driver.find_element_by_xpath(
                "/html/body/main/div/div/div[2]/div[2]/div[1]/div/div[2]/div[3]/div/input").get_attribute('value'):
            # 背景会变化，需要重新下载图片
            self.unsuccess += 1
            print("失败！次数: ", self.unsuccess)
            self.begin()
        else:
            self.success += 1
            print("成功！次数: ", self.success)
            self.begin()

        # 还可以采取这种思路
        # try: failure = self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME,
        # 'yidun_tips__text'), '向右滑动滑块填充拼图'))
        # print(failure)

        # except:
        #     print('验证成功')
        #     return None

        # if failure:
        #     self.crack_slider()

    def begin(self):
        self.open()
        self.get_pic()
        distance = self.match(self.targname, self.tempname)
        print("zoom： %f" % self.zoom)
        self.tracks = self.get_tracks((distance + 7) * cs.zoom)  # 对位移的缩放计算
        self.crack_slider()


if __name__ == '__main__':
    cs = CrackSlider()
    cs.begin()
