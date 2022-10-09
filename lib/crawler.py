# coding=utf-8
# !/usr/bin/env python3

from lib.utils import getTime
from lib.sub import Process

import warnings,simplejson
import json,time,re
from fake_useragent import UserAgent

ua = UserAgent(path="fake_ua.json")

warnings.filterwarnings(action='ignore')

def get_random_headers():
    headers = {'User-Agent': ua.random,'Spider-Name': 'hacdoc'}

    return headers

def crawler(mysql,ports):
	while True:
		for port in ports: #因为xray慢，所以用不同的端口去跑
			#获取目标
			result = mysql.execute('select id,url from domains limit 0,1;')[0]

			#目标内容太少，跳过扫描
			if result['flag'] > 1 and result['flag'] < 9:
				mysql.execute('update domains set scantime="%s",flag=%d where id=%s;'% (getTime(), (result['flag']+1),result['id']))
				print('[-]%s跳过扫描'%result['url'])
				continue
			# 更新扫描时间
			mysql.execute('update domains set scantime="%s" where id=%s;'%(getTime(), result['id']))

			out = Process('tools/crawlergo -c /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome -t 5 -f smart --fuzz-path --custom-headers \'%s\' --push-to-proxy http://127.0.0.1:%s --push-pool-max 10 --output-mode json %s' %(json.dumps(get_random_headers()),port,result['url'])).exe(outFlag=False)

			res = simplejson.loads(out.split("--[Mission Complete]--")[1])

			if 'navigate timeout %s'% result['url'] in out:#无法连接
				mysql.execute('delete from domains where id=%s' % result['id'])
			elif len(res['req_list']) < 5:	#页面链接太少
				print('链接仅%d，加入跳过'%len(res['req_list']))
				mysql.execute('update domains set flag=2 where id=%s'%result['id'])#设置flag>1 and flag <10则属于跳过

			# 删除临时扫描
			if result['flag'] == 0:
				mysql.execute('update domains set flag=99 where id=%s;'%result['id'])

			if len(res['all_domain_list']) > 1:
				rows = []
				domains = mysql.execute('SELECT domain from target where company = "%s";'%result['company'])
				print('新发现域名如下：')
				for domain in res['all_domain_list']:
					if domain in domains:
						temp = mysql.execute('select id from domains where subdomain = %s;'%domain)
						if len(temp) > 0:
							pass
						else:
							rows.append(('http://%s'%domain,domain,result['flag'],result['parentId'],'crawler'))
							print(domain)
				if len(rows) > 0:
					mysql.execute('insert into domains(url,subdomain,flag,parentId,remark) value(%s,%s,%d,%d,%s);',rows)

			print("[crawl ok]")
			print("[sleeping]")
			time.sleep(300)
