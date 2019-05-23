import time
from io import BytesIO
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

import base64

import slide
import utils

EMAIL = 'm@m.com'
PASSWORD = '123456'


# 后台登录，通过率很高

class CrackGeetest(object):

    def __init__(self):
        self.url = 'https://account.geetest.com/login'
        chrome_option = webdriver.ChromeOptions()
        chrome_option.add_argument('--log-level=3')
        self.browser = webdriver.Chrome(chrome_options=chrome_option)
        self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 5)
        self.email = EMAIL
        self.password = PASSWORD
        self.success = False
        self.try_num = 4
        self.now_num = 4
        self.fresh_num = 1
        self.zoom = 1
        self.bgname = ''
        self.northname = ''

    def __del__(self):
        self.browser.close()

    # 获取初始验证按钮
    def get_geetest_button(self):
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        return button

    # 获取滑块对象
    def get_slider(self):
        try:
            slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        except Exception:
            self.crack()
            return
        return slider

    # 获取验证码图片
    def get_geetest_image(self):
        """
        获取验证码图片
        :return: 图片对象
        """
        # 等待一段时间，以便完全加载js
        time.sleep(2)
        # 将slice滑块从背景图片上方隐藏
        self.browser.execute_script('document.querySelectorAll("canvas")[1].style="display: none;"')
        # 保存带有凹槽的图像
        js = 'return document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL();'
        slice_bytes = base64.b64decode(self.browser.execute_script(js).split(',')[1])  # 转为bytes类型
        self.bgname = 'all_type/jy/notch_bg_login.png'
        with open(self.bgname, 'wb') as f:  # 保存图片到本地
            f.write(slice_bytes)

        # 将凹槽阴影从背景图片上隐藏，display:none
        self.browser.execute_script('document.querySelectorAll("canvas")[2].style=""')
        # 保存纯色背景图像
        js = 'return document.getElementsByClassName("geetest_canvas_fullbg geetest_fade geetest_absolute")[' \
             '0].toDataURL(); '
        slice_bytes = base64.b64decode(self.browser.execute_script(js).split(',')[1])  # 转为bytes类型
        self.northname = 'all_type/jy/pure_bg_login.png'
        with open(self.northname, 'wb') as f:  # 保存图片到本地
            f.write(slice_bytes)
        # 加载纯色图片
        img = Image.open(self.bgname)
        # 若是全屏即是这个260，否则是235
        self.zoom = 260 / img.size[0]
        print("zoom是：%f, 宽度: %d" % (260 / img.size[0], img.size[0]))
        # 还原，以便显示凹槽和滑块
        self.browser.execute_script('document.querySelectorAll("canvas")[1].style=""')
        self.browser.execute_script('document.querySelectorAll("canvas")[2].style="display: none;"')

    # 打开页面,输入账号与密码
    def open(self):
        self.browser.get(self.url)
        time.sleep(0.5)
        email = self.browser.find_elements_by_xpath("//i[@class='icon-email']/../../input")[0]
        password = self.browser.find_element_by_xpath("//i[@class='icon-password']/../../input")
        email.send_keys(self.email)
        password.send_keys(self.password)

    # 拖动滑块到缺口处
    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def crack(self):
        # 输入用户名密码
        self.open()

        # 点击验证按钮
        time.sleep(1)
        button = self.get_geetest_button()
        button.click()

        # BOREDER：7，原滑块图片的左边缘
        def slider_try(gap):
            if self.now_num:
                # 减去缺口位置
                gap -= 7
                # 计算滑动距离
                track = slide.get_track(int(gap))

                # 拖动滑块
                slider = self.get_slider()
                self.move_to_gap(slider, track)
                try:
                    self.success = self.wait.until(
                        EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
                except Exception as e:
                    self.now_num -= 1
                    test_num = self.try_num - self.now_num  # type: int
                    if self.now_num == 0:
                        print("第%d次尝试失败, 验证失败" % test_num)
                    else:
                        print("验证失败,正在进行第%d次尝试" % test_num)

        while not self.success and self.now_num > 0:
            distance = self.get_img_distance()
            if distance == -1:
                print("阈值不合适，没找到凹槽位置")
            else:
                print("distance: ", distance)
                # gap减少７
                slider_try(distance)
            # if not self.success:
            #     distance = self.get_img_distance()
            #     if distance == -1:
            #         print("阈值不合适，没找到凹槽位置")
            #     else:
            #         print("distance: ", distance)
            #         # gap减少７
            #         slider_try(distance)
            # 成功后退出
            if self.success:
                test_num = self.try_num - self.now_num + 1
                print("第{}次刷新,第{}次尝试,验证通过".format(self.fresh_num, test_num))
                time.sleep(5)
                self.success = True

        if not self.success:
            print("重新刷新页面,这是第%d次刷新" % self.fresh_num)
            self.fresh_num += 1
            self.now_num = 2
            self.try_num = 2
            self.crack()

    def get_img_distance(self):
        # 获取验证码图片
        try:
            self.get_geetest_image()
        except Exception as e:
            # todo: 判断是其他验证，或者是自动识别通过
            self.success = True
            print("自动识别通过，无需滑动%s" % e)
            time.sleep(5)
            return -1

        # 获取缺口位置
        full_image = Image.open(self.bgname)
        cut_image = Image.open(self.northname)
        distance = utils.get_offset_distance(cut_image, full_image, "all_type/jy/", 110)
        return distance


if __name__ == '__main__':
    crack = CrackGeetest()
    crack.crack()
    del crack

# reference：https://blog.csdn.net/weixin_40576010/article/details/89255933
