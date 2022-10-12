# coding=utf-8
# !/usr/bin/env python3
import sys
from lib.utils import getTime
from lib.sub import Process
from subprocess import Popen, PIPE
import time, re, threading,warnings, os ,telebot
from fake_useragent import UserAgent
from flask import Flask, request

ua = UserAgent(path="fake_ua.json")

warnings.filterwarnings(action='ignore')

app = Flask(__name__)

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
        result = str(resultObj)
        if len(result) > 10*2047:
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

class xrayProcess(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../tools/%s/xray/' % self.port)
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        popen = Popen('./xray ws --listen 127.0.0.1:%s --webhook-output http://127.0.0.1:2233/webhook ----html-output %s' % (
            self.port,getTime()), stdout=PIPE, shell=True, env=env)
        count = 0
        try:
            while True:
                line = popen.stdout.readline().decode('utf-8')
                count += 1
                if line:
                    try:
                        if not flagDict[self.port]['flag'] and 'starting mitm server at 127.0.0.1' in line:
                            # 标记开始
                            flagDict[self.port] = {'flag': True, 'pending': 0}
                            print('[+] 线程 %s 启动完成！'%self.port)
                        if count > 300:
                            pending = pendingre.search().group()
                            if pending:
                                flagDict[self.port]['pending'] = pending.group()
                                count = 0
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

def scan(ports, mysql):
    try:
        appthread = threading.Thread(target=app_run)
        appthread.start()
        print('[+] webhook开启成功')

        #xray线程启动
        ports = ports.split(',')
        print('[+] 共%d个扫描线程，分别为:'%len(ports))
        for port in ports:
            flagDict.setdefault(port, {'flag': False, 'pending': 0,'xrayProcess':None})
            flagDict[port]['xrayProcess'] = xrayProcess(port)
            flagDict[port]['xrayProcess'].start()

        #测试是否启动完成，开始启动rad
        temp = True
        while temp:
            for port in ports:
                if not flagDict[port]['flag']:#只要有存在false就会True跳出，爆出循环了
                    temp = True
                    break
                temp = False

        #首次启动

        for port in ports:
            print('首次启动rad')
            result = mysql.execute('select id,url from domains limit 0,1;')[0]
            mysql.execute('delete from domains where id=%s;',(result['id']))
            flagDict[port]['url'] = result['url']
            print('[+] 当前%s线程扫描目标：%s'%(port,result['url']))
            Process(
                '../../rad/rad -t %s --http-proxy http://127.0.0.1:%s' % (
                    result['url'], port)).exe(outFlag=False)#每个起一个rad扫描


        #监控，xray任务少了rad就开始爬
        while True:
            time.sleep(30)
            for port in flagDict.keys():
                print('[+] %s线程当前任务数: %d'%(port,flagDict[port]['pending']))
                if flagDict[port]['pending'] < 10:#xray任务数小于50
                    result = mysql.execute('select id,url from domains limit 0,1;')[0]
                    mysql.execute('delete from domains where id=%s;', (result['id']))
                    print('[+] 当前%s线程扫描目标：%s' % (port, result['url']))
                    flagDict[port]['url'] = result['url']
                    Process(
                        '../../rad/rad -t %s --http-proxy http://127.0.0.1:%s' % (
                            result['url'], port)).exe(outFlag=False)  # 每个起一个rad扫描

    except KeyboardInterrupt:
        if len(flagDict):
            for port in ports:
                if flagDict[port]['xrayProcess'].is_alive():
                    mysql.execute('insert into domains(url) value(%s);', (flagDict[port]['url']))
    finally:
        tb.send_message(telegramid, '扫描任务停止')