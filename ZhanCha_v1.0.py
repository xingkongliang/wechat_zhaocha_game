#! /usr/bin/env python
# -*- coding:utf8 -*-
# __author__ : "ZhangTianliang"
# Date: 2018/1/16

import os
import sys
import subprocess
import shutil
import time
import math
from PIL import Image, ImageDraw
import random
import json
import re
import matplotlib.pyplot as plt
import cv2
import numpy as np


def pull_screenshot():
    global screenshot_way
    # 新的方法请根据效率及适用性由高到低排序
    if screenshot_way == 2 or screenshot_way == 1:
        process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
        screenshot = process.stdout.read()
        if screenshot_way == 2:
          binary_screenshot = screenshot.replace(b'\r\n', b'\n')
        else:
          binary_screenshot = screenshot.replace(b'\r\r\n', b'\n')
        f = open('scan_screen.png', 'wb')
        f.write(binary_screenshot)
        f.close()
    elif screenshot_way == 0:
        os.system('adb shell screencap -p /sdcard/scan_screen.png')
        os.system('adb pull /sdcard/scan_screen.png .')

def dump_device_info():
    size_str = os.popen('adb shell wm size').read()
    device_str = os.popen('adb shell getprop ro.product.model').read()
    density_str = os.popen('adb shell wm density').read()
    print("如果你的脚本无法工作，上报issue时请copy如下信息:\n**********\
        \nScreen: {size}\nDensity: {dpi}\nDeviceType: {type}\nOS: {os}\nPython: {python}\n**********".format(
            size=size_str.strip(),
            type=device_str.strip(),
            dpi=density_str.strip(),
            os=sys.platform,
            python=sys.version
    ))


def check_adb():
    flag = os.system('adb devices')
    if flag == 1:
        print('请安装ADB并配置环境变量')
        sys.exit()

def check_screenshot():
    global screenshot_way
    if os.path.isfile('scan_screen.png'):
        os.remove('scan_screen.png')
    if (screenshot_way < 0):
        print('暂不支持当前设备')
        sys.exit()
    pull_screenshot()
    try:
        Image.open('./scan_screen.png')
        print('采用方式{}获取截图'.format(screenshot_way))
    except:
        screenshot_way -= 1
        check_screenshot()

def backup_screenshot(ts):
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)
    shutil.copy('scan_screen.png', '{}{}.png'.format(screenshot_backup_dir, ts))


def read_image():
    pull_screenshot()
    im = cv2.imread('./scan_screen.png')
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    if Challenge_Mode:
        region1 = im[218:1042, 199:1023, :]
        w = 1023 - 199
        h = 1042 - 218
        region2 = im[1117:1117 + h, 199:199 + w, :]
    else:
        region1 = im[287:1110, 214:1039, :]
        w = 1039 - 214
        h = 1110 - 287
        region2 = im[1147:1147 + h, 214:214 + w, :]
    return im, region1, region2


def attention():
    global im_color
    im, region_1, region_2 = read_image()
    output = region_1 - region_2
    img2gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    eq = cv2.equalizeHist(img2gray)  # 灰度图像直方图均衡化
    im_color = cv2.applyColorMap(eq, cv2.COLORMAP_JET)
    ts = int(time.time())
    cv2.imwrite('{}result_{}.png'.format(screenshot_backup_dir, ts), im_color).savefig()

def mouse_action(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:
        if Challenge_Mode:
            x_bias = 199
            y_bias = 218
        else:
            x_bias = 214
            y_bias = 287
        x1 = x + x_bias
        y1 = y + y_bias
        x2 = x + x_bias
        y2 = y + y_bias
        cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            duration=200
        )
        print(cmd)
        os.system(cmd)
    elif event == cv2.EVENT_RBUTTONDOWN:
        attention()


def sleep(mytime=''):
    time.sleep(mytime)


if __name__ == '__main__':
    global Challenge_Mode
    Challenge_Mode = False
    screenshot_way = 2

    if Challenge_Mode:
        screenshot_backup_dir = 'zhaocha_challenge_screen_backups/'
    else:
        screenshot_backup_dir = 'zhaocha_screen_backups/'
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)

    dump_device_info()
    check_adb()
    check_screenshot()
    attention()
    while True:
        cv2.imshow('image', im_color)
        cv2.setMouseCallback('image', mouse_action)
        sleep(0.5)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    cv2.destroyAllWindows()









