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
                longtime = input('添加长期计划输入1，其他任意：')
                if longtime == '1':
                    longtime = 1
                else:
                    longtime = 0

                company = input('是否输入所属公司，输入则直接键入公司，否则输入会车跳过：')
                if len(company) < 1:
                    company = 'null'

                rows = []

                print('输入domain，输入quit退出，输入回车终止')
                while True:
                    temp = input('请输入domain:')
                    if temp == 'quit':
                        sys.exit(0)
                    elif len(temp) < 1:
                        break
                    else:
                        rows.append((temp,longtime,company))
                mysql.execute(
                        'replace into target(domain,flag,company) value(%s,%s,%s);',
                        args=rows)

    mysql.close()