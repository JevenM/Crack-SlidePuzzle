# -*-coding:utf-8-*-
import os
import requests
import time
from io import BytesIO

import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import demo
import slide
from lib.config import config as cfg


# 破解腾讯验证码的类
class CrackSlider:

    def __init__(self):
        super(CrackSlider, self).__init__()
        # 1 QQ安全中心url
        self.url = 'https://aq.qq.com/v2/uv_aq/html/reset_pwd/pc_reset_pwd_input_account.html?v=4.0'
        # 设置浏览器参数
        chrome_option = webdriver.ChromeOptions()
        # chrome_option.add_argument('--proxy-server=http://127.0.0.1:8080')
        # 这个参数是将window.navigator.webdriver设置为undefined
        chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_option.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        # 设置chrome的执行程序的位置
        self.driver = webdriver.Chrome(
            executable_path=r"E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML"
                            r"/Python/tesserocr/netease/chromedriver",
            chrome_options=chrome_option)

        # 等待时间10秒
        self.wait = WebDriverWait(self.driver, 10)
        # 缩放尺度
        self.zoom = 1
        # 成功次数
        self.succ = 0
        # 不成功通过的次数
        self.no_succ = 0
        # 名字
        self.name = ''
        self.sess = None
        self.net = None

    def open(self):
        self.driver.get(self.url)

    def get_button(self):
        button = self.wait.until(EC.presence_of_element_located((By.ID, 'loading_animation')))
        button.click()

    def change_frame(self):
        time.sleep(1)
        # 找到指定的frame
        self.driver.switch_to.frame(self.driver.find_elements_by_tag_name("iframe")[2])

    def get_pic(self):
        # 背景图片
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tc-bg-img')))
        # 找到src属性
        target_link = target.get_attribute('src')
        # print(target_link)
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        # 保留在/data/demo/下一份
        im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', "target_login.jpg")
        target_img.save(im_file)
        # 下载图片
        self.name = 'all_type/tx/target_login.jpg'
        target_img.save(self.name)
        # 使用Image打开图片
        local_img = Image.open(self.name)
        # 获得图片的长和宽
        size_loc = local_img.size
        # 计算得到缩放尺度并更新
        self.zoom = 340 / int(size_loc[0])
        print("zoom: ", self.zoom)

    def match(self, target):
        distance = demo.demo_customize(self.sess, self.net, target)
        print("match distance: ", distance)
        return int(distance)

    def crack_slider(self):
        # 从点击按钮之后开始记录时间
        time1 = time.time()
        # 获取图片下载
        self.get_pic()
        # 计算距离
        distance = self.match("target_login.jpg")
        print("real distance: ", distance * self.zoom)
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'tc-drag-thumb')))  # tcaptcha-drag-button
        # 按压滑块
        ActionChains(self.driver).click_and_hold(slider).perform()
        # 匀速
        # slide.go_slide_uniform(distance * self.zoom - 29, self.driver, slider, 2)
        # 直接
        # slide.go_slide_direct(distance * self.zoom - 29, self.driver, slider)
        slide.go_slide_2(distance * self.zoom - 29, self.driver, slider)
        # slide.go_slide_log(distance * self.zoom - 29, 4, self.driver, slider)
        # slide.go_slide_sigmoid(distance * self.zoom - 29, self.driver, slider)
        time.sleep(0.2)
        time2 = time.time()
        print('用时', time2 - time1)

        if self.is_success("tcaptcha_trigger_text_init"):
            self.succ += 1
            print("succ:", self.succ)
            # self.crack_slider()
            button = self.driver.find_element_by_id('next_step')
            button.click()
            self.get_button()
            c.change_frame()
            self.crack_slider()
        else:
            self.no_succ += 1
            print('no succ: ', self.no_succ)
            c.change_frame()
            self.crack_slider()

        # self.wait.until(
        #     EC.text_to_be_present_in_element((By.XPATH, '//*[@id="tcaptcha_trigger_text_init"]'), '验证成功'))
        # error_again = self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME,
        #                                                                 'tcaptcha-trigger-text'), '再试一次，拼得比上次更准些'))
        # hesitate = self.wait.until(EC.text_to_be_present_in_element((By.ID, 'statusError'), '网络恍惚了一下，再试一次吧'))

    def is_success(self, id_con):
        # 跳出当前iframe
        # self.driver.switch_to.parent_frame()
        self.driver.switch_to.parent_frame()
        try:
            # 返回最外层iframe
            # self.driver.switch_to.default_content()
            # self.driver.switch_to.parent_frame()
            WebDriverWait(self.driver, 10, 0.5).until(
                EC.text_to_be_present_in_element((By.ID, id_con), '验证成功'))
            return True
        except:
            return False


if __name__ == '__main__':
    c = CrackSlider()
    c.sess, c.net = demo.faster_detect()
    # 打开浏览器
    c.open()
    # 获取按钮
    c.get_button()
    c.change_frame()
    c.crack_slider()
