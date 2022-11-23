# coding=utf-8
# !/usr/bin/env python3

import time

#获取当前时间
def getTime(format='%Y-%m-%d %H:%M:%S'):
    now = time.strftime(format,time.localtime(time.time()))
    return now

