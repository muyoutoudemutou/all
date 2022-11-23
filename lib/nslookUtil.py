#coding=utf-8
#!/usr/bin/env python3

import sys,os,threading,re,time
sys.path.append('..')#命令行需要导入环境变量，一般是系统环境加当前目录，其他目录例如上一层则需要手动添加了
from subprocess import Popen,PIPE,STDOUT
from lib.sub import Process,getTime

class dns_nslookup(threading.Thread):#如此便作了继承
    #初始化，类必须的self，dns
    def __init__(self,dns,domainFile,name=None,id=None):
        threading.Thread.__init__(self)
        self.dns = dns
        self.domainFile = domainFile
        self.name = name
        self.id = id
        self.result = None
        self.Popen = None

    def run(self):#线程执行，这里肯定就是命令执行了
        with open(self.domainFile,'r')as f:
            domainDic = {}
            for domain in f.readlines():
                domain = domain.replace('\n','')
                #命令，输入管道，输出接收的管道
                self.Popen = Popen(('nslookup '+domain.replace('://','').replace('https','').replace('http','')+' '+self.dns), stdin=PIPE, stdout=PIPE, stderr=STDOUT,shell=True)
                ipRe = re.compile(r'Address: ((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))')
                domainDic[domain] = ipRe.findall(self.Popen.stdout.read().decode('utf-8'))
                self.Popen.kill()
                time.sleep(0.25)
        self.result = domainDic

def testDns():
    print('[*] 开始测试dns是否可用\n')
    testThread = {}
    with open('dns.txt', 'r')as f:
        for dns in f.readlines():
            dns = dns.replace('\n','')
            testThread[dns] = Process(' '.join(('ping', dns, '-c 5')))
            testThread[dns].start()
    count = len(testThread.keys())
    dnss = []
    while count:
        for dns in list(testThread.keys()):
            if testThread[dns].result:
                if int(re.search(r'([\d]*)[\.]*[\d]*% packet loss', testThread[dns].result).group(1))==100:
                    print('[*]\t'+dns+'不可达！')
                else:
                    dnss.append(dns)
                testThread.pop(dns)
                count -= 1
        time.sleep(2)
    print('[*] dns测试结束\n')
    return dnss

def getIp(dnss,domainFile):
    #给每个dnss创建线程
    threads = {}
    for dns in dnss:
        threads[dns] = dns_nslookup(dns,domainFile,name=dns)
        threads[dns].start()
    print('[*] nslookup命令线程启动完毕\n')
    #每10秒查看是否运行结束
    if len(threads):
        flag = True
    else:
        flag = False
    while flag:
        for key in list(threads.keys()):
            if threads[key].is_alive():
                break
            flag = False
        time.sleep(10)
    #合并字典
    domainDict = {}
    for key in list(threads.keys()):
        if threads[key].result:
            for domain in list(threads[key].result.keys()):
                for ip in threads[key].result[domain]:
                    if domain in domainDict:#避免keyerror
                        domainDict[domain].append(ip)
                    else:
                        domainDict.setdefault(domain,[ip])
    #最后去重
    #print(domainDict)
    for key in list(domainDict.keys()):
        domainDict[key] = list(set(domainDict[key]))
    return domainDict



def nslookup():
    try:
        dnss = testDns()
        print('可用dns：'+'，'.join(dnss)+'\n')
        domainDict = getIp(dnss,'iptemp.txt')
        print('[*] 输出文件中...')
        filePath = 'nslookup/%s.txt'%getTime()
        with open(filePath,'w')as f:
            for key in list(domainDict.keys()):
                f.write(key+'\t\t\t\t'+','.join(domainDict[key])+'\n')
        print('[*] 完成，文件路径：'+filePath)
        return filePath
    except Exception as e:
        print(e)
        print(help)
