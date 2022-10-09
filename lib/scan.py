# coding=utf-8
# !/usr/bin/env python3

import os
from lib.utils import getTime
from lib.sub import Process


def scan(port):
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../tools/%s/xray/'%port)
    #开始进行xray扫描
    print('开始扫描开启xray监听：')
    Process('./xray ws --listen 127.0.0.1:%s --html-output xray_%s_result.html'%(port,getTime(format='%Y%m%d%H%M%S'))).exe()