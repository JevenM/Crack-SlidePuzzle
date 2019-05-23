from pylab import *
import random
import math

import darw


def return_left(b):
    print("sigmoid函数接受的distance: ", b)
    k = random.randint(20, 50)
    D = []
    for j in range(k):
        if j == 0:
            y = float('%.4f' % ((1 / (1.0 + math.e ** (-1 / 2 + 4))) * b))
            D.append(y)
        elif j == k - 1:
            y = float('%.4f' % ((1 - (1 / (1.0 + math.e ** (-(j + 1) / 2 + 4)))) * b))
            D.append(y)
        else:
            y = float(
                '%.4f' % (((1 / (1 + (math.e ** (-(j + 1) / 2 + 4)))) - (1 / (1 + (math.e ** (-j / 2 + 4))))) * b))
            D.append(y)
    # random.shuffle(D)
    print("sum D: ", sum(D))
    b = [int(i) for i in D]
    print("sum int(D): ", sum(b))
    return D


def write_log():
    file = open('machine\machine_track.txt', 'a')

    for k in range(5):
        l = random.randint(100, 200)
        # over = random.randint(20, 70)
        # low = -random.randint(20, 70)
        # 将log生成的轨迹写入文件

        # y轴的数据
        y = darw.ret_log_4(l)
        D = []
        file.writelines(str(y) + '\n')

        summary = 0
        for j in range(len(y)):
            summary += y[j]
            D.append(summary)
        print("lenth(D): ", len(D))
        # x轴
        x = []
        for i in range(len(D)):
            x.append(i)

        plt.plot(x, D)
        # 取消Y轴和x轴刻度
        plt.xticks([])
        plt.yticks([])
        plt.savefig("machine/log" + str(k+5) + ".png")
        plt.close()
    file.close()


def write_sigmoid():
    file = open('machine\machine_track.txt', 'a')


    for k in range(5):
        l = random.randint(100, 200)
        # over = random.randint(20, 70)
        # low = -random.randint(20, 70)
        y = return_left(l)
        D = []
        file.writelines(str(y) + '\n')

        summary = 0
        for j in range(len(y)):
            summary += y[j]
            D.append(summary)
        print("lenth(D): ", len(D))
        x = []
        for i in range(len(D)):
            x.append(i)

        plt.plot(x, D)
        plt.xticks([])
        plt.yticks([])
        plt.savefig("machine/sigmoid" + str(k) + ".png")
        plt.close()
    file.close()


def read_human():
    # 读的是我滑动自己部署的类似淘宝的滑动验证码
    file = open('human\human_track.txt', 'r')
    summary = 0
    lines = file.readlines()
    for index in range(5):
        line_num = random.randint(0, 41)
        line = lines[line_num]
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
        D = []
        for j in range(len(l)):
            summary += l[j]
            D.append(summary)
        print("lenth(D): ", len(D))
        x = []
        for i in range(len(D)):
            x.append(i)

        plt.plot(x, D)
        plt.xticks([])
        plt.yticks([])
        plt.savefig("human/" + str(line_num) + ".png")
        plt.close()
    file.close()


if __name__ == '__main__':
    write_sigmoid()
    # read_human()
    # write_log()
