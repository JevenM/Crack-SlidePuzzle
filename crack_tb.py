# _*_coding:UTF-8_*_
"""
date: 2019.04.26/2019.04.30
author: maoge
crack taobao slide-captcha
success rate: 100%
"""

# 使用anaconda的base环境和tensorflow-gpu环境都行了
import numpy as np
import win32api
import win32con
import win32gui
from ctypes import *
import time, random
import webbrowser

import slide

SW = 1920
SH = 1080
VK_CODE = {
    'backspace': 0x08,
    'tab': 0x09,
    'clear': 0x0C,
    'enter': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'pause': 0x13,
    'caps_lock': 0x14,
    'esc': 0x1B,
    'spacebar': 0x20,
    'page_up': 0x21,
    'page_down': 0x22,
    'end': 0x23,
    'home': 0x24,
    'left_arrow': 0x25,
    'up_arrow': 0x26,
    'right_arrow': 0x27,
    'down_arrow': 0x28,
    'select': 0x29,
    'print': 0x2A,
    'execute': 0x2B,
    'print_screen': 0x2C,
    'ins': 0x2D,
    'del': 0x2E,
    'help': 0x2F,
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'a': 0x41,
    'b': 0x42,
    'c': 0x43,
    'd': 0x44,
    'e': 0x45,
    'f': 0x46,
    'g': 0x47,
    'h': 0x48,
    'i': 0x49,
    'j': 0x4A,
    'k': 0x4B,
    'l': 0x4C,
    'm': 0x4D,
    'n': 0x4E,
    'o': 0x4F,
    'p': 0x50,
    'q': 0x51,
    'r': 0x52,
    's': 0x53,
    't': 0x54,
    'u': 0x55,
    'v': 0x56,
    'w': 0x57,
    'x': 0x58,
    'y': 0x59,
    'z': 0x5A,
    'numpad_0': 0x60,
    'numpad_1': 0x61,
    'numpad_2': 0x62,
    'numpad_3': 0x63,
    'numpad_4': 0x64,
    'numpad_5': 0x65,
    'numpad_6': 0x66,
    'numpad_7': 0x67,
    'numpad_8': 0x68,
    'numpad_9': 0x69,
    'multiply_key': 0x6A,
    'add_key': 0x6B,
    'separator_key': 0x6C,
    'subtract_key': 0x6D,
    'decimal_key': 0x6E,
    'divide_key': 0x6F,
    'F1': 0x70,
    'F2': 0x71,
    'F3': 0x72,
    'F4': 0x73,
    'F5': 0x74,
    'F6': 0x75,
    'F7': 0x76,
    'F8': 0x77,
    'F9': 0x78,
    'F10': 0x79,
    'F11': 0x7A,
    'F12': 0x7B,
    'F13': 0x7C,
    'F14': 0x7D,
    'F15': 0x7E,
    'F16': 0x7F,
    'F17': 0x80,
    'F18': 0x81,
    'F19': 0x82,
    'F20': 0x83,
    'F21': 0x84,
    'F22': 0x85,
    'F23': 0x86,
    'F24': 0x87,
    'num_lock': 0x90,
    'scroll_lock': 0x91,
    'left_shift': 0xA0,
    'right_shift ': 0xA1,
    'left_control': 0xA2,
    'right_control': 0xA3,
    'left_menu': 0xA4,
    'right_menu': 0xA5,
    'browser_back': 0xA6,
    'browser_forward': 0xA7,
    'browser_refresh': 0xA8,
    'browser_stop': 0xA9,
    'browser_search': 0xAA,
    'browser_favorites': 0xAB,
    'browser_start_and_home': 0xAC,
    'volume_mute': 0xAD,
    'volume_Down': 0xAE,
    'volume_up': 0xAF,
    'next_track': 0xB0,
    'previous_track': 0xB1,
    'stop_media': 0xB2,
    'play/pause_media': 0xB3,
    'start_mail': 0xB4,
    'select_media': 0xB5,
    'start_application_1': 0xB6,
    'start_application_2': 0xB7,
    'attn_key': 0xF6,
    'crsel_key': 0xF7,
    'exsel_key': 0xF8,
    'play_key': 0xFA,
    'zoom_key': 0xFB,
    'clear_key': 0xFE,
    '+': 0xBB,
    ',': 0xBC,
    '-': 0xBD,
    '.': 0xBE,
    '/': 0xBF,
    '`': 0xC0,
    ';': 0xBA,
    '[': 0xDB,
    '\\': 0xDC,
    ']': 0xDD,
    "'": 0xDE}


class POINT(Structure):
    _fields_ = [("x", c_ulong), ("y", c_ulong)]


class CrackTaobao(object):
    """docstring for Crack_Taobao"""

    def __init__(self):
        super(CrackTaobao, self).__init__()
        self.url = 'https://reg.taobao.com/member/reg/fill_mobile.htm'
        self.succ_count = 0
        self.unsucc_count = 0
        self.chromepath = r"D:\\Google\Chrome\\Application\chrome.exe"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(self.chromepath))

    def get_mouse_point(self):
        po = POINT()
        windll.user32.GetCursorPos(byref(po))
        return int(po.x), int(po.y)

    def mouse_click(self, x=None, y=None):
        if x is not None and y is not None:
            self.mouse_move(x, y)
            time.sleep(round(random.uniform(0.02, 0.07), 2))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(round(random.uniform(0.02, 0.07), 2))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def mouse_move(self, x, y):
        print("x: %d, x: %d" % (x, y))
        windll.user32.SetCursorPos(x, y)

    # 拖动鼠标，
    def mouse_absolute(self, x, y, x2, y2):
        self.mouse_move(x, y)  # 鼠标移动到x,y位置
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)  # 左键按下
        time.sleep(round(random.uniform(0.4, 0.6), 2))

        px, py = self.get_mouse_point()
        print("px: %d, py: %d" % (px, py))

        # 坐标变换
        mw = int(x2 * 65535 / SW)
        mh = int(y2 * 65535 / SH)
        print("mw: %d, mh: %d" % (mw, mh))
        win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE + win32con.MOUSEEVENTF_MOVE, mw, mh, 0, 0)
        time.sleep(round(random.uniform(0.4, 0.6), 2))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)  # 左键松开

    # 在浏览器chrome的url框里输入字符串，并回车进入
    def key_input(self, str_=''):
        for s in str_:
            if s == ':':  # 这时要同时按两个键shift+;
                win32api.keybd_event(16, 0, 0, 0)
                win32api.keybd_event(186, 0, 0, 0)
                win32api.keybd_event(186, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(16, 0, win32con.KEYEVENTF_KEYUP, 0)
            elif s == '_':  # 这时要同时按两个键shift+-
                win32api.keybd_event(16, 0, 0, 0)
                win32api.keybd_event(189, 0, 0, 0)
                win32api.keybd_event(189, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(16, 0, win32con.KEYEVENTF_KEYUP, 0)
            else:
                # print(VK_CODE[c])
                win32api.keybd_event(VK_CODE[s], 0, 0, 0)
                win32api.keybd_event(VK_CODE[s], 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(round(random.uniform(0.01, 0.04), 2))
        time.sleep(0.1)
        # 按下回车输入网址
        win32api.keybd_event(13, 0, 0, 0)  # enter键位码是13
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)  # enter键位码是13
        # 按一下url搜索框
        self.mouse_click(630, 50)
        # 再次回车即为开始搜索
        win32api.keybd_event(13, 0, 0, 0)  # enter键位码是13
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)  # enter键位码是13

    def crack2(self):
        webbrowser.get('chrome').open(self.url, new=1, autoraise=True)
        time.sleep(3)
        log_time1 = time.time()
        times = 1  # 操作次数
        start_x = 878  # x
        # initial_x = start_x
        y = 383  # y coordinate
        end_x = 1144
        # length = end_x - start_x
        every_time = []
        for x in range(times):
            # start_x = initial_x
            if x != 0:
                # 刷新
                self.mouse_click(85, 50)
                log_time1 = time.time()
            time.sleep(2)
            # 点击接受协议
            self.mouse_click(958, 750)
            # self.mouse_move(start_x, y)  # 鼠标移动到x,y位置
            # 获取轨迹，加速度公式
            # tracks = slide.get_track(length)
            # 累加轨迹算出的是每一时刻实际相对于0所在的位置
            # t_x = self.cumulative_sum(tracks)
            # 现在每个元素加上初始点坐标就是相对于起始点的位置了
            # trackx = [i + initial_x for i in t_x]
            # print(trackx)
            # for i in range(len(trackx)-2): # 经过打印发现，逸出，故减去2
            #     self.mouse_absolute(trackx[i], y, trackx[i+1], y)
            # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)  # 左键松开
            self.mouse_absolute(start_x, y, end_x, y)
            log_time2 = time.time()
            every_time.append(log_time2 - log_time1 - 2)
            print("time to crack: ", log_time2 - log_time1 - 2)
            # self.succ_count += 1
        # 一定100%！
        # print("攻击成功率：%f%%" % (self.succ_count / times))
        print("mean time to crack: ", np.mean(every_time))

    # 类似斐波那契数列，后一项是前一项和当前的和
    def cumulative_sum(self, l):
        new_l = [l[0]]
        for old in l[1:]:
            new_l.append(new_l[len(new_l) - 1] + old)
        return new_l

    def crack1(self):
        times = 2  # 操作次数
        start_x = 878  # x
        y = 383  # y coordinate
        end_x = 1144
        for x in range(times):
            # 先点击一下url框，以便输入内容
            self.mouse_click(750, 50)
            # 依次按下键盘相应字符
            self.key_input(self.url)
            # 等待进入网站
            time.sleep(2)
            # 点击接受协议
            self.mouse_click(962, 750)
            # 拖动滑动验证码
            self.mouse_absolute(start_x, y, end_x, y)
            self.succ_count += 1
        print("攻击成功率：%f%%" % (self.succ_count / times))


if __name__ == "__main__":
    c = CrackTaobao()
    '''
    start attack taobao
    '''
    # 1）using win32api, you should open the chrome browser first, and start 'python crack_alibaba.py' over the browser
    # window.
    # c.crack1()
    # 2）using webbroser, you shouldn't open browser first, system will open the browser you specified automately and
    # execute the code.
    c.crack2()
