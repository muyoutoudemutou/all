# coding=utf-8
# !/usr/bin/env python3
import sys

from lib.sub import Process
from lib.utils import getTime
import csv,time

def getChildDomain(mysql):
    try:
        while True:

            #获取目标
            result = mysql.execute('select id,domain from target limit 0,1;')[0]
            #更新扫描时间
            mysql.execute('delete from target where id=%s',(result['id']))

            #调用工具开始爆破子域名
            print('[+] 开始 %s 子域名扫描,命令如下:'%result['domain'])
            Process('python3 tools/OneForAll/oneforall.py --target %s --path domains.csv --alive true --fmt csv run'%result['domain']).exe(outFlag=False)

            print('[+] 根域 %s 扫描结束，发现子域名：' % result['domain'])
            rows = []
            with open('domains.csv','r') as domains:
                domain_csv = csv.DictReader(domains)
                for line in domain_csv:
                    print('[+] %s'%line['subdomain'])
                    rows.append((line['url'],line['subdomain'],line['status'],line['ip']))
            #区分临时扫描和长久扫描
            if len(rows) > 0:
                mysql.execute('replace into domains(url,subdomain,status,ip) value(%s,%s,%s,%s);',args=rows)
            Process('rm -rf tools/OneForAll/result/*').exe(outFlag=False)
    except KeyboardInterrupt:
        mysql.execute('insert into target(domain) value(%s);'% result['domain'])