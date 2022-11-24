# coding=utf-8
# !/usr/bin/env python3

import os,getopt,sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from lib.domainUtil import getChildDomain
from lib.mysqlConnect import MySQLconnect
from lib.scan import scan


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'm:', ['method='])
    with open('mysql.conf','r') as conf:
        user = conf.readline().strip()
        passwd = conf.readline().strip()
        db = conf.readline().strip()
        host = conf.readline().strip()
    mysql = MySQLconnect(user,passwd,db,host=host)

    if len(sys.argv) < 2:
        print('python3 all.py -m domain|s(scan)|a(add)|f')
    for opt,arg in opts:
        if opt in ('method','-m'):
            if arg == 'domain':
                getChildDomain(mysql)
            elif arg == 's':
                scan(mysql)#扫描类型
            elif arg == 'a':
                rows = []
                print('输入domain，输入quit退出，输入回车终止')
                while True:
                    temp = input('请输入domain:')
                    if temp == 'quit':
                        sys.exit(0)
                    elif len(temp) < 1:
                        break
                    else:
                        rows.append(temp)
                mysql.execute(
                        'insert into target(domain) value(%s);',
                        args=rows)
            elif arg == 'f':
                rows = []
                with open('domains.txt') as domainFile:
                    for line in domainFile.readlines():
                        rows.append(line.strip())
                mysql.execute(
                    'insert into domains(url,remark) value(%s,"scan");',
                    args=rows)
            else:
                print('python3 all.py -m domain|s(xray)|a(add)|f')

    mysql.close()