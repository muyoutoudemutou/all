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

            mysql.execute('delete from target where id=%s;',(result['id']))

            #调用工具开始爆破子域名
            print('[+] 开始 %s 子域名扫描,命令如下:'%result['domain'])
            Process('python3 tools/OneForAll/oneforall.py --target %s --path domains.csv --alive true --fmt csv run'%result['domain']).exe(outFlag=True)

            rows = []
            urlrows = []
            with open('domains.csv','r') as domains:
                domain_csv = csv.DictReader(domains)
                print('发现域名如下：')
                for line in domain_csv:
                    for ip in line['ip'].split(','):
                        rows.append(ip)
                        print(line['url'])
                        urlrows.append(line['url'])

            rows = list(set(rows))#去重

            if len(urlrows) > 0:
                mysql.execute('insert into domains(url) value(%s);',args=urlrows)

            with open('iptemp.txt', 'w') as ipfile:
                for row in rows:
                    ipfile.write(row+'\n')

            print('开始端口扫描')
            Process('./tools/naabu -stats -l iptemp.txt -p 2053,2087,2096,8443,2083,2086,2095,2052,2082,3443,444,9443,2443,10000,10001,20000,8000-8999 -silent -o open-domain.txt').exe()
            print('开始http服务存活扫描')
            Process('./tools/httpx -silent -stats -l open-domain.txt -fl 0 -mc 200,302,403,404,204,303,400,401 -o newurls.txt').exe()

            rows.clear()
            print('发现http服务如下：')
            with open('newurls.txt', 'r') as newurlsfile:
                for line in newurlsfile.readlines():
                    print(line)
                    if len(line.strip()):
                        rows.append(line.strip())
            print('\n\n\n')
            if len(rows) > 0:
                mysql.execute('insert into domains(url) value(%s);',args=rows)
            Process('rm -rf tools/OneForAll/result/*').exe(outFlag=False)
    except KeyboardInterrupt:
        mysql.execute('insert into target(domain) value(%s);',(result['domain']))
    except Exception:
        print('报错，重新执行')
        getChildDomain(mysql)