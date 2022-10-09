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
        self.Popen = Popen(self.common, stdin=PIPE, stdout=PIPE, stderr=STDOUT,shell=True,env=env)
        temp = ''
        try:
            print('%s 执行命令%s' % (getTime(), self.common))
            print('当前进程id:',self.Popen.pid)
            while True:
                line = self.Popen.stdout.readline()
                if line:
                    try:
                        if (outFlag):
                            print(line.decode('utf-8'),end='')
                        temp += line.decode('utf-8')
                    except:
                        pass
                elif not line and self.Popen.poll() != None:
                    break
                else:
                    pass
                time.sleep(0.5)
        except Exception as e:
            print(e)
        if outFlag:
            print('%s 命令完成' % getTime())
        self.Popen.kill()
        self.result = temp
        return self.result

    def run(self):
        self.result = self.exe(False)
