#! /bin/env python
# encoding=utf-8
# chenkan@baidu.com
# 
import sys
import os
import re
import jieba
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer


def dirTraverse(path):
    fl = os.listdir(path)
    filelist = []
    for file in fl:
        if file.startswith('http') and file.find('question') != -1:
            filelist.append(file)
    return filelist


def simplifyFile(filename, filepath):
    newfilename = filepath+filename
    f = open(filename,'r')
    nf = open(newfilename,'w+')
    content = f.read()
    newcontent = re.sub(r'<[^>]*>','',content)
    nf.write(newcontent)

    nf.close()
    f.close()

def cutfile(filename, filepath):
    newfilename = filepath+'seg'+filename
    nf = open(newfilename, 'w+')

    f = open(filepath+filename, 'r')

    seg_list = jieba.cut(f.read(), cut_all=False)
    seg_list = list(filter(lambda x:x != '', seg_list))
    seg_list = list(filter(lambda x:x != '\n', seg_list))
    seg_list = list(filter(lambda x:x!=' ', seg_list))
    seg_list_l = []
    
    sf = open(filepath+'stopwordscn.txt','r')
    stopwordscn = map(lambda x:x.strip(), list(sf.readlines()))
    sf.close()
    cf = open(filepath+'stopcharacters.txt','r')
    stopcharacters = map(lambda x:x.strip(), list(cf.readlines()))
    cf.close()
    
    for item in seg_list:
        item = item.encode('utf-8')
        if item not in stopwordscn and item not in stopcharacters:
            seg_list_l.append(item)
    
    content = ','.join(seg_list_l)
    nf.write(content)

    f.close()
    nf.close()

def calc_tfidf(filelist, filepath):
    corpus = []
    for filename in filelist:
        try:
            f = open(filepath+filename, 'r')
            corpus.append(f.read())
        except Exception,e:
            print filename+' open failed'
    print len(filelist)
    print 'calc tfidf'
    try:
        vectorizer = CountVectorizer()
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
        word = vectorizer.get_feature_names()
        weight = tfidf.toarray()
   
        for i in range(len(weight)):
            f = open(str(i)+'tfidf_result.txt','w+')
            for j in range(len(word)):
                f.write(str(word[j].encode('utf-8'))+':'+str(weight[i][j]))
    except Exception,e:
        print 'calc tfidf exception'

if __name__=='__main__':
    filelist = dirTraverse('.')
    '''
    for filename in filelist:
        print 'cut '+filename
        simplifyFile(filename, './files2/')
        cutfile(filename,'./files2/')
    
    print 'cut file finished'
    '''
    # tfidf
    newfilelist = []
    for filename in filelist:
        newfilelist.append('seg'+filename)
    calc_tfidf(newfilelist, './files2/')
    print 'tfidf caculation finished'

