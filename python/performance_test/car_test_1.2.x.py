#!/usr/bin/env python
# -*- coding: utf8 -*-

# author: mikahou
# date  : 27 Sept., 2016
# Load Test for Matrix


import base64
import datetime
import json
import logging
import logging.handlers
import operator
import os
import re
import requests
import signal
import sys
import threading
import time

reload(sys)
sys.setdefaultencoding("utf-8")

SESSION_ID = 0

## global configure infomation
conf = dict(
        ## server config
        mode = 1, # 0 means single, 1 means batch
        endpoints = dict(
            single = "http://192.168.2.234:6601/rec/image",
            batch = "http://192.168.2.234:6601/rec/image" + "/batch",
        ),
        batchNum = 8,
        functions = [100,101,102,103,104,105,106,107,108,109,110,300,301,400,401,402],
        svrType = 1, # 1:car 2:face 3:all 0:default(face)

        ## photo config
        uriType = 3, # 0 means local path, 1 means http path, 2 means encode to base64, 3 means image url file
        uriHeader = 'http://192.168.2.16:3002/',
        mountPath = '/',
        #mountPath = '/home/dell/matrix_server/test/photo/',
        photoPath = '/home/dell/python/sun/matrix/press_test/1.2.x/4K',
	#img_url_file = 'reconnect_https.txt',
        img_url_file = '02_new.txt',

        ## client config
        threadNum = 100,

        ## status info
        timeout = 100000,
        timeBound = (200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 5000,10000),
        carNumBound = (1, 2, 3, 5, 10, 20),
        pedestrianNumBound = (1, 2, 3, 5, 10, 20),
        NonMotorNumBound = (1, 2, 3, 5, 10, 20),
        logID = 0,
        interval = 5, # stat interval
        onePass = 0, # 1 means only run one time
        verbose = 1,# 0 means closed
        duration = 0, #how long to run, now default: never stop
)

## init log
logger = logging.getLogger("MyLogger")
os.system("mkdir -p ./log")
log_name = "./log/matrix.restful.log." + str(conf["logID"])
logging.basicConfig(level=logging.DEBUG,
           format='[%(asctime)s %(name)s %(levelname)s] %(message)s',
           #format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
           datefmt='%Y-%m-%d %H:%M:%S',
           filename=log_name,
           filemode='w')
handler = logging.handlers.RotatingFileHandler(log_name,
            maxBytes = 20971520, backupCount = 5)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.info(
        "[[time.time:%s]]" % str(int(time.time())))
logger.info(
        "[[loadtest start at %s]]" % str(datetime.datetime.now()))
logger.info("Timeout Threshold: %dms", conf["timeout"])
logger.info("threadNum: %d", conf["threadNum"])


## global stat
stat = dict(
    timeDist = [0] * (len(conf['timeBound']) + 1),
    timeDistAll = [0] * (len(conf['timeBound']) + 1),

    carNumDist = [0] * (len(conf['carNumBound']) + 1),
    carNumDistAll = [0] * (len(conf['carNumBound']) + 1),

    pedestrianNumDist = [0] * (len(conf['pedestrianNumBound']) + 1),
    pedestrianNumDistAll = [0] * (len(conf['pedestrianNumBound']) + 1),

    NonMotorNumDist = [0] * (len(conf['NonMotorNumBound']) + 1),
    NonMotorNumDistAll = [0] * (len(conf['NonMotorNumBound']) + 1),

    httpCodeDist = [0]*1000,
    httpCodeDistAll = [0]*1000,

    statusCodeDist = [0]*1000,  #analyze matrix return code
    statusCodeDistAll = [0]*1000,

    requestCount = 0,
    requestCountAll = 0,
    requestTime = 0.0,
    requestTimeAll = 0.0,

    httpErrorCount = 0,
    httpErrorCountAll = 0,
    httpErrorTime = 0.0,
    httpErrorTimeAll = 0.0,

    max_qps = 0.0,
    min_qps = 1000000.0,
    max_time = 0.0,
    min_time = 1000000.0,

    timeoutCount = 0,
    timeoutCountAll = 0,
    timeoutTime = 0.0,
    timeoutTimeAll = 0.0,

    errorCount = 0,
    errorCountAll = 0,
    errorTime = 0.0,
    errorTimeAll = 0.0,

    carCount = 0,
    carCountAll = 0,
    plateCount = 0,
    plateCountAll = 0,
    colorCount = 0,
    colorCountAll = 0,

    pedestrianCount = 0,
    pedestrianCountAll = 0,

    NonMotorCount = 0,
    NonMotorCountAll = 0

)


## query thread
class QueryThread(threading.Thread):
    def __init__(self, root_path):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.root_path = root_path
        self.header = {"Content-type": "application/json"}
        self.functions = conf['functions']
        self.svr_type = conf['svrType']

    def SingleReq(self, query):
        if len(query) == 0:
            return

        global SESSION_ID
        post_dict = {"Context": {"SessionId": 'singleReq_restful' + str(SESSION_ID), "Functions" : self.functions, "Type": self.svr_type}}
        SESSION_ID += 1

        logger.info("raw query:%s" %(query))
        query_dict = {}
        query = query[0]
        if conf['uriType'] == 0:
            query_dict = {'URI': 'file:' + query}
            print query
        elif conf['uriType'] == 1:
            query_dict =  {'URI': conf['uriHeader'] + '/' + query.split(conf['mountPath'])[1]}
        elif conf['uriType'] == 2:
             fd = open(query, "rb")
             file_encode = base64.b64encode(fd.read())
             fd.close()
             query_dict = {'BinData' : file_encode}
	elif conf['uriType'] == 3:
	    query_dict =  {'URI': query}
        post_dict['Image'] = {"Data": query_dict}
        return json.dumps(post_dict)

    def BatchReq(self, batchQuery):
        if len(batchQuery) == 0:
            return

        global SESSION_ID
        post_dict = {"Context": {"SessionId": 'batchReq_restful' + str(SESSION_ID), "Functions" : self.functions, "Type": self.svr_type}}
        SESSION_ID += 1
    
        batch_image = []
        for query in batchQuery:
            logger.info("raw query:%s" %(query))
            #print "raw query"
            #print query
            query_dict = {}
            if conf['uriType'] == 0:
                query_dict = {'URI': 'file:' + query}
            elif conf['uriType'] == 1:
                query_dict =  {'URI': conf['uriHeader'] + '/' + query.split(conf['mountPath'])[1]}
            elif conf['uriType'] == 2:
                fd = open(query, "rb")
                file_encode = base64.b64encode(fd.read())
                fd.close()
                query_dict = {'BinData' : file_encode}
	    elif conf['uriType'] == 3:
		query_dict = {'URI': query}
            batch_image.append({"Data": query_dict})
        post_dict['Images'] = batch_image
        
        return json.dumps(post_dict)

    ## request once
    def Search(self, query):
        post_data = ""
        m_url = ""

        ## single
        if conf['mode'] == 0:
            post_data = self.SingleReq(query)
            m_url = conf['endpoints']['single']
        ## batch
        elif conf['mode'] == 1:
            post_data = self.BatchReq(query)
            m_url = conf['endpoints']['batch']

        #print "===="* 50
        #print 'post_data'
        #print post_data
        #print "===="* 50
        begin = time.time()*1000
        #print "sun"
        #print post_data
        resp = requests.post(m_url, data=post_data)
        #resp = requests.post(m_url, data=post_data, headers=self.header)
        end = time.time()*1000

        #print "=="* 5 + resp.content
        #print "=="* 5 + str(len(str(resp.content)))
        #time.sleep(3)

        #request count
        stat["requestCount"] += 1
        #time cost
        elapse = end - begin
        #print elapse

        #sun 
        #elapse = resp.elapsed.microseconds*1.0/1000
        #print resp.elapsed.microseconds*1.0/1000

        stat["requestTime"] += elapse

        #http return code
        resultCode = resp.status_code
        #print "http return code:%s" %(resp.status_code)
        stat["httpCodeDist"][resultCode] += 1

        #http error request
        if int(resultCode) != 200:
            #http error
            stat["httpErrorCount"] += 1
            stat["httpErrorTime"] += elapse

        if elapse > conf["timeout"] :
            stat["timeoutCount"] += 1
            stat["timeoutTime"] += elapse

        for (i, bound) in enumerate(conf['timeBound']) :
            if elapse < bound :
                stat["timeDist"][i] += 1
                break
        if elapse > conf['timeBound'][-1]:
            stat["timeDist"][-1] += 1


        stat["max_time"] = max(elapse, stat["max_time"])
        stat["min_time"] = min(elapse, stat["min_time"])

        #matrix return context
        resp_dict = {}
        try:
            resp_dict =  json.loads(resp.content)
        except:
            logger.error('json.loads(resp.content) error')
            #logger.error('json.loads(resp.content) error, resp.content:', resp.content)
            return

        #print '#'*50
        #print int(resultCode)
        #print resp_dict
        #print '-'*40

	#matrix return code
        if not resp_dict.has_key('Context'):
            logger.error('resp_dict does not has key Context')
            return
        if not resp_dict['Context'].has_key('Status'):
            logger.error('resp_dict[\'Context\'] does not has key Status')
            return
        if resp_dict['Context']['Status'] == '': 
            logger.error('resp_dict[\'Context\'][\'Status\'] is empty')
            return
        returnCode = int(resp_dict['Context']['Status'])
        #print "deepv return code:%s" %(returnCode)
        stat["statusCodeDist"][returnCode] += 1
        if returnCode != 200:
        #if returnCode != 200 and resp_dict['Context'].has_key('Message'):
            #print "Debug###############"
            stat["errorCount"] += 1
            stat["errorTime"] += elapse
            #print post_data
            print resp.content
            #print resp_dict["Message"]
            logger.error('returnCode:%d' %(returnCode))
            logger.error(resp_dict)

        results = []
        if conf['mode'] == 0:
            result = resp_dict['Result']
            results.append(result)
        elif conf['mode'] == 1:
            results = resp_dict['Results']
        #print 'Results Size:%d' %(len(results))
        for result in results:
            if result.has_key("Vehicles"):
                car_num  = len(result['Vehicles'])
                stat['carCount'] += car_num

                for (i, bound) in enumerate(conf['carNumBound']) :
                    if car_num < bound :
                        stat["carNumDist"][i] += 1
                        break
                    if car_num > conf['carNumBound'][-1]:
                        stat["carNumDist"][-1] += 1

                for vehicle in result['Vehicles']:                                                                                             
                    if vehicle.has_key('Color') and vehicle['Color'].has_key('ColorId'):                                                       
                        if vehicle['Color']['ColorId'] != -1:                                                                                  
                            stat['colorCount'] += 1                                                                                            
                        else:                                                                                                                  
                            logger.error('Color Error, ColorId=-1') 
                            logger.error(str(vehicle)) 
                    else:
                        logger.error('Color Error')    
                        logger.error(str(vehicle))
                    if vehicle.has_key('Plates') and len(vehicle['Plates']) != 0:
                         stat['plateCount'] += 1
                    else:
                        logger.error('Plates Error')
                        logger.error(str(vehicle)) 

            #Pedestrian
            if result.has_key("Pedestrian"):
                pedestrian_num  = len(result['Pedestrian'])
                stat['pedestrianCount'] += pedestrian_num

                for (i, bound) in enumerate(conf['pedestrianNumBound']) :
                    if pedestrian_num < bound :
                        stat["pedestrianNumDist"][i] += 1
                        break
                    if pedestrian_num > conf['pedestrianNumBound'][-1]:
                        stat["pedestrianNumDist"][-1] += 1

            if result.has_key("NonMotorVehicles"):
                NonMotor_num = len(result["NonMotorVehicles"])
                stat["NonMotorCount"] += NonMotor_num

                for (i, bound) in enumerate(conf['NonMotorNumBound']):
                    if NonMotor_num < bound :
                        stat["NonMotorNumDist"][i] += 1
                        break 
                    if NonMotor_num > conf['NonMotorNumBound'][-1]:
                        stat["NonMotorNumDist"][-1] += 1

        #time.sleep(1)

    def batch_run(self, root_path, batch_num):
        batch_list = []
	if conf['uriType'] == 3:
	    fd = open(conf['img_url_file'],'r')
	    for line in fd.readlines():
		temp_path = line.strip()
		batch_list.append(temp_path)
		if len(batch_list) >= batch_num:
		    self.Search(batch_list)
		    batch_list = []
	    fd.close()
	else:
            for sub_dir_name in os.listdir(root_path):
                temp_path = "%s/%s" %(root_path, sub_dir_name)
                #print "temp_path:%s" %(temp_path)
                if re.search("^\.", sub_dir_name) != None:
                    #print "not deal it."
                    continue
                if os.path.isfile(temp_path):
                    if re.search("\.jpg", temp_path) == None:
                        continue
                    #print "-------------------"
                    #print temp_path
                    batch_list.append(temp_path)
                    if len(batch_list) >= batch_num:
                        self.Search(batch_list)
                        batch_list = []
                elif os.path.isdir(temp_path):
                    #print "in iter..."
                    #self.batch_run(temp_path)
                    self.batch_run(temp_path, batch_num)
            if len(batch_list) != 0:
                self.Search(batch_list)
                batch_list = []

    def run(self):
        while conf["onePass"] != 2:
            try:
                if conf['mode'] == 0:
                    self.batch_run(self.root_path, 1)
                    if conf["onePass"] == 1:
                        conf["onePass"] = 2
                elif conf['mode'] == 1:
                    self.batch_run(self.root_path, conf['batchNum'])
                    if conf["onePass"] == 1:
                        conf["onePass"] = 2
            except Exception as e:
		print e
            #    pass


class StatThread(threading.Thread) :
    def __init__(self) :
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.cycleCount = 0
        self.logger = logging.getLogger("StatLogger")
        #mika:make log name with logID
        log_name = "./log/stat.restful.log." + str(conf["logID"])
        print "log_name:%s" %(log_name)
        handler = logging.handlers.RotatingFileHandler(log_name,
                maxBytes = 20971520, backupCount = 5)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(
                "[[time.time:%s]]" % str(int(time.time())))
        self.logger.info(
                "[[loadtest start at %s]]" % str(datetime.datetime.now()))
        self.logger.info("Timeout Threshold: %dms", conf["timeout"])
        self.logger.info("threadNum: %d", conf["threadNum"])

	self.logger_1 = logging.getLogger("StatLoggerAll")
        log_name_1 = "./log/stat.restful_all.log." + str(conf["logID"])
        print "log_name_all:%s" %(log_name_1)
        handler_1 = logging.handlers.RotatingFileHandler(log_name_1,maxBytes = 20971520, backupCount = 5)
        self.logger_1.addHandler(handler_1)
        self.logger_1.setLevel(logging.DEBUG)
        self.logger_1.info("[[time.time:%s]]" % str(int(time.time())))
        self.logger_1.info("[[loadtest start at %s]]" % str(datetime.datetime.now()))
        self.logger_1.info("Timeout Threshold: %dms", conf["timeout"])
        self.logger_1.info("threadNum: %d", conf["threadNum"])
    
    def SnapShot(self) :
        # save stats
        self.timeDist = stat["timeDist"][:]
        self.carNumDist = stat["carNumDist"][:]
        self.pedestrianNumDist = stat["pedestrianNumDist"][:]
        self.NonMotorNumDist = stat["NonMotorNumDist"][:]
        self.requestCount = stat["requestCount"]
        self.timeoutCount = stat["timeoutCount"]
        self.requestTime = stat["requestTime"]
        self.timeoutTime = stat["timeoutTime"]
        self.httpCodeDist = stat["httpCodeDist"][:]
        self.statusCodeDist = stat["statusCodeDist"][:]
        self.httpErrorCount = stat["httpErrorCount"]
        self.httpErrorTime = stat["httpErrorTime"]
        self.errorCount = stat["errorCount"]
        self.errorTime = stat["errorTime"]
        self.carCount = stat["carCount"]
        self.pedestrianCount = stat["pedestrianCount"]
        self.NonMotorCount = stat["NonMotorCount"]
        self.plateCount = stat["plateCount"]
        self.colorCount = stat["colorCount"]

            
        if self.requestCount != 0:
            stat["max_qps"] = max(self.requestCount*1.0/conf["interval"], stat["max_qps"])
            stat["min_qps"] = min(self.requestCount*1.0/conf["interval"], stat["min_qps"])

        # reset stats
        stat["timeDist"] = [0] * (len(conf['timeBound']) + 1)
        stat["carNumDist"] = [0] * (len(conf['carNumBound']) + 1)
        stat["pedestrianNumDist"] = [0] * (len(conf['pedestrianNumBound']) + 1)
        stat["NonMotorNumDist"] = [0] * (len(conf['NonMotorNumBound']) + 1)
        stat["requestCount"] = 0
        stat["timeoutCount"] = 0
        stat["requestTime"] = 0.0
        stat["timeoutTime"] = 0.0
        stat["httpCodeDist"] = [0] * 1000
        stat["statusCodeDist"] = [0] * 1000
        stat["httpErrorCount"] = 0
        stat["HTTPErrorTime"] =0.0
        stat["errorCount"] = 0
        stat["errorTime"] = 0.0
        stat["carCount"] = 0
        stat["pedestrianCount"] = 0
        stat["NonMotorCount"] = 0
        stat["plateCount"] = 0
        stat["colorCount"] = 0


        # count all
        stat["timeDistAll"] = map(operator.add,
                stat["timeDistAll"], self.timeDist)
        stat["carNumDistAll"] = map(operator.add,
                stat["carNumDistAll"], self.carNumDist)
        stat["pedestrianNumDistAll"] = map(operator.add,                                                                                          
                stat["pedestrianNumDistAll"], self.pedestrianNumDist)
        stat["NonMotorNumDistAll"] = map(operator.add,
                stat["NonMotorNumDistAll"], self.NonMotorNumDist)
        stat["requestCountAll"] += self.requestCount
        stat["timeoutCountAll"] += self.timeoutCount
        stat["requestTimeAll"] += self.requestTime
        stat["timeoutTimeAll"] += self.timeoutTime
        stat["httpCodeDistAll"] = map(operator.add,
                stat["httpCodeDistAll"], self.httpCodeDist)
        stat["statusCodeDistAll"] = map(operator.add,
                stat["statusCodeDistAll"], self.statusCodeDist)
        stat["httpErrorCountAll"] += self.httpErrorCount
        stat["httpErrorTimeAll"] += self.httpErrorTime
        stat["errorCountAll"] += self.errorCount
        stat["errorTimeAll"] += self.errorTime
        stat["carCountAll"] += self.carCount
        stat["pedestrianCountAll"] += self.pedestrianCount
        stat["NonMotorCountAll"] += self.NonMotorCount
        stat["plateCountAll"] += self.plateCount
        stat["colorCountAll"] += self.colorCount


    def StatInfo(self, requestCount, timeoutCount, requestTime,
            timeoutTime, timeDist, elapse,
            httpCodeDist, errorCount, errorTime, httpErrorCount, HTTPErrorTime,
            statusCodeDist, carNumDist, pedestrianNumDist,NonMotorNumDist,carCount,pedestrianCount,NonMotorCount, plateCount, colorCount
            ) :
        elapse *= 1.0
        effectiveCount = requestCount  - errorCount - httpErrorCount;
        effectiveTime = requestTime -  errorTime - HTTPErrorTime;
        if elapse == 0:
            avgTimeoutCount = 0
            avgRequestCount = 0
            avgEffectiveCount = 0
            avgErrorCount = 0
            avgHttpErrorCount = 0
        else:
            avgTimeoutCount = timeoutCount / elapse
            avgRequestCount = requestCount / elapse
            avgEffectiveCount = effectiveCount / elapse
            avgErrorCount = errorCount / elapse
            avgHttpErrorCount = httpErrorCount / elapse

        if requestCount == 0:
            avgRequestTime = 0
        else:
            avgRequestTime = requestTime / requestCount

        if effectiveCount == 0:
            avgEffectiveTime = 0
        else:
            avgEffectiveTime = effectiveTime / effectiveCount

        #global BATCH_NUM
        #global conf['batchNum']
        throughput = 0
        time_1w = 0
        car_per_p = 0
        pedestrian_per_p = 0
        NonMotor_per_p = 0
        if conf['mode'] == 0:
            throughput = int(avgEffectiveCount * 86400)
            if avgEffectiveCount != 0:
                time_1w = 10000 / (avgEffectiveCount)
            if effectiveCount != 0:
                car_per_p = carCount*1.0/ effectiveCount
                pedestrian_per_p = pedestrianCount*1.0/ effectiveCount
                NonMotor_per_p = NonMotorCount*1.0/ effectiveCount
        elif conf['mode'] == 1:
            throughput = int(avgEffectiveCount * conf['batchNum'] * 86400)
            if avgEffectiveCount != 0:
                time_1w = 10000 / (avgEffectiveCount * conf['batchNum'])
            if effectiveCount != 0:
                car_per_p = carCount*1.0/(effectiveCount * conf['batchNum'])
                pedestrian_per_p = pedestrianCount*1.0/(effectiveCount * conf['batchNum'])
                NonMotor_per_p = NonMotorCount*1.0/(effectiveCount * conf['batchNum'])
        color_per_p = 0.0
        plate_per_p = 0.0
        if carCount != 0:
            color_per_p = colorCount*1.0/carCount
            plate_per_p = plateCount*1.0/carCount

        statInfo = "### Search time:%d, ErrorCount:%d, HttpErrorCount:%d,\n"\
                   "### timeoutCount:%d, avgTimeoutCount:%.2f/s,\n" \
                   "### avgQPS/avgEffectiveQPS:%.2f/%.2f/s,\n" \
                   "### avgRequestTime/avgEffectiveRequestTime:%.2fms/%.2fms,\n"\
                   "### maxQPS/minQPS:%.2f/%.2f,\n"\
                   "### maxReqestTime/minRequestTime:%.2fms/%.2fms,\n"\
                   "### Throughput per Day:%d,\n"\
                   "### Timecost per 1W::%.2fs,\n"\
                   "### colorCount:%d,%.4f plateCount:%d,%.4f carCount:%d  pedestrianCount:%d,\n"\
                   "### car per photo:%.2f pedestrian per photo:%.2f NonMotor per photo:%.2f,\n"\
                   "### elapse:%ds\n" % (
                        requestCount, errorCount, httpErrorCount, timeoutCount,
                        avgTimeoutCount, avgRequestCount, avgEffectiveCount,
                        avgRequestTime, avgEffectiveTime,
                        stat["max_qps"], stat["min_qps"],
                        stat["max_time"], stat["min_time"],
                        throughput,
                        time_1w,
                        colorCount, color_per_p, plateCount, plate_per_p, carCount, pedestrianCount,
                        car_per_p, pedestrian_per_p,NonMotor_per_p,
                        int(elapse))

        timeDistStr = [];
        timeDistStr.append("Time distro:")
        for i in range(len(timeDist)) :
            if i == 0 :
                timeDistStr.append("  0   - %-3d ms: %d" % (conf['timeBound'][i],
                    timeDist[i]))
            elif i == len(conf['timeBound']) :
                timeDistStr.append("  >  %-3d ms  : %d" % (conf['timeBound'][i - 1],
                    timeDist[i]))
            else :
                timeDistStr.append("  %-3d - %-3d ms: %d" % (conf['timeBound'][i - 1],
                    conf['timeBound'][i], timeDist[i]))


        carNumDistStr = [];
        carNumDistStr.append("Car Num distro:")
        for i in range(len(carNumDist)) :
            if i == 0 :
                carNumDistStr.append("  [ 0   - %-3d): %d" % (conf['carNumBound'][i],
                    carNumDist[i]))
            elif i == len(conf['carNumBound']) :
                carNumDistStr.append("  >  %-3d: %d" % (conf['carNumBound'][i - 1], 
                    carNumDist[i]))
            else :
                carNumDistStr.append("  [ %-3d - %-3d): %d" % (conf['carNumBound'][i - 1],
                    conf['carNumBound'][i], carNumDist[i]))

        pedestrianNumDistStr = [];
        pedestrianNumDistStr.append("Pedestrian Num distro:")
        for i in range(len(pedestrianNumDist)) :
            if i == 0 :
                pedestrianNumDistStr.append("  [ 0   - %-3d): %d" % (conf['pedestrianNumBound'][i],
                    pedestrianNumDist[i]))
            elif i == len(conf['pedestrianNumBound']) :
                pedestrianNumDistStr.append("  >  %-3d: %d" % (conf['pedestrianNumBound'][i - 1],                                                        
                    pedestrianNumDist[i]))                                                                                                        
            else :                                                                                                                         
                pedestrianNumDistStr.append("  [ %-3d - %-3d): %d" % (conf['pedestrianNumBound'][i - 1],                                                 
                    conf['pedestrianNumBound'][i], pedestrianNumDist[i]))

        NonMotorNumDistStr = [];
        NonMotorNumDistStr.append("NonMotor Num distro:")
        for i in range(len(NonMotorNumDist)) :
            if i == 0 :
                NonMotorNumDistStr.append("  [ 0   - %-3d): %d" % (conf['NonMotorNumBound'][i],
                    NonMotorNumDist[i])) 
            elif i == len(conf['NonMotorNumBound']) : 
                NonMotorNumDistStr.append("  >  %-3d: %d" % (conf['NonMotorNumBound'][i - 1],
                    NonMotorNumDist[i]))
            else : 
                NonMotorNumDistStr.append("  [ %-3d - %-3d): %d" % (conf['NonMotorNumBound'][i - 1],
                    conf['NonMotorNumBound'][i], NonMotorNumDist[i]))


        resultDistStr = [];

        httpCodeDistStr = [];
        httpCodeDistStr.append("Http Code distro:")
        for i in range(len(httpCodeDist)) :
            if httpCodeDist[i] == 0 :
                continue;
            httpCodeDistStr.append("  %s : %d" % (str(i), httpCodeDist[i]))


        statusCodeDistStr = [];
        statusCodeDistStr.append("DeepV Status Code distro:")
        for i in range(len(statusCodeDist)) :
            if statusCodeDist[i] == 0 :
                continue;
            statusCodeDistStr.append("  %s : %d" % (str(i), statusCodeDist[i]))

        for i in range(
                max(len(timeDistStr), len(resultDistStr), len(httpCodeDistStr), \
                    len(statusCodeDistStr), len(carNumDistStr), len(pedestrianNumDistStr), len(NonMotorNumDistStr))) :
            str1 = str2 = str3 = str4 = str5 = str6 = str7 = ""
            if i < len(timeDistStr) : str1 = timeDistStr[i]
            if i < len(resultDistStr) : str2 = resultDistStr[i]
            # added by mika
            if i < len(httpCodeDistStr) : str3 = httpCodeDistStr[i]
            if i < len(statusCodeDistStr) : str4 = statusCodeDistStr[i]
            if i < len(carNumDistStr) : str5 = carNumDistStr[i]
            if i < len(pedestrianNumDistStr) : str6 = pedestrianNumDistStr[i]
            if i < len(NonMotorNumDistStr) : str7 = NonMotorNumDistStr[i]
            statInfo += "%-22s %-22s %-25s %-10s %-10s %-25s %-25s\n" % (str1, str5, str6, str7, str2, str3, str4)
            #statInfo += "%-25s %-26s %-25s\n" % (str1, str2, str3)

        return statInfo


    def run(self) :
        while conf["onePass"] != 2 :
            time.sleep(conf["interval"])
            self.cycleCount += 1
            self.SnapShot()
            statInfo = "#" * 26 + str(datetime.datetime.now()) + "#" * 26 + "\n"
            if conf["verbose"] :
                statInfo += "verbose:\n"
                statInfo += self.StatInfo(self.requestCount, 
                        self.timeoutCount, self.requestTime, 
                        self.timeoutTime, self.timeDist,
                        conf["interval"], self.httpCodeDist,
                        self.errorCount, self.errorTime, self.httpErrorCount,
                        self.httpErrorTime, self.statusCodeDist, self.carNumDist,self.pedestrianNumDist,self.NonMotorNumDist, 
                        self.carCount, self.pedestrianCount, self.NonMotorCount, self.plateCount, self.colorCount)
                statInfo += "=-" * 38 + "\n"
	    self.logger.info(statInfo)


	    statInfo1 = "#" * 26 + str(datetime.datetime.now()) + "#" * 26 + "\n"
            statInfoAll = self.StatInfo(
                    stat["requestCountAll"], 
                    stat["timeoutCountAll"], stat["requestTimeAll"],
                    stat["timeoutTimeAll"],
                    stat["timeDistAll"],
                    conf["interval"] * self.cycleCount,stat["httpCodeDistAll"],
                    stat["errorCountAll"],stat["errorTimeAll"],
                    stat["httpErrorCountAll"],stat["httpErrorTimeAll"],
                    stat["statusCodeDistAll"], stat["carNumDistAll"],stat["pedestrianNumDistAll"],stat["NonMotorNumDistAll"],
                    stat["carCountAll"], stat["pedestrianCountAll"], stat["NonMotorCountAll"], stat["plateCountAll"], stat["colorCountAll"])
	    self.logger_1.info(statInfo1 + statInfoAll)

            print statInfo + statInfoAll
            #self.logger.info(statInfo)
        os.kill(os.getpid(), signal.SIGKILL)

def quitTest(signum, frame) :
    print "loadtest quit"
    sys.exit(0)

#do load test
def LoadTest() :
    testThreads = []
    for i in range(conf['threadNum']) :
        thrd = QueryThread(conf['mountPath'] + conf['photoPath']) 
        testThreads.append(thrd)
        thrd.start()

    try:
        statThread = StatThread()
        statThread.start()
    except:
        #mika:for debug
        #print  sys.exc_info()[0],sys.exc_info()[1]
        print 'load test error..............'
        sys.stdout = open('log/error.log.' + str(conf['logID']), 'a')
        print  sys.exc_info()[0],sys.exc_info()[1]
        sys.stdout = sys.__stdout__
        sys.exit(0)

    if conf['duration'] != 0 :
        signal.signal(signal.SIGALRM, quitTest)
        signal.alarm(conf['duration'] + 1)

    while True :
        time.sleep(36000)

    sys.exit(0)


if __name__ == '__main__':
    LoadTest()
