# coding=utf-8
# !/usr/bin/env python3
import time

from lib.utils import getTime
from subprocess import Popen, PIPE
import os

flagDict = {}


class xrayProcess():
    def __init__(self,url):
        self.url = url

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../tools/xray/')
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        popen = Popen('./xray ws --basic-crawler %s --html-output ../../xrayresult/%s.html' % (
            self.url,getTime('%Y%m%d%H%M%S')), stdout=PIPE, shell=True, env=env)
        try:
            while True:
                line = popen.stdout.readline().decode('utf-8')
                if line:
                    try:
                        print(line,end='')
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
        while True:
            try:
                result = mysql.execute('select id,url from domains where remark = "scan" limit 0,1;')[0]
            except IndexError:
                print('无子域名，等待5分钟。')
                time.sleep(300)
            mysql.execute('delete from domains where id=%s;', (result['id']))
            xrayProcess(result['url']).run()

    except KeyboardInterrupt:
        pass
    finally:
        mysql.execute('insert into domains(id,url) value(%s,%s);', (result['id'],result['url']))