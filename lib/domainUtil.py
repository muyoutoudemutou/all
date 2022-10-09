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
            while True:
                count = mysql.execute('select count(id) as count from domains;')[0]['count']
                if count > 300:
                    print('目前目标数%s，暂停域名爆破'%count)
                    time.sleep(1800)
                else:
                    break
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
                    print('[+] %s'%line['url'])
                    rows.append((line['url']))
            #区分临时扫描和长久扫描
            if len(rows) > 0:
                mysql.execute('replace into domains(url) value(%s);',args=rows)
            Process('rm -rf tools/OneForAll/result/*').exe(outFlag=False)
    except KeyboardInterrupt:
        mysql.execute('insert into target(domain) value(%s);'% result['domain'])