# coding=utf-8
# !/usr/bin/env python3
import time

from lib.utils import getTime
from subprocess import Popen, PIPE
import os

class scanProcess():
    def __init__(self,url,type):
        self.url = url
        self.type = type

    def exe(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../tools/xray/')
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'

        if self.type == 'scan':
            exepopen = Popen('./xray ws --basic-crawler %s --html-output ../../xrayresult/%s.html' % (
            self.url,getTime('%Y%m%d%H%M%S')), stdout=PIPE, shell=True, env=env)
        elif self.type == 'nuclei':
            exepopen = Popen('../nuclei -rl 1000 -bs 100 -c 100  -mhe 10 -ni -u %s -o ../../xrayresult/%s-nuclei.txt -stats -silent -severity critical,medium,high,low' % (
                self.url, getTime('%Y%m%d%H%M%S')), stdout=PIPE, shell=True, env=env)
        try:
            while True:
                line = exepopen.stdout.readline().decode('utf-8')
                if line:
                    try:
                        print(line,end='')
                    except:
                        pass
                elif not line and exepopen.poll() != None:
                    break
                else:
                    pass
        except Exception as e:
            print(e)
        finally:
            exepopen.kill()

def scan(mysql):
    try:
        while True:
            try:
                result = mysql.execute('select id,url,remark from domains where remark = "scan" limit 0,1;')[0]
            except IndexError:
                try:
                    result = mysql.execute('select id,url,remark from domains where remark = "bountyscan" limit 0,1;')[0]
                except IndexError:
                    print('无子域名，等待5分钟。')
                    time.sleep(300)

            mysql.execute('delete from domains where id=%s;', (result['id']))
            if result['remark'] == 'scan':
                scanProcess(result['url'], 'xray').exe()
            elif result['remark'] == 'bountyscan':
                scanProcess(result['url'], 'nuclei').exe()

    except KeyboardInterrupt:
        pass
    finally:
        mysql.execute('insert into domains(id,url,remark) value(%s,%s,%s);', (result['id'],result['url'],result['remark']))