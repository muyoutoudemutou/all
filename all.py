# coding=utf-8
# !/usr/bin/env python3

import os,getopt,sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from lib.domainUtil import getChildDomain
from lib.mysqlConnect import MySQLconnect
from lib.scan import scan
from lib.crawler import crawler


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'm:', ['method='])
    mysql = MySQLconnect('*','*','*',host='*')

    if len(sys.argv) < 2:
        print('python3 all.py -m domain|x(xray)|c(crawler)|a(add) port(xray port) port,port(crawler)')
    for opt,arg in opts:
        if opt in ('method','-m'):
            if arg == 'domain':
                getChildDomain(mysql)
            elif arg == 'x':
                mysql.close()
                if len(args) > 0:
                    scan(args[0])#输入监听的端口号
            elif arg == 'c':
                if len(args) > 0:
                    ports = args[0].split(',')
                    crawler(mysql,ports)
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
                        'replace into target(domain) value(%s);',
                        args=rows)

    mysql.close()