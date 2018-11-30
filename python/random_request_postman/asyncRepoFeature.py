#!/home/dell/anaconda3/bin/python
#!coding=utf-8
import json
from httpadapter import post_request
import requests
import string
import random
import re 
from repoRanker2 import Ranker2Repo
from featureCreate import featureCreate
from featureRanker2 import Ranker2Feature
from multiprocessing import Pool
from multiprocessing import Lock
from queue import Queue
import threading
import time
'''
# Get random string
def getRandomString(strLen=None, type_=0):

    
    type = 0, means number
    type = 1, means string
    

    retStr = ""

    if type_ == 0:
        str_ = string.digits    
    else:
        str_ = string.hexdigits

    for _index in range(int(strLen)):
        i = random.randint(0, 9)
        tmp = str_[i-1]
        retStr += tmp
    
    retStr = re.sub(r"\b0*([1-9][0-9]*|0)", r"\1", retStr)  

    return retStr

# Get choice num
def getChoiceNum(nList):

    return random.choice(nList)    
'''
# repo add operation
def repoAdd():
    url = "http://192.168.2.19:8010/rank/repo"
    for i in range(random.randint(5, 15)):
        #print '000 i:', i
        repo = Ranker2Repo("http://192.168.2.19:8010/rank/repo")
        repoid = "world%s"% i

    # Do the repo add operation
        #print '111 i:', i
        add_source = {"Context":{},"Repo":{"Operation":1,"RepoId":repoid,"Level":3,"FeatureLen":384,"FeatureDataType":3,"Capacity":1000,"Params":{"GPUThreads":"[0,0,1,0]"},"IndexType":"IDMap2,Flat","NeedAttribute":"true"}}
        #print '222 i',i
        #repo.addRepo(add_source)
#        f = open("./fse3.1.4_V100_response.info", "a+")
        resp_dict, _ret, jsource = post_request(url, add_source)
#        print >> f , "当前时间:{} , 当前操作:repoAdd, 返回值:{}, 状态码:{}\n, json_string:{}\n".format(time.asctime(), resp_dict, _ret, jsource)
        print "repoAdd_msg : %s\n" % resp_dict
		#print '333 i',i
        print "repoAdd do the %s times\n" % (i+1)
    
# repo delete operation
def repoDelete():
    url = "http://192.168.2.19:8010/rank/repo"
    for i in range(random.randint(5, 15)):
        #repo = Ranker2Repo("http://192.168.2.19:8010/rank/repo")
        repoid = "world%s"% i
        delete_source = {"Context":{},"Repo":{"Operation":2,"RepoId":repoid}}
        #repo.deleteRepo(delete_source)
        #print "$$$$$$$$$$$$$$$$$$$$$$$$$$"
#        f = open("./fse3.1.4_V100_response.info", "a+")
#        print "11111111111111111111111111"
        resp_dict, _ret, jsource = post_request(url, delete_source)
        #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@"
#        print >> f , "当前时间:{} , 当前操作:repoDelete, 返回值:{}, 状态码:{}\n, json_string:{}\n".format(time.asctime(), resp_dict, _ret, jsource)
        print "repoDelete_msg : %s\n" % resp_dict
        print "repoDelete do the %s times\n" % (i+1)

# repo update operation
def repoUpdate():
    # Assign ranker2 repo instance
    url = "http://192.168.2.19:8010/rank/repo"
    for i in range(random.randint(5, 15)):
        #print '000 i' ,i
        repo = Ranker2Repo("http://192.168.2.19:8010/rank/repo")
        repoid = "world%s"% i
        #print '111 i' ,i
        update_source = {"Context":{},"Repo":{"Operation":3,"RepoId":repoid,"Level":3,"FeatureLen":384,"FeatureDataType":3,"Capacity":1100,"Params":{ "GPUThreads":"[0,0,1,0]"},"IndexType": "IDMap2,Flat","NeedAttribute":"true"}}
        #print '222 i',i
        #repo.updateRepo(update_source)
#        f = open("./fse3.1.4_V100_response.info", "a+")
        resp_dict, _ret, jsource = post_request(url, update_source)
#        print >> f , "当前时间:{} , 当前操作:repoUpdate, 返回值:{}, 状态码:{}\n, json_string:{}\n".format(time.asctime(), resp_dict, _ret, jsource)
        #print '333 i',i
        print "repoUpdate_msg : %s\n" % resp_dict
        print "repoUpdate do the %s times\n" % (i+1)

# repo query operation
def repoQuery():
    url = "http://192.168.2.19:8010/rank/repo"
    for i in range(random.randint(5, 15)):
        repo = Ranker2Repo("http://192.168.2.19:8010/rank/repo")
#        repoid = "world%s"% i
        query_source = {"Context":{},"Repo":{"Operation":4}}
        #repo.queryRepo(query_source)
#        f = open("./fse3.1.4_V100_response.info", "a+")
        resp_dict, _ret, jsource = post_request(url, query_source)
#        print >> f , "当前时间:{} , 当前操作:repoQuery, 返回值:{}, 状态码:{}\n, json_string:{}\n".format(time.asctime(), resp_dict, _ret, jsource)
        print "repoQuery_msg : %s\n" % resp_dict
        print "repoQuery do %s times\n"% (i+1)

# feature add opeartion
def featureAdd():
    
    for i in range(random.randint(5, 15)):
        for j in range(50):    
            feature = featureCreate(384)
            url = "http://192.168.2.19:8010/rank/feature"
            fea = Ranker2Feature("http://192.168.2.19:8010/rank/feature")
            repoid = "world%s"% i
            add_source = {"Features":{"Operation":1,"RepoId":repoid,"ObjectFeatures":[{"Feature":feature,"Attribute":{"Id":"attr-%s"%i,"Attributes": {"sex": "male", "age": "27"}},"Time":86400000,"Id":"id-%s-%s"%(i,j),"Location":"l45"}]},"Context":{"SessionId":"ss_743"}}
            #print "#########################"
            #fea.addFeature(add_source)
#            f = open("./fse3.1.4_V100_response.info", "a+")
            resp_dict, _ret, jsource = post_request(url, add_source)
#            print >> f , "当前时间:{} , 当前操作:featureAdd, 返回值:{}, 状态码:{}\n, json_string:{}\n".format(time.asctime(), resp_dict, _ret, jsource)
            print "featureAdd_msg : %s\n" % resp_dict
        print "featureAdd do the %s times\n" % (i+1)

# feature delete operation
def featureDelete():
    url = "http://192.168.2.19:8010/rank/feature"
    for i in range(random.randint(5, 15)):
        fea = Ranker2Feature("http://192.168.2.19:8010/rank/feature")
        repoid = "world%s"% i
        for j in range(random.randint(0,20)):
            delete_source = {"Context":{},"Features": {"Operation":2,"RepoId": repoid,"ObjectFeatures":[{"Id":"id-%s-%s"%(i,j)}]}}
            #fea.deleteFeature(delete_source)
#            f = open("./fse3.1.4_V100_response.info", "a+")
            resp_dict, _ret, jsource = post_request(url, delete_source)
#            print >> f , "当前时间:{} , 当前操作:featureDelete, 返回值:{}, 状态码:{}\n, json_string:{}\n".format(time.asctime(), resp_dict, _ret, jsource)
        print "featureDelete_msg :%s\n" % resp_dict 
    print "featureDelete do the %s times\n" % (i+1)

#featureVN operation
def featureVN():
    for i in range(random.randint(5, 15)):
        #print '000 i',i
        feature = featureCreate(384)
        rank_url = "http://192.168.2.19:8010/rank"
        #repoid = "world%s"% i
        repoid = "cx"
        rank_source = {"Params":{"RepoId":repoid,"Normalization":"true","Locations":"l01","StartTime":"0","EndTime":"9999999999999"},"ObjectFeature":{"Feature":feature},"Context": {"SessionId": "test123"}}
        #print '111 i' ,i
#        f = open("./fse3.1.4_V100_response.info", "a+")
        resp_dict,ret,jsource = post_request(rank_url,rank_source)
#        print >> f , "当前时间:{} , 当前操作:featureVN, 返回值:{}, 状态码:{}\n, json_string:{}\n".format(time.asctime(), resp_dict, ret, jsource)
        print "featureVN_msg :%s\n" % resp_dict
        print "featureVN do the %s times\n" % (i+1)

def test(p):
    oMap = {"0":repoAdd,"1":repoDelete,"2":repoUpdate,"3":repoQuery, "4":featureAdd, "5":featureDelete, "6":featureVN}
    op = random.choice(["0", "1", "2", "3", "4", "5", "6"])
#    op = "4"
    print('op:%s , operation:%s' %(op,oMap[op]))
    oMap[op]()
    time.sleep(0.001)

if __name__ == "__main__":
    start = time.time()
    result = Queue(maxsize = 50000000)
    pool = Pool(24)
    lock = threading.Lock()
    #lock = Lock()
    exitFlag = 0

    def put_into_queue():
        #for i in range(500000000):
        i = 0
        while not exitFlag:
            lock.acquire()
            try: 
                result.put(pool.apply_async(test, args=(i, )))
                print "==================start==========================\n"
                print "total do %s times" % (i+1)
                print "===================end===========================\n"
                i += 1
                lock.release()
            except:
                print "Error,exit!"
                break
                #lock.release()

    def get_from_queue():
        while not result.empty():
            a = result.get()

    t1 = threading.Thread(target=put_into_queue)
    t2 = threading.Thread(target=get_from_queue)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    pool.close()
    pool.join()
    end = time.time()
    print("total cost %s s" % (end - start))
