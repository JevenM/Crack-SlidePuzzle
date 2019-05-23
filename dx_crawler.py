# -*-coding:utf-8-*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from io import BytesIO
import time, requests, base64
from PIL import Image

# desc: 收集顶象带有凹槽的背景图像和工具
# date: 2019.5.08 15.12
# author: maoge
import match


class Crack_DX(object):
    """docstring for Crack_DX"""

    def __init__(self):
        super(Crack_DX, self).__init__()
        self.url = 'https://www.dingxiang-inc.com/business/captcha-online'
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--log-level=3')
        options.add_argument('-lang=zh-cn')
        # 不加这一行说明chrome.exe的位置会报错
        options.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        self.browser = webdriver.Chrome(chrome_options=options)
        self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 10, 0.5)
        self.index = 10

    def open(self):
        self.browser.get(self.url)

    def get_pic(self):
        time.sleep(2)
        # 下面的js代码根据canvas文档说明而来
        _js = 'return document.getElementById("dx_captcha_basic_bg_1").firstChild.toDataURL();'
        # 执行 js 代码并拿到图片 base64 数据
        bg_info = self.browser.execute_script(_js)  # 执行js文件得到带图片信息的图片数据
        bg_base64 = bg_info.split(',')[1]  # 拿到base64编码的图片信息
        bg_bytes = base64.b64decode(bg_base64)  # 转为bytes类型
        with open("all_type/dx/bg/target" + str(self.index) + '.jpg', 'wb') as f:  # 保存canvas图片到本地
            f.write(bg_bytes)

        element = self.browser.find_element_by_xpath('//*[@id="dx_captcha_basic_sub-slider_1"]/img')
        template_link = element.get_attribute('src')
        # 在这open函数报错OSError: cannot identify image file <_io.BytesIO object at 0x000001E479B405C8>，更新pillow解决
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        template_img.save("all_type/dx/blk/template" + str(self.index) + '.png')
        self.index += 1


if __name__ == '__main__':
    # 以下代码为了收集顶象100张图像作为定位测试集
    # dx = Crack_DX()
    # dx.open()
    # # 总共收集100张
    # i = 9
    # while i > 0:
    #     for index in range(1, 11):
    #         if index % 10 == 0:
    #             dx.open()
    #             dx.get_pic()
    #         else:
    #             element = dx.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,
    #                                                                 'dx_captcha_basic_img_btn_refresh')))
    #             element.click()
    #             dx.get_pic()
    #
    #     time.sleep(10)
    #     i -= 1
    #     print("i为： ", i)
    # print("收集结束！")

    # 生成100张测试定位后的图像（有标记框）
    for i in range(0, 100):
        # 生成的定位图像文件在mark1里面
        # match.match_1("all_type/dx/", 'all_type/dx/bg/target' + str(i) + '.jpg',
        #               'all_type/dx/blk/template' + str(i) + '.png', str(i),
        #               "demo")
        # 生成的定位图像文件在mark里面
        # match.match_4_for_crawler("all_type/dx/", 'all_type/dx/bg/target' + str(i) + '.jpg',
        #                           'all_type/dx/blk/template' + str(i) + '.png', str(i),
        #                           "demo")
        # 生成的定位图像文件在mark3里面
        match.match_3("all_type/dx/", 'all_type/dx/bg/target' + str(i) + '.jpg',
                      'all_type/dx/blk/template' + str(i) + '.png', str(i))
