# -*- coding： utf-8 -*-

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

import slide


class Crack:
    def __init__(self):
        self.url = "https://user.dingxiang-inc.com/user/register"
        chrome_option = webdriver.ChromeOptions()
        chrome_option.binary_location = r"D:/Google\Chrome/Application\chrome.exe"
        chrome_option.add_argument('--log-level=3')
        self.browser = webdriver.Chrome(
            executable_path='E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML/Python/tesserocr/netease/'
                            'chromedriver.exe',
            chrome_options=chrome_option)
        self.wait = WebDriverWait(self.browser, 5)
        self.zoom = 400 / 300

    def open_browser(self):
        self.browser.get(self.url)
        # self.browser.maximize_window()
        # WebDriverWait(self.browser, 10, 0.5).until(EC.element_to_be_clickable((By.XPATH,
        # '//*[@id="dx_captcha_basic_slider-img-animated-wrap_1"]')))
        # 鼠标移动到拖动按钮，按压显示出图片
        # element = self.browser.find_element_by_xpath('//*[@id="dx_captcha_basic_slider-img-animated-wrap_1"]')
        # ActionChains(self.browser).click_and_hold(element).perform()

    # 为了便于循环，单独提出来
    def doit(self, target, template):
        time_start = time.time()
        self.get_image(target, template)
        import match
        # length = match.match_4('all_type/dx/', target, template, 'regist', True) / self.zoom
        # length = match.match_3('all_type/dx/', target, template, 'regist', True) / self.zoom
        length = match.match_1('all_type/dx/', target, template, "regist") / self.zoom
        print("length: ", length)
        self.slide_pizzle(length)
        time_end = time.time()
        return time_end - time_start

    # target大图，template小图
    def crack(self, target, template):
        self.open_browser()
        t = self.doit(target, template)

        while not self.is_success('dx_captcha_basic_lang_verify_success'):
            print('Failed！ Total time: %s. Once Again...' % t)
            self.doit(target, template)

        print('Succeeded! Total time: ', t)

    # 判断是否破解成功
    def is_success(self, class_con):
        try:
            self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, class_con), '验证成功'))
            return True
        except:
            return False

    def slide_pizzle(self, distance):
        element = self.browser.find_element_by_xpath('//*[@id="dx_captcha_basic_slider-img-animated-wrap_1"]')
        distance -= 10  # 滑块初始前面的gap
        # ActionChains(self.browser).click_and_hold(element).perform()
        # slide.go_slide_log(distance, 4, self.browser, element)
        # slide.go_slide_sigmoid(distance, self.browser, element)
        # slide.go_slide_2(distance, self.browser, element)
        # slide.go_slide_uniform(distance, self.browser, element, 2)
        ActionChains(self.browser).drag_and_drop_by_offset(element, distance, 0).perform()

    def get_image(self, target, template):
        time.sleep(2)
        # 下面的js代码根据canvas文档说明而来
        _JS = 'return document.getElementById("dx_captcha_basic_bg_1").firstChild.toDataURL();'
        # 执行 JS 代码并拿到图片 base64 数据
        bg_info = self.browser.execute_script(_JS)  # 执行js文件得到带图片信息的图片数据
        bg_base64 = bg_info.split(',')[1]  # 拿到base64编码的图片信息
        bg_bytes = base64.b64decode(bg_base64)  # 转为bytes类型
        with open(target, 'wb') as f:  # 保存canvas图片到本地
            f.write(bg_bytes)

        element = self.browser.find_element_by_xpath('//*[@id="dx_captcha_basic_sub-slider_1"]/img')
        template_link = element.get_attribute('src')
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        template_img.save(template)
        # local_img = Image.open(template)
        # size = local_img.size
        # print("x: %d, y: %d" % (size[0], size[1]))


if __name__ == "__main__":
    Ocrack = Crack()
    Ocrack.crack('all_type/dx/target_regist.png', 'all_type/dx/template_regist.png')
