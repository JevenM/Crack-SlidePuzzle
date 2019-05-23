# -*- coding:utf-8-*-
import math
import random
import matplotlib.pyplot as plt


def ret_log_4(distance):
    x = []
    y = []
    i = 0
    # b = random.randint(100,200)
    k = int(distance / 4)
    before = 0
    while sum(y) < distance:
        x.append(i)
        after = math.log(i + 1) * k
        y.append(after - before + float('%.4f' % random.uniform(-0.5, 0.5)))
        before = after
        i += 1
    return y



# 返回轨迹, div划分为几段
def ret_log(distance, div):
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
    interval = (distance - sum(y)) / 20.0
    for j in range(20):
        y.append(float('%.4f' % interval))
    # 上面三行等同于这一行
    # y.append(distance - sum(y))

    b = [int(i) for i in y]
    # 返回y，即是轨迹
    # print("sum y: ", sum(y))
    # 对比真实浏览器窗口中出现的距离，和这个值很相似，说明返回的数组y的sum和是过大的，而正因为在滑动过程中不能滑动分数个像素，所以应该在xoffset=track处被转化为整数
    # print("sum int(y): ", sum(b))
    return y
