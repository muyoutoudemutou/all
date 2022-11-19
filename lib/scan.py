# coding=utf-8
# !/usr/bin/env python3

from lib.utils import getTime
from subprocess import Popen, PIPE
import time, re, threading,warnings, os ,telebot
from fake_useragent import UserAgent
from flask import Flask, request

ua = UserAgent(path="fake_ua.json")

warnings.filterwarnings(action='ignore')

app = Flask(__name__)

ignoreVul = []
with open('ignore.conf','r') as ignore:
    for line in ignore.readlines():
        ignoreVul.append(line.strip())

with open('conf.conf','r') as conf:
    token = conf.readline().strip()
    telegramid = conf.readline().strip()

tb = telebot.TeleBot(token)

flagDict = {}

pendingre = re.compile(r'pending: (\d[+])')


@app.route('/webhook', methods=['POST'])
def xray_webhook():
    resultObj=request.json
    if 'vuln' in resultObj['type']:
        print('[+]发现漏洞，地址为%s：'%resultObj['data']['detail']['addr'])
        print('[+]漏洞类型为：%s'%resultObj['data']['plugin'])
        if resultObj['data']['plugin'] in ignoreVul:#垃圾漏洞咱就不推了
            return 'ignore'
        if len(str(resultObj)) > 10*2047:
            resultObj['data']['detail']['snapshot'] = None
        result = str(resultObj)
        if len(result) > 2047:
            for x in range(0, len(result), 2047):
                tb.send_message(telegramid,  result[x:x + 2047])
                time.sleep(0.5)#避免一次性发送太多被报错
        else:
            tb.send_message(telegramid, result)
    return 'ok'


def app_run():
    app.run(host='127.0.0.1',port=2233)#起推送服务


def get_random_headers():
    headers = {'User-Agent': ua.random}
    return headers

class xrayProcess():
    def __init__(self,url):
        self.url = url

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../tools/xray/')
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        popen = Popen('./xray ws --basic-crawler %s --webhook-output http://127.0.0.1:2233/webhook --html-output ../../../xrayresult/%s.html' % (
            self.url,getTime('%Y%m%d%H%M%S')), stdout=PIPE, shell=True, env=env)
        try:
            while True:
                line = popen.stdout.readline().decode('utf-8')
                if line:
                    try:
                        print(line)
                    except:
                        pass
                elif not line and popen.poll() != None:
                    break
                else:
                    pass
        except Exception as e:
            print(e)
        finally:
            popen.kill()

def scan(mysql):
    try:
        appthread = threading.Thread(target=app_run)
        appthread.start()
        print('[+] webhook开启成功')

        while True:
            result = mysql.execute('select id,url from domains limit 0,1;')[0]
            xrayProcess(result['url']).run()
            mysql.execute('delete from domains where id=%s;', (result['id']))

    except KeyboardInterrupt:
        pass
    finally:
        tb.send_message(telegramid, '扫描任务停止')