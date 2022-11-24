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
            self.exepopen = Popen('./xray ws --basic-crawler %s --html-output ../../xrayresult/%s.html' % (
            self.url,getTime('%Y%m%d%H%M%S')), stdout=PIPE, shell=True, env=env)
        elif self.type == 'nuclei':
            self.exepopen = Popen('../nuclei -l ../../nucleitarget.txt -rl 300 -bs 35 -c 30 -mhe 10 -ni -o ../../xrayresult/%s-nuclei.txt -stats -silent -severity critical,medium,high,low' % (
                getTime('%Y%m%d%H%M%S')), stdout=PIPE, shell=True, env=env)
        try:
            while True:
                line = self.exepopen.stdout.readline().decode('utf-8')
                if line:
                    try:
                        print(line,end='')
                    except:
                        pass
                elif not line and self.exepopen.poll() != None:
                    break
                else:
                    pass
        except Exception as e:
            print(e)
        finally:
            self.exepopen.kill()

def scan(mysql):
    try:
        while True:
            type = ''
            try:
                result = mysql.execute('select id,url,remark from domains where remark = "scan" limit 0,1;')[0]
                type = 'scan'
            except IndexError:
                try:
                    result = mysql.execute('select id,url,remark from domains where remark = "bountyscan" limit 0,500;')
                    type = 'bountyscan'
                    ids = []
                    with open('nucleitarget.txt', 'w')as nfile:
                        for row in result:
                            nfile.write(row['url']+'\n')
                            ids.append(row['id'])
                except IndexError:
                    print('无子域名，等待5分钟。')
                    time.sleep(300)

            mysql.execute('delete from domains where id=%s;',args=ids)
            if type == 'scan':
                scanProcess(result['url'], type).exe()
            elif type == 'bountyscan':
                scanProcess('',type).exe()

    except KeyboardInterrupt:
        pass
    finally:
        mysql.execute('insert into domains(id,url,remark) value(%s,%s,%s);', args=result)