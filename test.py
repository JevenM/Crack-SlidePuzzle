# -*- coding:utf-8 -*-
import demo

if __name__ == "__main__":
    sess, net = demo.faster_detect()
    distance = demo.demo_customize(sess, net, "xxx.jpg")
    print(distance)
    # sys.exit(0)

