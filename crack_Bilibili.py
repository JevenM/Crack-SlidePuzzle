import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INIT_LEFT = 60


class CrackGeetest():
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'
        chrome_option = webdriver.ChromeOptions()
        # chrome_option.set_headless()
        chrome_option.add_argument('--log-level=3')
        chrome_option.binary_location = r"D:\\Google\Chrome\\Application\chrome.exe"
        self.browser = webdriver.Chrome(r"E:/FirstSemesterofSeniorYear/Self-studyMaterials_DLML/Python/tesserocr/netease/chromedriver", chrome_options=chrome_option)
        self.wait = WebDriverWait(self.browser, 20)

    def __del__(self):
        self.browser.close()

    def open(self):
        self.browser.get(self.url)

    def move_to_slider(self):
        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_slider_knob')))
        ActionChains(self.browser).move_to_element(slider).perform()
        #截图保存
        image1 = self.get_image("c1.png")
        time.sleep(2)
        ActionChains(self.browser).release().perform()
        return image1

    def hold_slider(self):

        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_slider_knob')))
        ActionChains(self.browser).click_and_hold(slider).perform()
        # 赶快截屏
        image2 = self.get_image("c2.png")
        return image2


    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_box_holder')))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()  #Gets the screenshot of the current window as a binary data.
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        left = 75
        print("image1.width:%d, height:%d" % (image1.size[0],image1.size[1]))
        for i in range(left, image1.size[0], 1):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 50 #固定阈值
        print("x:", x)
        if (abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(pixel1[2] - pixel2[2]) < threshold):
            # print("pixel1[0] - pixel2[0]:%d, pixel1[1] - pixel2[1]:%d, pixel1[2] - pixel2[2]:%d" % (pixel1[0] - pixel2[0],pixel1[1] - pixel2[1],pixel1[2] - pixel2[2]))
            return True
        else:
            # print("!!pixel1[0] - pixel2[0]:%d, pixel1[1] - pixel2[1]:%d, pixel1[2] - pixel2[2]:%d" % (pixel1[0] - pixel2[0],pixel1[1] - pixel2[1],pixel1[2] - pixel2[2]))
            return False

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 7
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2.8
            else:
                # 加速度为负3
                a = -4
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        # ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def crack(self):
        # 输入用户名密码
        self.open()
        time.sleep(2)
        # 点击验证按钮
        image1 = self.move_to_slider()
        image2 = self.hold_slider()
        
        # 获取缺口位置
        gap = self.get_gap(image1, image2)
        print('缺口位置', gap)
        # 获取移动轨迹
        track = self.get_track(gap-22)
        print('滑动轨迹', track)
        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_slider_knob')))
        # 拖动滑块
        self.move_to_gap(slider, track)

        try:
            success = self.wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="gc-box"]/div/div[1]/div[2]/div[2]/div/div[2]/span[1]'), '验证成功:'))
            print(success)
            pass
        except Exception as e:
            self.crack()


if __name__ == '__main__':
    crack = CrackGeetest()
    crack.crack()