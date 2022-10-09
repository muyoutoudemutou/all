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
	try:
		while True:
			for port in ports: #因为xray慢，所以用不同的端口去跑
				try:
					#获取目标
					result = mysql.execute('select id,url from domains limit 0,1;')[0]
				except IndexError:
					time.sleep(3600)

				mysql.execute('delete from domains where id=%s',(result['id']))#删除

				Process('tools/crawlergo -c /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome -t 5 -f smart --fuzz-path --custom-headers \'%s\' --push-to-proxy http://127.0.0.1:%s --push-pool-max 10 --output-mode json %s' %(json.dumps(get_random_headers()),port,result['url'])).exe(outFlag=False)
				print('扫描完毕')
				time.sleep(300)
	except KeyboardInterrupt:
		mysql.execute('insert into domains(url) value(%s);' % result['url'])