#!/usr/bin/env python
# -*- coding: utf8 -*-
import base64
import json
import numpy as np
import requests
import signal
import sys
import threading
import time
import random
import uuid
import math
from sklearn import preprocessing
from threading import Thread

# sys.path.append(os.getcwd()+'/proto/python')
#
# reload(sys)
# sys.setdefaultencoding("utf-8")

# Ranker service address
IP = "127.0.0.1"
RestfulPort = 6501

ServiceRestful = "http://" + IP + ":" + str(RestfulPort) + "/rank/feature"
#repoId = "capture-face-repo"
repoId = "1000w"
threadnum = 1
batchsize = 1
total = int(1000 * 10000 / 50)   # (800000 * 50 threads)
feature_len = 384
location_total = 10
attribute_total = 200
totalPerThread = total / threadnum

ss_mutex = threading.Lock()
send_count = 0
cur_added = 0
cur_added_faild = 0
req_failed = 0
req_time = 0
elapse = 0.0
status_interval = 2

featureFile = sys.argv[1]

fd = open(featureFile,'w')

def signal_handler(signum, aaa):
    sys.exit()


def start_restful(threadindex):
    global cur_added
    global cur_added_faild
    global req_failed
    global req_time
    global send_count
    global num

    for index in range(totalPerThread):
        source = {"Context": {"SessionId": "ss_%s" % index}, "Features": {}}
        features = {"RepoId": repoId, "Operation": 1, "ObjectFeatures": []}
        objectFeature = {"Id": "", "Location": "0", "Time": 0, "Feature": "", "Attributes": []}
        #attr = {"key": "", "value": ""}
        attr = {}

        #seed = int(time.time()) * index % 1023
        #np.random.seed(seed)
        #random.seed(seed)

        cur_ts = time.localtime()
        tsstr = "%d %d 17 %d:%d:%d" % (random.randint(1,30), 9, cur_ts.tm_sec, cur_ts.tm_min, cur_ts.tm_hour)
        timestamp = int(time.mktime(time.strptime(tsstr, "%d %m %y %S:%M:%H"))) * 1000

        objectFeature["Id"] = "%s" % str(uuid.uuid4())
        objectFeature["Location"] = str(index % location_total + 1)
        #objectFeature["Time"] = 0,#timestamp

        f_list = []
        ff_sum = 0.0
        for i in range(feature_len):
            f = random.uniform(-1,1)
            ff = f*f
            f_list.append(f)
            ff_sum = ff_sum + ff
        t = math.sqrt(ff_sum)
        featureFloat = []
        for f in f_list:
            featureFloat.append(f/t)
        #featureFloat = np.random.random_sample((feature_len,))
        #featureFloat = featureFloat.astype('float32')
        #featureFloat = preprocessing.normalize(featureFloat.reshape(1, feature_len), norm='l2')
        featureFloat = np.array(featureFloat,dtype=np.float32)
        featureString = base64.b64encode(featureFloat)
        objectFeature["Feature"] = featureString

        #attr["key"] = "k%s" % (index % attribute_total)
        #attr["value"] = index % attribute_total
        attr["k%s" % (index % attribute_total)] = index % attribute_total
        objectFeature["Attributes"] = attr
        features["ObjectFeatures"].append(objectFeature)
        source["Features"] = features

        # if index % batchsize == 0:
        post_data = json.dumps(source)
        # print post_data
        try:
            timestart = time.time()
            send_count += 1
            resp = requests.post(ServiceRestful, data=post_data)
            elapse = time.time() - timestart
        except requests.RequestException as e:
            resp.close()
            continue

        if resp.status_code != 200:
            ss_mutex.acquire()
            req_failed = req_failed + 1
            ss_mutex.release()
            resp.close()
            continue

        content = json.loads(resp.content)
        if content["Context"]["Status"] != "200":
            ss_mutex.acquire()
            cur_added_faild = cur_added_faild + 1
            ss_mutex.release()
            resp.close()
            continue

        ss_mutex.acquire()
        fd.write("%s   %s\n"%(objectFeature["Id"],objectFeature["Feature"]))
        req_time = req_time + elapse
        cur_added = cur_added + 1
        ss_mutex.release()
        resp.close()
    fd.close()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    threads = []
    start_time = time.time()
    t = Thread(target=start_restful, args=(1,))
    t.setDaemon(True)
    t.start()
    while True:
        print "Send Count: %d, Successful added: %d, add failed: %d, req failed: %d" % (send_count, cur_added, cur_added_faild, req_failed)
        print "Add Performance avg(count/s): %f" % (cur_added / (time.time() - start_time))
        if cur_added > 1:
            print "Request Latency: %f ms"%((req_time/cur_added)*1000)
        time.sleep(status_interval)
