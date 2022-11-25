# coding=utf-8
# !/usr/bin/env python3
import sys

from lib.sub import Process
from lib.utils import getTime
from lib.nslookUtil import nslookup
import csv,time,re,json,requests

ipRe = re.compile(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')

def getChildDomain(mysql):
    try:
        while True:
            #获取目标
            try:
                result = mysql.execute('select id,domain from target limit 0,1;')[0]
                try:
                    getChildDomainForOne(result,mysql)
                except KeyboardInterrupt:
                    mysql.execute('insert into target(domain) value(%s);', (result['domain']))
            except IndexError:
                #result = mysql.execute('select id,url,remark from domains where remark = "bounty" limit 0,100;')
                result = None#赏金不做细致扫描，顶不住
                if result:
                    try:
                        getbountyDoamins(result, mysql)
                    except KeyboardInterrupt:
                        ids = []
                        for row in result:
                            ids.append(row['id'])
                        mysql.execute('update domains set remark = "bounty" where id = %s;', args=ids)
                else:
                    result = mysql.execute('select id,url,remark from domains where remark = "bountyscan" limit 0,1;')
                    if result:#还没扫描完
                        print('[-] 无域名需爆破，等待扫描结束。')
                        time.sleep(300)
                        continue
                    else:
                        print('[-] 无域名需爆破，重新下载赏金目标')
                        Process('rm -rf bountyFile/*').exe()#删除原本的所有文件
                        result = json.loads(requests.get('https://chaos-data.projectdiscovery.io/index.json',verify=False).text)
                        for target in result:
                            if target['bounty'] == True and (target['platform'] == 'hackerone' or target['platform'] == 'bugcrowd'):
                                with open('bountyFile/'+target['URL'][target['URL'].rindex('/')+1:],'wb') as targetZip:
                                    targetZip.write(requests.get(target['URL']).content)
                        Process('lib/unzip.sh').exe()#解压
                        rows = []
                        with open('bountyFile/alltargets.txt','r') as targeturl:
                            for line in targeturl.readlines():
                                if 'test' in line or len(line) > 32:
                                    continue
                                rows.append((line.strip(),'bountyscan'))
                        mysql.execute('insert into domains(url,remark) value(%s,%s);',args=rows)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(e)
        print('报错，重新执行')
        getChildDomain(mysql)

def getChildDomainForOne(result,mysql):
    mysql.execute('delete from target where id=%s;', (result['id']))

    # 调用工具开始爆破子域名
    print('[+] 开始 %s 子域名扫描,命令如下:' % result['domain'])
    Process('python3 tools/OneForAll/oneforall.py --target %s --path oneforallresult/%s_domains.csv --alive true --fmt csv run' % (result['domain'],result[
        'domain'])).exe(outFlag=True)

    rows = []
    urlrows = []
    with open('oneforallresult/%s_domains.csv'%result['domain'], 'r') as domains:
        domain_csv = csv.DictReader(domains)
        print('发现域名如下：')
        for line in domain_csv:
            for ip in line['ip'].split(','):
                rows.append(ip)
                print(line['url'])
                urlrows.append((line['url'],'scan'))



    rows = list(set(rows))  # 去重

    if len(urlrows) > 0:
        mysql.execute('insert into domains(url,remark) value(%s,%s);', args=urlrows)

    with open('iptemp.txt', 'w') as ipfile:
        for row in rows:
            ipfile.write(row + '\n')

    Process('./tools/fscan -hf iptemp.txt -o oneforallresult/%s_fscan.txt' %
    result['domain']).exe()

    print('开始端口扫描')
    Process(
        './tools/naabu -stats -l iptemp.txt -p 2053,2087,2096,8443,2083,2086,2095,2052,2082,3443,444,9443,2443,10000,10001,20000,8000-8999 -silent -o open-domain.txt').exe()
    print('开始http服务存活扫描')
    Process(
        './tools/httpx -silent -stats -l open-domain.txt -fl 0 -mc 200,302,403,404,204,303,400,401 -o newurls.txt').exe()

    rows.clear()
    print('发现http服务如下：')
    with open('newurls.txt', 'r') as newurlsfile:
        for line in newurlsfile.readlines():
            print(line)
            if len(line.strip()):
                rows.append((line.strip(),'scan'))
    print('\n\n\n')
    if len(rows) > 0:
        mysql.execute('insert into domains(url,remark) value(%s,%s);', args=rows)
    Process('rm -rf tools/OneForAll/result/*').exe(outFlag=False)


def getbountyDoamins(result,mysql):
    ids=[]
    with open('iptemp.txt', 'w') as ipfile:
        for row in result:
            ipfile.write(row['url']+'\n')
            ids.append(row['id'])
    mysql.execute('update domains set remark = "bountyscan" where id = %s;',args=ids)
    with open(nslookup(),'r') as f:
        ips = set()
        for line in f.readlines():
            j = ipRe.findall(line)
            for i in j:
                ips.add(i)
    with open('iptemp.txt', 'w', encoding='utf-8') as w:
        for i in ips:
            w.write(i+'\n')

    print('开始端口扫描')
    Process(
        './tools/naabu -stats -l iptemp.txt -p 2053,2087,2096,8443,2083,2086,2095,2052,2082,3443,444,9443,2443,10000,10001,20000,8000-8999 -silent -o open-domain.txt').exe()
    print('开始http服务存活扫描')
    Process(
        './tools/httpx -silent -stats -l open-domain.txt -fl 0 -mc 200,302,403,404,204,303,400,401 -o newurls.txt').exe()

    rows = []
    print('发现http服务如下：')
    with open('newurls.txt', 'r') as newurlsfile:
        for line in newurlsfile.readlines():
            print(line)
            if len(line.strip()):
                rows.append((line.strip(), 'bountyscan'))
    print('\n\n\n')
    if len(rows) > 0:
        mysql.execute('insert into domains(url,remark) value(%s,%s);', args=rows)

