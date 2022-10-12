#!/usr/bin/env python3
#-*-encoding:utf-8-*-
from subprocess import Popen, PIPE, STDOUT
import os,threading,time
from lib.utils import getTime

# 进程命令执行类
class Process(threading.Thread):
    def __init__(self, common):
        threading.Thread.__init__(self)
        self.common = common
        self.result = None
        self.Popen = None

    def exe(self,outFlag=True):
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        self.Popen = Popen(self.common, stdout=PIPE,shell=True,env=env)
        temp = ''
        try:
            print('%s 执行命令%s' % (getTime(), self.common))
            print('当前进程id:',self.Popen.pid)
            while True:
                line = self.Popen.stdout.readline().decode('utf-8')
                if line:
                    try:
                        if (outFlag):
                            print(line,end='')
                        temp += line
                    except:
                        pass
                elif not line and self.Popen.poll() != None:
                    break
                else:
                    pass
                time.sleep(0.1)
        except Exception as e:
            print(e)
        print('%s 命令完成 %s' % (getTime(),self.common))
        self.Popen.kill()
        self.result = temp
        return self.result

    def run(self):
        self.result = self.exe(False)
