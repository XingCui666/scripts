#!/usr/bin/env python
# -*- coding: utf8 -*-
#from __future__ import print_function
from gevent import monkey; monkey.patch_all()
from gevent import Greenlet
import base64
import json
import numpy as np
import requests
import signal
import sys, os, datetime
import threading
import logging
import logging.handlers
import time
import random
import uuid
from sklearn import preprocessing
from threading import Thread

# sys.path.append(os.getcwd()+'/proto/python')
#
# reload(sys)
# sys.setdefaultencoding("utf-8")

# Ranker service address
# IP = "192.168.2.130"
IP = "192.168.2.17"
RestfulPort = 6501

threadNum = 1

ServiceRestful = "http://" + IP + ":" + str(RestfulPort) + "/rank"
repoId = "2000w"
startdate = 1
enddate = 2
locationrange = 1
threadnum = 1
batchsize = 1
total = int(2000 * 10000 / 50)  # (5kw)
feature_len = 384
location_total = 100
totalPerThread = total / threadnum

ss_mutex = threading.Lock()
cur_rankered_count = 0
cur_rankered_succ = 0
cur_rankered_fail =0
cur_rankered_num = 0
req_failed = 0
req_time = 0.0
correct_count = 0
elapse = 0.0
status_interval = 2

featureDir = "feature" #sys.argv[1]


## init log
logger = logging.getLogger("MyLogger")
os.system("mkdir -p ./log")
log_name = "./log/ranker.log"
formatter = logging.Formatter(
    '%(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s: %(message)s')
handler = logging.handlers.RotatingFileHandler(log_name,
            maxBytes = 20971520, backupCount = 5)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.info("[[time.time:%s]]" % str(int(time.time())))
logger.info("[[loadtest start at %s]]" % str(datetime.datetime.now()))
#logger.info("Timeout Threshold: %dms", conf["timeout"])
logger.info("threadNum: %d", threadNum)


class Ranker(threading.Thread):
    def __init__(self,thread_num):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.thread_num = thread_num


    #def cycle_rank(self, threadindex):
    def run(self):
        print "111111111111"
        threadindex = self.thread_num
        while True:
            featureFile = "%s/feature_%d.txt"%(featureDir,self.thread_num)
            print 'featureFile:', featureFile
            fd = open(featureFile,'r')
            self.start_restful(threadindex,fd)
            fd.close()

    def start_restful(self,threadindex,fd):
        global cur_rankered_count
        global cur_rankered_succ
        global cur_rankered_num
        global cur_rankered_fail
        global req_failed
        global startdate
        global enddate
        global repoId
        global locationrange
        global req_time
        global correct_count

        #for index in range(totalPerThread):
        for (index,value) in enumerate(fd):
            feature_id = value.strip().split()[0]
            feature_string = value.strip().split()[1]
            seed = int(time.time()) * index % 1023
            np.random.seed(seed)
            random.seed(seed)
            cur_ts = time.localtime()
            #starttsstr = "%d %d 17 %d:%d:%d" % (random.randint(startdate,startdate), 12, cur_ts.tm_sec, cur_ts.tm_min, cur_ts.tm_hour)
            #starttimestamp = int(time.mktime(time.strptime(starttsstr, "%d %m %y %S:%M:%H"))) * 1000
            #endtsstr = "%d %d 17 %d:%d:%d" % (random.randint(enddate,enddate), 12, cur_ts.tm_sec, cur_ts.tm_min, cur_ts.tm_hour)
            #endtimestamp = int(time.mktime(time.strptime(endtsstr, "%d %m %y %S:%M:%H"))) * 1000
            #locations = ','.join(str(e) for e in random.sample(range(1,location_total+1),locationrange))

            source = {"Context": {"SessionId": "ss_%s" % index}, "ObjectFeature": {"Feature":""},"Params":[]}
            parameters_context= {
                'ConfidenceThreshold' : '0',
                'MaxCandidates' : '100',
                'PageSize' : '200',
                'PageIndex' : '0',
                'Locations': '0',
                'StartTime' : "0",#str(starttimestamp),
                'EndTime' : "9999999999999",#str(endtimestamp),
                'ScoreTransform':'true',
                'RepoId':repoId,
                'Normalization':'true',
            }
            #for key,value in parameters_context.items():
            #    param_iter = {"key":"","value":""}
            #    param_iter["key"] = key
            #    param_iter["value"] = value
            #    source["Params"].append(param_iter)
            source["Params"] = parameters_context

            #featureFloat = np.random.random_sample((feature_len,))
            #featureFloat = featureFloat.astype('float32')
            #featureFloat = preprocessing.normalize(featureFloat.reshape(1, feature_len), norm='l2')
            #featureString = base64.b64encode(featureFloat)
            source["ObjectFeature"]["Feature"] = feature_string #featureString

            #print source
            # if index % batchsize == 0:
            post_data = json.dumps(source)
            # print post_data
            try:
                timestart = time.time()
                resp = requests.post(ServiceRestful, data=post_data)
                elapse = time.time() - timestart
                #ss_mutex.acquire()
                cur_rankered_count = cur_rankered_count + 1
                #ss_mutex.release()
            except requests.RequestException as e:
                resp.close()
                continue

            if resp.status_code != 200:
                req_failed = req_failed + 1
                resp.close()
                continue

            content = json.loads(resp.content)
            if content["Context"]["Status"]=="200":
                cur_rankered_succ = cur_rankered_succ+ 1
                req_time = req_time + elapse
                if content.has_key('Candidates'):
                    cur_rankered_num = cur_rankered_num + len(content["Candidates"])
                    #for candidates in content["Candidates"]:
                    candidates = content["Candidates"][0]
                    topN_id = candidates["Id"]
                    topN_score = candidates["Score"]
                    if topN_id == feature_id and topN_score >= 0.9:
                        correct_count += 1
                    elif topN_score >= 0.9:
                        print topN_id,feature_id,topN_score
                resp.close()
                continue
            else:
                cur_rankered_fail = cur_rankered_fail+ 1
                resp.close()
                continue

def signal_handler(signum, aaa):
    sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    threads = []
    start_time = time.time()
    for i in range(threadNum):
        thrd = Ranker(i)
        threads.append(thrd)
        g = Greenlet.spawn(thrd.run)
        #g.start()
        #thrd.start()

    while True:
        time.sleep(status_interval)
        print "Rankered Count: %d" % cur_rankered_count
        print "Rankered succ: %d,  correct count: %d  rankered failed: %d,  req failed: %d" % (cur_rankered_succ,correct_count,cur_rankered_fail,req_failed)
        print "Rankered QPS: %f"%(cur_rankered_succ/(time.time() - start_time))
        if cur_rankered_succ == 0:
            latency = 0
            recall = 0
            accuracy = 0
        else:
            latency = req_time*1000/(cur_rankered_succ)
            recall = cur_rankered_num*1.0 / cur_rankered_succ
            accuracy = correct_count*1.0 / cur_rankered_succ
        print "Rankered Latency: %f ms" % latency
        print "Rankered Accuracy: %f" % accuracy
        print "Ranked Recall avg: %f" % recall
