# -*- coding： utf-8 -*-

import base64
import os
import random
import time

import demo
import slide
import match
import utils
from lib.config import config as cfg

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

'''
破解Geetest验证码，使用像素对比和OpenCV
成功率13/24

2019.05.05 大更新
'''


class CrackGeetest:

    def __init__(self):
        self.url = "https://www.geetest.com/Sensebot"
        chrome_option = webdriver.ChromeOptions()
        chrome_option.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        chrome_option.add_argument('--log-level=3')
        self.browser = webdriver.Chrome(
            executable_path='E:\\FirstSemesterofSeniorYear\\Self-studyMaterials_DLML\\Python\\tesserocr\\'
                            'netease\\chromedriver.exe',
            chrome_options=chrome_option)

        self.wait = WebDriverWait(self.browser, 15)
        self.zoom = 1
        self.flag = False
        self.success = 0
        self.unsucc = 0
        self.slicename = "all_type/jy/slice_demo.png"
        self.bgname = "all_type/jy/bg_demo.png"
        # self.sess = None
        # self.net = None
        # self.dis = [5, 10, 15, 25, 20, 30, 40, 50, 0]  # 初始时有一个随机位移，只要一碰按钮就会触发

    def open_browser(self):
        time.sleep(random.uniform(0.1, 0.5))
        # WebDriverWait(driver, 超时时长, 调用频率[默认0.5], 忽略异常).until(可执行方法, 超时时返回的信息)
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gt-en-mobile"]/section[5]/div/div[2]/div[1]/ul/li[2]')))
        # WebDriverWait(self.browser, 10, 0.5).until(EC.element_to_be_clickable((By.XPATH,
        # '//*[@id="gt-sensebot-mobile"]/div[2]/section[3]/div/div[2]/div[1]/ul/li[2]')))

        # 点击 滑动验证
        slide_btn = self.browser.find_element_by_xpath('//*[@id="gt-en-mobile"]/section[5]/div/div[2]/div[1]/ul/li[2]')
        # slideBtn = self.browser.find_element_by_xpath('//*[@id="gt-sensebot-mobile"]/div[2]/section[3]/div/div[2]/
        # div[1]/ul/li[2]')
        slide_btn.click()

        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="captcha"]/div[3]/div[2]/div[1]/div[3]')))
        # 鼠标移动到拖动按钮，点击一下显示验证码图片
        element = self.browser.find_element_by_xpath('//*[@id="captcha"]/div[3]/div[2]/div[1]/div[3]')
        element.click()
        if self.is_success('geetest_success_radar_tip_content', 'Verification Succeeded'):
            # 点击直接通过验证
            print("破解成功！耗时: ", 0)
            self.success += 1
            print("成功次数: ", self.success)
            self.browser.refresh()
            self.open_browser()

    def get_image(self):
        # 保存图片，带凹槽但是不带滑块
        # 先刷新
        # element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'geetest_refresh_1')))
        # element.click()
        # 延迟2秒保证能够获取到canvas
        time.sleep(2)
        # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_slicebg')))
        # 下面的js代码根据canvas文档说明而来
        js = 'return document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL();'
        # 执行 JS 代码并拿到图片 base64 数据
        bg_info = self.browser.execute_script(js)  # 执行js文件得到带图片信息的图片数据
        bg_base64 = bg_info.split(',')[1]  # 拿到base64编码的图片信息
        bg_bytes = base64.b64decode(bg_base64)  # 转为bytes类型
        with open(self.bgname, 'wb') as f:  # 保存图片到本地
            f.write(bg_bytes)
        # 保留在/data/demo/下一份
        im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', "target_jy.png")
        with open(im_file, 'wb') as f:  # 保存canvas图片到demo
            f.write(bg_bytes)
        # 保存slice图像
        js = 'return document.getElementsByClassName("geetest_canvas_slice geetest_absolute")[0].toDataURL();'
        slice_bytes = base64.b64decode(self.browser.execute_script(js).split(',')[1])  # 转为bytes类型
        with open(self.slicename, 'wb') as f:  # 保存图片到本地
            f.write(slice_bytes)
        # 加载原始slice图片
        img = Image.open(self.slicename)
        # 若是全屏即是这个260，否则是235
        self.zoom = 260 / img.size[0]
        print("zoom是：", 260 / img.size[0])
        # 对图片进行截图处理，因为保存下来的是一张260×160的透明图片，截取长条58×160即可
        img2 = img.crop((0, 0, 58, 160))
        img2.save(self.slicename, 'PNG')

    def is_exist_element(self, elem):
        s = self.browser.find_elements_by_class_name(elem)
        if len(s) == 0:
            print("不存在%s，循环继续..." % elem)
            return False
        if len(s) == 1:
            print("存在元素%s..." % s)
            return True
        else:
            print("存在%s个元素分别是%s" % (len(s), s))
            return True

    def is_success(self, class_con, content):
        try:
            self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, class_con), content))
            return True
        except:
            return False

    # 方法1，先使用像素对比找到纯背景图片，然后再像素对比找到凹槽位置
    # def crack1(self):
    #     # 打开浏览器，定位标签位置
    #     self.open_browser()
    #     # 下载图片
    #     self.get_image()
    #     imgname = self.find_bg()
    #     print("image name: ", imgname)
    #     if imgname == 'error':
    #         print("出错了！")
    #     else:
    #         full_image = Image.open('bgimg/'+imgname+'.png')
    #         north_image = Image.open('fe.png')
    #         #原图大小260实际不全屏的话235，缩放比例0.9，如果全屏就是1，这写死了
    #         distance = utils.get_offset_distance(cut_image, north_image, "all_type/jy/", 20)*0.9
    #         print("realistic distance: ", distance)
    #         for x in self.dis:
    #             if not self.is_success('geetest_success_radar_tip_content', 'Verification Succeeded'):
    #                 print("自动破解中...")
    #                 self.start_move(distance-x)
    #             else:
    #                 print("破解成功！")
    #                 self.driver.close()
    #                 return True
    #         print("此次破解失败")

    # target是在demo里面的名字
    # def match4(self, target):
    #     distance = demo.demo_customize(self.sess, self.net, target) * self.zoom
    #     return distance

    # 方法2，直接深度学习或者使用opencv定位
    def crack2(self):
        time.sleep(random.uniform(0.8, 1.5))
        time1 = time.time()
        # 下载图片
        self.get_image()
        # 原图大小260实际未全屏时235，缩放比例0.9，全屏为1
        distance = match.match_255("all_type/jy/", self.bgname, self.slicename, "demo") * self.zoom
        print("realistic distance: ", distance)
        print("开始自动破解中...")

        self.start_move(distance)
        time2 = time.time()
        if not self.is_success('geetest_success_radar_tip_content', 'Verification Succeeded'):
            self.unsucc += 1
            print("破解失败，失败次数: ", self.unsucc)
            print("耗时： ", time2 - time1)
            if self.is_exist_element('geetest_radar_error'):
                print("次数过多，重试")
                # 点击重试
                element = WebDriverWait(self.browser, 10, 0.5).until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="captcha"]/div[3]/div[2]/div[1]/div[3]/span[2]')))
                element.click()

            if self.is_success('geetest_result_content', 'Try again in 3 seconds'):
                print("try again in 3 seconds")
                # time1 = time.time()
                # self.get_image()
                # # 原图大小260实际未全屏时235，缩放比例0.9，全屏为1
                # distance = match.match_255("all_type/jy/", self.bgname, self.slicename, "demo") * self.zoom
                # print("realistic distance: ", distance)

        else:
            print("破解成功！耗时: ", time2 - time1)
            self.success += 1
            print("成功次数: ", self.success)
            time.sleep(random.uniform(0.6, 3.0))
            self.browser.refresh()
            self.open_browser()
            # self.crack2()

    # 开始移动
    def start_move(self, distance):
        time.sleep(2)

        element = self.browser.find_element_by_xpath("//div[@class='geetest_slider_button']")
        # 按下鼠标左键
        ActionChains(self.browser).click_and_hold(element).perform()
        # 第一次获取滑块的位置
        # left1 = utils.get_position(self.browser, "geetest_canvas_slice")
        # print("left1: ", left1)

        # 1、使用getBoundingClientRect()移动一个像素还是获得的位置无变化
        # js = "return document.getElementsByClassName('geetest_canvas_slice')[0].getBoundingClientRect().left"
        # _left = self.browser.execute_script(js)
        # print(_left)

        # 先滑动一个像素
        ActionChains(self.browser).move_by_offset(xoffset=1, yoffset=0).perform()
        # 将背景图片隐藏，这时只显示滑块，背景透明
        self.browser.execute_script('document.querySelectorAll("canvas")[0].style="display: none;"')
        # 保存只有slide的透明图像
        js = 'return document.getElementsByClassName("geetest_canvas_slice geetest_absolute")[0].toDataURL();'
        slice_bytes = base64.b64decode(self.browser.execute_script(js).split(',')[1])  # 转为bytes类型
        imname = 'all_type/jy/cal_len.png'
        with open(imname, 'wb') as f:  # 保存图片到本地
            f.write(slice_bytes)
        # 2、使用location获得的位置无变化
        # time.sleep(0.5)
        # 第二次获取左边界的位置
        # left2 = utils.get_position(self.browser, "geetest_canvas_slice")
        # print("left2: ", left2)
        # shake_len = left2 - left1
        # 第二次使用getBoundingClientRect()移动一个像素还是获得的位置无变化
        # js = "return document.getElementsByClassName('geetest_canvas_slice')[0].getBoundingClientRect().left"
        # _left = self.browser.execute_script(js)
        # print(_left)
        # print("shake length: ", shake_len)

        im = Image.open(imname)
        # 3、成功！计算开始移动时的抖动，使用对比法，先让它移动一个像素，然后对比距离左边的距离，算出位置差即可，
        # 不用遍历位置数组随缘命中了，这样成功率剧增！！
        shake_len = utils.get_shake(im) - 1
        print("shake_len: ", shake_len)
        # 将背景显示出来，恢复
        self.browser.execute_script('document.querySelectorAll("canvas")[0].style=""')
        # slide.go_slide_2(distance - shake_len, self.browser, element)
        # slide.go_slide_3(distance - shake_len, self.browser, element)
        # slide.go_slide_log(distance - shake_len, 4, self.browser, element)
        # slide.go_slide_sigmoid(distance - shake_len, self.browser, element)
        # slide.go_slide_direct(distance - shake_len, self.browser, element)  # 0%
        slide.go_slide_uniform(distance - shake_len, self.browser, element, 2)

    def find_bg(self):
        path = "E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML/Python/tesserocr/Geetest/crackGeetest/bgimg/"
        # 该文件夹下所有的文件（包括文件夹）
        filelist = os.listdir(path)
        filename = "error"
        # 遍历所有文件filelist:
        # 原来的文件路径
        for file in filelist:
            olddir = os.path.join(path, file)
            # 如果是文件夹则跳过
            if os.path.isdir(olddir):
                continue
            # 文件名
            filename = os.path.splitext(file)[0]
            # 判断颜色是否相近，计算色差
            fepx = Image.open(self.bgname).getpixel((190, 100))
            bgpx = Image.open(olddir).getpixel((190, 100))
            if utils.is_similar_color(fepx, bgpx):
                print("找到背景了！")
                break
        return filename


if __name__ == '__main__':
    cg = CrackGeetest()
    # cg.sess, cg.net = demo.faster_detect()
    cg.browser.get(cg.url)
    cg.browser.maximize_window()
    cg.open_browser()
    times = 5
    while times > 0:
        cg.crack2()
        times -= 1
    print("success rate: ", cg.success/(cg.success+cg.unsucc))

