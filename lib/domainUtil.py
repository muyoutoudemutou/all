# coding=utf-8
# !/usr/bin/env python3

from lib.sub import Process
from lib.utils import getTime
import csv,time

def getChildDomain(mysql):
    while True:
        #获取目标
        result = mysql.execute('select id,domain,flag,scantime from target where flag<>99 ORDER BY scantime asc limit 0,1;')
        #更新扫描时间
        mysql.execute('update target set scantime=%s where id=%s',(getTime(),result[0]['id']))

        #调用工具开始爆破子域名
        print('[+] 开始 %s 子域名扫描,命令如下:'%result[0]['domain'])
        Process('python3 tools/OneForAll/oneforall.py --target %s --path domains.csv --alive true --fmt csv run'%result[0]['domain']).exe(outFlag=False)

        print('[+] 根域 %s 扫描结束，发现子域名：' % result[0]['domain'])
        rows = []
        with open('domains.csv','r') as domains:
            domain_csv = csv.DictReader(domains)
            for line in domain_csv:
                temp = mysql.execute('select id from domains where subdomain = \'%s\';' % line['subdomain'])
                if len(temp) > 0:
                    continue
                print('[+] %s'%line['subdomain'])
                rows.append((line['url'],line['subdomain'],line['status'],line['title'],line['ip'],result[0]['id']))
        #区分临时扫描和长久扫描
        if len(rows) > 0:
            if result[0]['flag'] == '0':#临时扫描
                mysql.execute('replace into domains(url,subdomain,flag,status,title,ip,parentId) value(%s,%s,0,%s,%s,%s,%s);',
                              args=rows)
                mysql.execute('update target set flag=99 where id = %s;', (result[0]['id']))#非临时扫描
            else:
                mysql.execute('replace into domains(url,subdomain,flag,status,title,ip,parentId) value(%s,%s,1,%s,%s,%s,%s);',args=rows)
        Process('rm -rf tools/OneForAll/result/*').exe(outFlag=False)