#! /bin/env python
# encoding=utf-8
# kanchen
# 
import os
import gzip
import re
import urllib
import hashlib
import datetime
import Queue

filepath = './files/'
        
def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

def getUrl(html):
    areg = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
    alist = re.findall(areg, html)
    return alist

def findValidUrl(hostname, urllist):
    invalidStr = ['javascript:', 'javascript:;', '/']
    invalidReg = r'#|mailto:|javascript|{{.*}}|google'
    validStr = []
    for (url,des) in urllist:
        if url not in invalidStr and re.search(invalidReg, url) is None:
            if url.startswith("http://") or url.startswith("https://"):
                item = (url, des)
                validStr.append(item)
            else:
                item = (hostname+url, des)
                validStr.append(item)
    return validStr

def getHost(url):
    topHostPostfix = (
                '.com','.la','.io','.co','.info','.net','.org','.me','.mobi',
                    '.us','.biz','.xxx','.ca','.co.jp','.com.cn','.net.cn',
                        '.org.cn','.mx','.tv','.ws','.ag','.com.ag','.net.ag',
                            '.org.ag','.am','.asia','.at','.be','.com.br','.net.br',
                                '.bz','.com.bz','.net.bz','.cc','.com.co','.net.co',
                                    '.nom.co','.de','.es','.com.es','.nom.es','.org.es',
                                        '.eu','.fm','.fr','.gs','.in','.co.in','.firm.in','.gen.in',
                                            '.ind.in','.net.in','.org.in','.it','.jobs','.jp','.ms',
                                                '.com.mx','.nl','.nu','.co.nz','.net.nz','.org.nz',
                                                    '.se','.tc','.tk','.tw','.com.tw','.idv.tw','.org.tw',
                                                        '.hk','.co.uk','.me.uk','.org.uk','.vg', ".com.hk")
    regx = r'(.*'+'|'.join(h.replace('.','\.') for h in topHostPostfix)+')'
    pattern = re.compile(regx, re.IGNORECASE)
    hostname = pattern.search(url)
    return hostname.group() if hostname else url

def checkVisited(url, urlProcessedSet):
    m = hashlib.md5()
    m.update(url)
    urlmd5 = m.hexdigest()
    if urlmd5 in urlProcessedSet:
        return True
    urlProcessedSet.add(urlmd5)
    return False

def writeFile(filename, filecontent, append):
    filename = filepath + filename
    if append == True:
        filehandler = open(filename, 'a')
    else: 
        filehandler = open(filename, 'w')
    
    filehandler.write(filecontent)
    filehandler.write("\r\n")
    filehandler.close()

def writeRelationFile(filename, url, urllist):
    filename = filepath + filename
    filehandler = open(filename, 'a')
    for (u, d) in urllist:
        content = url + '\t' + u + '\t' + d.strip() + '\r\n'
        filehandler.write(content)
    filehandler.close()

def saveFile(url, html, urllist):
    if html is None:
        writeFile('url.txt',url,True)
    else:
        ulist = re.findall(r'(\w*)', url)
        filename = ''.join(ulist)
        writeFile(filename+'.txt', html, False)

        writeFile('url_processed.txt',url,True)
        writeRelationFile('url_relation.txt', url, urllist)


def bfs(urlSet, urlProcessedSet):
    queue = Queue.Queue(maxsize = -1)

    for url in urlSet:
        queue.put(url)
    
    cnt = 0L
    while(not queue.empty()):
        cnt += 1
        if cnt % 5000 == 0:
            print 'collect the %Ld url info' % cnt
        url = queue.get()
        visited = checkVisited(url, urlProcessedSet)

        if visited==True:
            print "skip "+url
        else:
            print 'processing '+url
            try:
                html = getHtml(url)
                hostname = getHost(url)
                urllist = findValidUrl(hostname, getUrl(html))
                for (u,description) in urllist:
                    saveFile(u,None,None)
                    queue.put(u)
                saveFile(url, html, urllist)
            except Exception, e:
                print 'Exception happened in processing url:' + url

def initDict(upSet, urlFilename, urlProcessedFilename):
    urlSet = set()
    urlProcessedSet = set()
    filehandler1 = open(urlFilename, 'r')
    filehandler2 = open(urlProcessedFilename, 'r')
    for line in filehandler1.readlines():
        urlSet.add(line.strip())
    for line in filehandler2.readlines():
        m = hashlib.md5()
        m.update(line.strip())
        urlmd5 = m.hexdigest()
        upSet.add(urlmd5)
        urlProcessedSet.add(line.strip())
    
    filehandler1.close()
    filehandler2.close()
    return urlSet - urlProcessedSet
    

if __name__ == "__main__":
    try:
        now = datetime.datetime.now()
        print now.strftime('%Y-%m-%d %H:%M:%S')
        
        urlSet = set()
        urlProcessedSet = set()
        
        urlToProcessSet = initDict(urlProcessedSet, filepath+"url.txt", filepath+"url_processed.txt")
        #bfs("https://www.zhihu.com/topics");
        bfs(urlToProcessSet, urlProcessedSet);
        now = datetime.datetime.now()
        print now.strftime('%Y-%m-%d %H:%M:%S')
    except Exception,e:
        print "main process Exception"
