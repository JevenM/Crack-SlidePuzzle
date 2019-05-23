# -*- coding： utf-8 -*-

import base64
import requests
import time
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 在线体验成功率很高，定位不是很准确，不检测滑动轨迹特征
import match
import slide


class Crack:
    def __init__(self):
        self.url = "https://www.dingxiang-inc.com/business/captcha-online"
        chrome_option = webdriver.ChromeOptions()
        chrome_option.binary_location = r"D:/Google\Chrome/Application\chrome.exe"
        chrome_option.add_argument('--log-level=3')
        chrome_option.add_argument('-lang=zh-cn')
        self.browser = webdriver.Chrome(
            executable_path='E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML/Python/tesserocr/netease/'
                            'chromedriver.exe',
            chrome_options=chrome_option)
        self.wait = WebDriverWait(self.browser, 5, 0.5)
        self.zoom = 400 / 300

    def open_browser(self):
        self.browser.get(self.url)

    # 为了便于循环，单独提出来
    def doit(self, target, template):
        time_start = time.time()
        print("time_start: ", time_start)
        self.get_image(target, template)
        # length = self.match2(target, template
        # length = match.match_2("all_type/dx/", target, template, "demo", True) / self.zoom
        length = match.match_3("all_type/dx/", target, template
                               , "demo", True) / self.zoom
        print("length: ", length)
        self.slide_pizzle(length)
        time_end = time.time()
        print("time_end: ", time_end)
        return time_end - time_start

    # target大图，template小图
    def crack(self, target, template):
        self.open_browser()
        t = self.doit(target, template)

        while not self.is_success('dx_captcha_basic_lang_verify_success'):
            # 后面立刻100%弹出下一个挑战，无法判定此次是否成功！
            print('OOPS！ Total time: %s. Once Again...' % t)
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
        element = self.browser.find_element_by_xpath('//*[@id="dx_captcha_basic_slider_1"]')
        distance -= 10  # 滑块初始前面的gap
        ActionChains(self.browser).click_and_hold(element).perform()
        # slide.go_slide_log(distance, 4, self.browser, element)
        # slide.go_slide_sigmoid(distance, self.browser, element)
        slide.go_slide_2(distance, self.browser, element)
        # slide.go_slide_uniform(distance, self.browser, element, 2)
        # slide.go_slide_direct(distance, self.browser, element)

        # 好像只能通过这种方式
        # ActionChains(self.browser).drag_and_drop_by_offset(element, distance, 0).perform()

    def get_image(self, target, template):
        time.sleep(2)
        # 下面的js代码根据canvas文档说明而来
        _js = 'return document.getElementById("dx_captcha_basic_bg_1").firstChild.toDataURL();'
        # 执行 js 代码并拿到图片 base64 数据
        bg_info = self.browser.execute_script(_js)  # 执行js文件得到带图片信息的图片数据
        bg_base64 = bg_info.split(',')[1]  # 拿到base64编码的图片信息
        bg_bytes = base64.b64decode(bg_base64)  # 转为bytes类型
        with open(target, 'wb') as f:  # 保存canvas图片到本地
            f.write(bg_bytes)
        # local_img = Image.open(target)
        # size = local_img.size
        # print("x: %d, y: %d" % (size[0], size[1]))

        element = self.browser.find_element_by_xpath('//*[@id="dx_captcha_basic_sub-slider_1"]/img')
        template_link = element.get_attribute('src')
        # 在这open函数报错OSError: cannot identify image file <_io.BytesIO object at 0x000001E479B405C8>，更新pillow解决
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        template_img.save(template)

        # template_img = Image.open(BytesIO(requests.get(template_link).content))
        # img_byte_arr = BytesIO()  # 创建一个空的Bytes对象
        # template_img.save(img_byte_arr, format='PNG')  # PNG就是图片格式，我试过换成JPG/jpg都不行
        # img_byte_arr = img_byte_arr.getvalue()  # 这个就是保存的图片字节流

        # with open(template, "wb") as f:
        #     f.write(img_byte_arr)
        # 原文：https://blog.csdn.net/wgPython/article/details/80740067
        # template_img.save(template)

    # def match1(self, oblk='all_type/dx/target_demo.jpg', otemp='all_type/dx/template_demo.png'):
    #     target = cv2.imread(oblk, 0)
    #     temp = 'all_type/dx/tem_gray_demo.png'
    #     targ = 'all_type/dx/tar_gray_demo.jpg'
    #     # 必须灰白打开
    #     template = cv2.imread(otemp, 0)
    #     cv1.handle(otemp, temp)
    #     # 获取图像的长和宽
    #     template = cv2.imread(otemp, 0)
    #     w, h = template.shape[::-1]
    #     template = cv2.imread(temp, 0)
    #     cv2.imwrite(temp, template)
    #     cv2.imwrite(targ, target)
    #     # ------------ 这几部同样是转换为灰度图，重复，去掉
    #     # template = cv2.imread(temp)
    #     # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    #     # cv2.imwrite("all_type/dx/tem_2gray.png", template)
    #     # img = Image.open("all_type/dx/tem_2gray.png")
    #
    #     # ----------------转化为RGBA色彩模式
    #     img = Image.open(temp)
    #     img = img.convert("RGBA")
    #     # 获取图像像素
    #     pixdata = img.load()
    #     # 遍历图片中的像素
    #     for y in range(img.size[1]):
    #         for x in range(img.size[0]):
    #             # 这个阈值也是试出来的
    #             if pixdata[x, y][0] < 5 and pixdata[x, y][1] < 5 and pixdata[x, y][2] < 5:
    #                 # 设置像素为白色透明
    #                 pixdata[x, y] = (255, 255, 255, 0)
    #     # 保存图片
    #     img.save("all_type/dx/temp_denoise_demo.png", "PNG")
    #     import utils
    #     utils.denoise(temp)
    #     denoiseimg = cv1.mean_blur("all_type/dx/temp_denoise_demo.png")
    #     # ---------------------
    #     # 继续使用OpenCV读取图像
    #     template = cv2.imread(denoiseimg)
    #     target = cv2.imread(targ)
    #     # 模板匹配
    #     result = cv2.matchTemplate(template, target, cv2.TM_CCOEFF_NORMED)
    #     x, y = np.unravel_index(result.argmax(), result.shape)
    #     # 展示圈出来的区域
    #     cv2.rectangle(target, (y, x), (y + w, x + h), (7, 249, 151), 2)
    #     cv2.imshow('Show', target)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    #     return y / self.zoom


if __name__ == "__main__":
    Ocrack = Crack()
    Ocrack.crack('all_type/dx/target_demo.jpg', 'all_type/dx/template_demo.png')
