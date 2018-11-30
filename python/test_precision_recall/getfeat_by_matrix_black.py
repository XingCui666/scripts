#!/usr/bin/env python
#!coding=utf-8

import requests
import json

from multiprocessing import Pool
import time
import os
import urllib
import sys

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

#print 'allPics:', len(allPics)

def post_request(url, source):
    jsource = json.dumps(source)
    resp = requests.post(url, data = jsource)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

def get_request(url):
    resp = requests.get(url)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

def del_request(url):
    resp = requests.delete(url)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

def put_request(url, source):
    jsource = json.dumps(source)
    resp = requests.put(url, data = jsource)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

class Matrix:
    def __init__(self, url):
        self.url = url

    def query(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print 'resp: ', json.dumps(resp_dict, indent=1)
        return resp_dict

# Matrix informaiton
matrix_url = "http://192.168.2.17:5503/rec/image"
matrixSession = Matrix(matrix_url)

def download(i, j):

    print 'i:', i
    if save_str == "black2w.list":
        featureStr = getFeatreFrommatrix(matrixSession, imageUrl="file://" + allPics[i].strip())
    else:
    #print 'imageUrl:', allPics[i].strip()
        featureStr = getFeatreFrommatrix(matrixSession, imageUrl=allPics[i].strip())
    #print 'featureStr:', featureStr

    if featureStr is None or len(featureStr) == 0:
        return
    fobj = open("%s/feature_" % j + save_str + ".1822" , "a+")
    fobj.write("%s %s%s" % (allPics[i].strip().encode("utf-8"),featureStr,os.linesep))
    fobj.close()

# Get featureStr from Matrix
def getFeatreFrommatrix(matrixSession=None, imageUrl="http://192.168.2.164:8501/api/file/6,06ba23581a"):

    post_source = {"Context":{"SessionId":"test face single","Type":2,"Functions":[200,201,202,203,204,205]},"Image":{"Data":{"URI": imageUrl}}}

    try:
        result = matrixSession.query(post_source)
        featureStr = result["Result"]["Faces"][0]["Features"]
        return featureStr
    except:
        return None

if __name__ == "__main__":
    if (sys.argv < 2):
        print "please start by: [python] [feature.list]"
        exit(-1)
    fea_list = sys.argv[1]
    fobj = open(fea_list)
    allPics = fobj.readlines()
    fobj.close()
    save_str = str(fea_list)

    t1 = time.time()

    totalLen = len(allPics)

    per_num = totalLen
    #per_num = 20000
    for i in range(totalLen/per_num):
        pool = Pool(processes=24)
        os.system("mkdir -p %s" % i)
        for j in range(per_num):
            pool.apply_async(download, args=(j+i*per_num, i))

        print("start")
        pool.close()
        pool.join()
        print("done")

    print time.time() - t1
