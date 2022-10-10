# coding=utf-8
# !/usr/bin/env python3

from lib.utils import getTime
from lib.sub import Process
from subprocess import Popen, PIPE, STDOUT
import warnings, simplejson, os
import json, time, re, threading
from fake_useragent import UserAgent
from flask import Flask, request
import telebot

ua = UserAgent(path="fake_ua.json")

warnings.filterwarnings(action='ignore')

app = Flask(__name__)

with open('conf.conf','r') as conf:
    token = conf.readline().strip()
    telegramid = conf.readline().strip()

tb = telebot.TeleBot(token)

@app.route('/webhook', methods=['POST'])
def xray_webhook():
  result=request.json
  if 'vuln' in result['type']:
    tb.send_message(telegramid, str(result))#如果存在漏洞就推送
  return 'ok'

def app_run():
    app.run(host='127.0.0.1',port=2233)#起推送服务

def get_random_headers():
    headers = {'User-Agent': ua.random}
    return headers


class xrayProcess(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../tools/%s/xray/' % self.port)
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        popen = Popen('./xray ws --listen 127.0.0.1:%s --webhook-output 127.0.0.1:2233' % (
            self.port), stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True, env=env)
        try:
            while True:
                line = popen.stdout.readline()
                if line:
                    try:
                        if 'pending: 0' in line:
                            print('%s xray扫描结束' % self.port)
                            popen.kill()
                        elif 'starting mitm server at 127.0.0.1' in line:
                            print('%s xray扫描开始' % self.port)
                    except:
                        pass
                elif not line and popen.poll() != None:
                    break
                else:
                    pass
                time.sleep(0.1)
        except Exception as e:
            print(e)
        print('[+]%s %s命令完成' % (getTime(), self.port))
        popen.kill()


class crawler(threading.Thread):

    def __init__(self, port, url):
        self.port = port
        self.url = url

    def run(self):
        Process(
            './tools/rad/rad -t %s --http-proxy http://127.0.0.1:%s' % (
                 self.url,self.port)).exe(outFlag=False)


class xray_crawler(threading.Thread):

    def __init__(self, port, url):
        self.port = port
        self.url = url

    def run(self):
        # xray监听开始
        xrayProcess(self.port).start()
        time.sleep(15)
        # crawler开始
        crawler(self.port, self.url).start()


def scan(ports, mysql):
    threadDict = {}
    appthread = threading.Thread(target=app_run)
    appthread.start()
    try:
        for port in ports:
            # 获取目标
            result = mysql.execute('select id,url from domains limit 0,1;')[0]
            threadDict.setdefault(port,(xray_crawler(port,result['url']),result['url']))
            threadDict[port][0].start()
            mysql.execute('delete from domains where id=%s', (result['id']))  # 删除
            time.sleep(5)#防止mysql误读
        while True:
            for port in ports:
                if not threadDict[port].isAlive():
                    result = mysql.execute('select id,url from domains limit 0,1;')[0]
                    threadDict.setdefault(port, xray_crawler(port, result['url']),result['url'])
                    threadDict[port][0].start()
                    mysql.execute('delete from domains where id=%s', (result['id']))  # 删除
            if not appthread.is_alive():
                appthread = threading.Thread(target=app_run)
                appthread.start()
            time.sleep(10)
    except KeyboardInterrupt:
        if len(threadDict):
            for port in ports:
                if threadDict[port].isAlive():
                    mysql.execute('replace into domains(url) value(%s);' % threadDict[port][1])