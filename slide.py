# -*- coding:utf-8 -*-
# @Time    : 5/5/2019 2:44 PM
# @Author  : maoge
# @File    : sllide.py
# @Software: PyCharm
# @desc    : ways to slide the block
import math
import numpy as np
import random
import time
from selenium.webdriver import ActionChains


def go_slide_1(distance, browser, element):
    """
    :param distance: distance to slide
    :param browser: your browser object
    :param element: the block to slide
    :return: None
    """
    # time.sleep(0.5)
    v = 0
    t = 0.2
    current = 0
    mid = distance * 3 / 5  # 减速阀值
    ActionChains(browser).click_and_hold(element).perform()
    while current < distance:
        if current < mid:
            a = 2  # 加速度为+2
        else:
            a = -3  # 加速度-3
        s = v * t + 0.5 * a * (t ** 2)
        v = v + a * t
        ActionChains(browser).move_by_offset(xoffset=round(s), yoffset=0).perform()
        current += s

    # 有误差，再往回返回差额就准确了
    ActionChains(browser).move_by_offset(distance - current, 0).release(element).perform()


# 极验
def get_track(distance):
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 0

    while current < distance:
        if current < mid:
            # 加速度为正2
            a = 2
        else:
            # 加速度为负3
            a = -3
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


def go_slide_2(distance, browser, element):
    # 当前位移
    current = 0
    x_1 = float('%.4f' % random.uniform(4 / 5, 6 / 7))
    x_ac = distance * x_1
    t = 0.2
    v = random.randint(0, 2)
    round_move = []
    real_move = []
    while current < distance:
        if current < x_ac:
            a = random.randint(2, 4)
        else:
            a = -random.randint(3, 7)
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        round_move.append(round(move))
        real_move.append(move)
        ActionChains(browser).move_by_offset(xoffset=round(move), yoffset=0).perform()

    ActionChains(browser).move_by_offset(sum(real_move) - sum(round_move), 0).perform()
    # 有误差，再往回返回差额就准确了，其他验证码打开这一行
    ActionChains(browser).move_by_offset(distance - current, 0).release(element).perform()
    # 顶象的验证码要用drag_and_drop_by_offset松开，打开下两行，注释掉上一行
    # ActionChains(browser).move_by_offset(distance - current, 0).perform()
    # ActionChains(browser).drag_and_drop_by_offset(element, 0, 0).perform()


# 模仿人类实际轨迹滑动...
def go_slide_3(distance, browser, element):
    with open('human/human_track.txt', 'r') as f:
        # 读取所有的行
        lines = f.readlines()
        # 行索引的最大数
        max = len(lines) - 1
        # 生成随机行数
        num = random.randint(20, max)
        print("index: ", num)
        # 取得对应行内容
        line = lines[num]
        # 把末尾的'\n'和'['删掉
        l = line.strip('[').strip()
        # 去掉最后一个']'
        l = l[0:len(l) - 1]
        # 分割成list
        x = l.split(",")
        # str转换为int类型
        l = [int(x[i]) for i in range(len(x))]
        # 打印所有元素之和
        print('sum(l): ', sum(l))
        # 我收集的人类轨迹长度和此验证码需要滑动长度的比
        ratio = (sum(l) + 1) / distance  # print("l: ", l)
        # 经过除以比例计算得到应用到此验证码上的具有人类特征的轨迹
        newx = [int(x[i]) / ratio for i in range(len(x))]
        print("sum(newx): ", sum(newx))
        # 转化为整数，不然滑动会在中间停止，比如不能offset滑动0.58838个像素...不知道为什么，其他函数轨迹就可以
        newx_integer = [round(int(x[i]) / ratio) for i in range(len(x))]
        print("sum(new_integer): ", sum(newx_integer))
        # 经过四舍五入转化为整数之后，计算一下差值，表示要减去的值
        difference = sum(newx_integer) - sum(newx)
        print("difference: ", difference)
        if difference >= 0:
            # 随机在整数list中间找几个数，每次减去一就行
            p = 0
            while p < difference:
                index = random.randint(0, len(newx_integer) - 1)
                if newx_integer[index] > 1:
                    newx_integer[index] -= 1
                    p += 1
        else:
            p = 0
            while p > difference:
                index = random.randint(0, len(newx_integer) - 1)
                newx_integer[index] += 1
                p -= 1
    for i in newx_integer:
        ActionChains(browser).move_by_offset(xoffset=i, yoffset=0).perform()
    time.sleep(0.5)
    ActionChains(browser).release(element).perform()


# log()
def go_slide_log(distance, div, browser, element):
    print("log函数接受的distance: ", distance)
    # x记录0,1,2,3
    x = []
    # y记录每一小段的轨迹
    y = []
    i = 0
    # 每一小段的长度
    k = int(distance / div)
    before = 0
    tmp = math.e ** (distance / k)
    # print("tmp: ", tmp)
    while i < tmp:
        x.append(i)
        # log默认底数为e
        after = math.log(i + 1) * k
        if i == 0:
            y.append(float('%.4f' % (after - before)))
        else:
            y.append(float('%.4f' % (after - before + random.uniform(-0.5, 0.5))))
        before = after
        i += 1
    # 间隔，分20次将剩余的部分赋值给y
    interval = (distance - sum(y)) / 5.0
    for j in range(5):
        y.append(float('%.4f' % interval))
    # 上面三行等同于这一行
    # y.append(distance - sum(y))

    b = [int(i) for i in y]
    # 返回y，即是轨迹
    print("sum y: ", sum(y))
    # 对比真实浏览器窗口中出现的距离，和这个值很相似，说明返回的数组y的sum和是过大的，而正因为在滑动过程中不能滑动分数个像素，所以应该在xoffset=track处被转化为整数
    print("sum int(y): ", sum(b))
    ii = 0
    diff = round(sum(y)) - sum(b)
    print("(round(sum(y)) - sum(b)：", diff)
    while ii < diff:
        index = random.randint(0, len(b) - 1)
        b[index] += 1
        ii += 1
    print("sum b: ", sum(b))
    for i in b:
        ActionChains(browser).move_by_offset(xoffset=i, yoffset=0).perform()
    # 同盾打开下三行
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    time.sleep(0.2)
    ActionChains(browser).release(element).perform()
    # 顶象注释上一行打开下一行
    # ActionChains(browser).drag_and_drop_by_offset(element, 0, 0).perform()


# sigmoid()
def go_slide_sigmoid(distance, browser, element):
    # def go_slide_sigmoid(distance):
    print("sigmoid函数接受的distance: ", distance)
    k = random.randint(20, 50)
    D = []
    for j in range(k):
        if j == 0:
            y = float('%.4f' % ((1 / (1.0 + math.e ** (-1 / 2 + 4))) * distance))
            D.append(y)
        elif j == k - 1:
            y = float('%.4f' % ((1 - (1 / (1.0 + math.e ** (-(j + 1) / 2 + 4)))) * distance))
            D.append(y)
        else:
            y = float(
                '%.4f' % (((1 / (1 + (math.e ** (-(j + 1) / 2 + 4)))) - (
                            1 / (1 + (math.e ** (-j / 2 + 4))))) * distance))
            D.append(y)
    # random.shuffle(D)
    print("sum D: ", sum(D))
    b = [int(i) for i in D]
    print("sum int(D): ", sum(b))
    ii = 0
    diff = round(sum(D)) - sum(b)
    print("(int(sum(D)) - sum(b)：", diff)
    while ii < diff:
        index = random.randint(0, len(b) - 1)
        b[index] += 1
        ii += 1
    print("sum b: ", sum(b))
    for i in b:
        ActionChains(browser).move_by_offset(xoffset=i, yoffset=0).perform()
    # 同盾打开下三行
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    time.sleep(0.5)

    ActionChains(browser).release(element).perform()
    # 顶象注释掉上一行，打开下一行
    # ActionChains(browser).drag_and_drop_by_offset(element, 0, 0).perform()


# direct
def go_slide_direct(distance, browser, element):
    ActionChains(browser).drag_and_drop_by_offset(element, distance, 0).perform()


# 匀速
def go_slide_uniform(distance, browser, element, b):
    arr = np.full(int(distance/b), b)  # 生成一维数组，元素为b
    for i in arr:
        ActionChains(browser).move_by_offset(xoffset=i, yoffset=0).perform()
    time.sleep(0.2)
    # 同盾验证码需要打开注释
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    # ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()

    ActionChains(browser).release(element).perform()
    # 顶象注释掉上一行，打开下一行
    # ActionChains(browser).drag_and_drop_by_offset(element, 0, 0).perform()


if __name__ == "__main__":
    # go_slide_log(131.89, 4)
    go_slide_sigmoid(131.89)
