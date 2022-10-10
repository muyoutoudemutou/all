# coding=utf-8
# !/usr/bin/env python3

from lib.utils import getTime
from lib.sub import Process
from subprocess import Popen, PIPE, STDOUT
import warnings,simplejson,os
import json,time,re,threading
from fake_useragent import UserAgent

ua = UserAgent(path="fake_ua.json")

warnings.filterwarnings(action='ignore')








def crawler(mysql,ports):
	try:
		while True:
			for port in ports: #循环遍历起线程
				try:
					#获取目标
					result = mysql.execute('select id,url from domains limit 0,1;')[0]
				except IndexError:
					time.sleep(3600)

				mysql.execute('delete from domains where id=%s',(result['id']))#删除


				print('扫描完毕')
				time.sleep(300)
	except KeyboardInterrupt:
		mysql.execute('insert into domains(url) value(%s);' % result['url'])
	except Exception:
		crawler(mysql,ports)