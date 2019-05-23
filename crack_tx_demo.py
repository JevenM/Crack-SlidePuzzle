import os
import requests
import time
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import darw
import demo
import match
import slide
from lib.config import config as cfg


class CrackSlider():
    """
    通过浏览器截图，识别验证码中缺口位置，获取需要滑动距离，并模仿人类行为破解滑动验证码
    """

    def __init__(self):
        super(CrackSlider, self).__init__()
        # 2 腾讯防水墙地址
        self.url = 'https://007.qq.com/online.html?ADTAG=capt.head'
        # 设置浏览器参数
        chrome_option = webdriver.ChromeOptions()
        # 这个参数是将window.navigator.webdriver设置为undefined
        chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_option.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        self.driver = webdriver.Chrome(
            executable_path=r"E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML"
                            r"/Python/tesserocr/netease/chromedriver",
            chrome_options=chrome_option)
        self.wait = WebDriverWait(self.driver, 5)
        self.zoom = 1
        self.succ = 0
        self.no_succ = 0
        self.count = 0
        self.name = ''
        self.sess = None
        self.net = None

    def open(self):
        self.driver.get(self.url)

    def get_button1(self):
        button = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '可疑用户')))
        return button

    def get_button2(self):
        button = self.wait.until(EC.presence_of_element_located((By.ID, 'code')))
        return button

    def get_pic(self):
        time.sleep(1)
        # 切换frame
        self.driver.switch_to.frame(self.driver.find_elements_by_tag_name("iframe")[1])
        # 获取带有凹槽的背景图片
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tc-bg-img')))
        target_link = target.get_attribute('src')
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        # 保留在/data/demo/下一份
        im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', "target.jpg")
        target_img.save(im_file)
        # 下载图片
        self.name = 'all_type/tx/target_demo.jpg'
        target_img.save(self.name)
        # 使用Image打开图片
        local_img = Image.open(self.name)
        size_loc = local_img.size
        # 340是实际在网页上展示的大小
        self.zoom = 340 / int(size_loc[0])
        print("zoom: ", self.zoom)

    def get_slider(self):
        # 获取带有凹槽的背景图片
        target = self.wait.until(EC.presence_of_element_located((By.ID, 'slideBlock')))
        target_link = target.get_attribute('src')
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        # 下载图片
        name = 'all_type/tx/template_demo.png'
        target_img.save(name)

    def get_tracks(self, distance):
        # sigmoid
        # return sigmoid.return_left(distance + 7)
        return darw.ret_log(distance + 23, 4)

    def match(self, targetname):
        distance = demo.demo_customize(self.sess, self.net, targetname)
        print("match distance: ", distance)
        return int(distance)

    def crack_slider(self):
        self.open()
        time1 = time.time()
        btn1 = self.get_button1()
        btn1.click()
        btn2 = self.get_button2()
        btn2.click()
        self.get_pic()
        self.get_slider()
        # 传统方法
        # distance = match.match_1('all_type/tx/', "all_type/tx/target_demo.jpg",
        # 'all_type/tx/template_demo.png', "demo")
        # 深度学习法
        distance = self.match("target.jpg")

        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'tc-drag-button')))
        ActionChains(self.driver).click_and_hold(slider).perform()

        # 1、滑动方法1第一个为left，-36为观察的来
        # tracks = self.get_tracks(round((distance - 46) * self.zoom))
        # for i in tracks:
        #     ActionChains(self.driver).move_by_offset(xoffset=i, yoffset=0).perform()
        # ActionChains(self.driver).release(slider).perform()
        # 2、滑动方法2，注释上4行
        # slide.go_slide_sigmoid(round(distance * self.zoom)-29, self.driver, slider)
        # slide.go_slide_direct(round(distance * self.zoom) - 27, self.driver, slider)
        slide.go_slide_log(round(distance * self.zoom) - 29, 4, self.driver, slider)
        # slide.go_slide_uniform(round(distance * self.zoom - 27), self.driver, slider, 2)
        time2 = time.time()
        print("耗时：", time2 - time1)
        success = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'show-success')))
        # 选择测试的次数：10
        if self.count < 1:
            if success:
                self.succ += 1
                print("succ:", self.succ)
                self.count += 1
                self.crack_slider()
            else:
                self.no_succ += 1
                print('no succ: ', self.no_succ)
                self.count += 1
                self.crack_slider()
        else:
            print("success rate: ", self.succ / self.count, "  successful : ", self.succ, "  unsuccessful : ",
                  self.no_succ)


if __name__ == '__main__':
    c = CrackSlider()
    c.sess, c.net = demo.faster_detect()
    c.crack_slider()
