# -*- coding:utf-8 -*-
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import cv2, random
import numpy as np
from io import BytesIO
import time, requests

# 准确率估计高达90%以上
import match
import slide


class CrackSlider():

    def __init__(self):
        self.url = 'https://id.163yun.com/login'
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        # 不加这一行说明chrome.exe的位置会报错
        options.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.zoom = 1
        self.success = 0
        self.unsuccess = 0
        self.tarname = ''
        self.temname = ''
        self.time = []

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
        self.tarname = 'all_type/wy/target_login.jpg'
        self.temname = 'all_type/wy/template_login.png'
        target_img.save(self.tarname)
        template_img.save(self.temname)
        local_img = Image.open(self.tarname)
        size_loc = local_img.size  # w,h
        print("size_loc[0]: ", size_loc[0])  # 480 240
        self.zoom = 326 / int(size_loc[0])  # 326×163

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
    '''
    2019.05.16 早上来测试sigmoid的时间以及通过率
    '''

    def crack_slider(self, distance, time1):
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.driver).click_and_hold(slider).perform()
        # slide
        # slide.go_slide_log(distance, 4, self.driver, slider)
        slide.go_slide_sigmoid(distance, self.driver, slider)
        # slide.go_slide_uniform(distance, self.driver, slider, 2)
        # slide.go_slide_direct(distance, self.driver, slider)
        # 必须等待两秒，不然获得不了下面的value值
        time.sleep(2)
        if not self.driver.find_element_by_xpath(
                "//*[@id='bg']/div[2]/div/div/div/div/div[2]/form/div[3]/div/input").get_attribute('value'):
            # 背景会变化，需要重新下载图片
            time2 = time.time()
            self.time.append(time2-time1)
            # print("用时: ", time2 - time1)
            self.unsuccess += 1
            print("失败！次数: ", self.unsuccess)
            print("mean time: ", np.mean(self.time))
            time.sleep(2)
            time1 = time.time()
            self.get_pic()
            distance = match.match_2('all_type/wy/', self.tarname, self.temname,
                                     'login', False)
            # print("raw distance: ", distance)
            zoom_distance = distance * self.zoom + 12
            # print("zooming distance: ", zoom_distance)
            self.crack_slider(zoom_distance, time1)
        else:
            time2 = time.time()
            self.time.append(time2-time1)
            # print("用时: ", time2 - time1)
            self.success += 1
            print("成功！次数: ", self.success)
            print("mean time: ", np.mean(self.time))
            self.begin()

        # 还可以采取这种思路
        # try:
        #     failure = self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'yidun_tips__text'),
        # '向右滑动滑块填充拼图'))
        #     print(failure)

        # except:
        #     print('验证成功')
        #     return None

        # if failure:
        #     self.crack_slider()

    def begin(self):
        self.open()
        time1 = time.time()
        self.get_pic()
        distance = match.match_2('all_type/wy/', self.tarname, self.temname,
                                 'login', False)
        # print("raw distance: ", distance)
        # 12是观察得到
        zoom_distance = distance * self.zoom + 12
        # print("zooming distance: ", zoom_distance)
        # print("zoom： %f" % self.zoom)
        self.crack_slider(zoom_distance, time1)


if __name__ == '__main__':
    cs = CrackSlider()
    cs.begin()
