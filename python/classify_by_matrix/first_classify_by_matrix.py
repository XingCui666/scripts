#!/usr/bin python
#!coding=utf-8
import sys
import os
import shutil
import time
import multiprocessing as mp
from httpadapter import post_request
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

if(len(sys.argv) < 2):
    print "please start by [python] [file.list]"
    sys.exit(-1)
url_list = sys.argv[1]
with open(url_list) as f:
    urllist = f.readlines()


def tag_classify(i):
    url_path = urllist[i].strip("\n")
    save_path = url_path.replace("http://192.168.2.17", "/data")
    resp_dict = matrix_request(url_path, Port)
    if resp_dict["Context"]["Status"] != "200":
        tag = "invaild"
        shutil.copy(save_path, "picture_firstdetect_" + tag)
        print "invaild_image is: " ,url_path
    else:
        if resp_dict["Result"].has_key("Vehicles"):
            tag = "vehicle"
            shutil.copy(save_path, "picture_firstdetect_" + tag)
        elif resp_dict["Result"].has_key("Pedestrian"):
            tag = "pedestrian"
            shutil.copy(save_path, "picture_firstdetect_" + tag)
        elif resp_dict["Result"].has_key("NonMotorVehicles"):
            #resp_dict["Result"]["NonMotorVehicles"][0]["Passengers"][0]["Driver"] = "true"
            nonmotorattrs = resp_dict["Result"]["NonMotorVehicles"][0]["Passengers"][0]["Attributes"]
            for nonmotorattr in nonmotorattrs:
                if nonmotorattr["AttributeName"] == "车型":
                    tagId = nonmotorattr["ValueId"]
                    #print "tagId: ",tagId
                    if tagId in [1, 2, 5]:
                        tag = "tricycle"
                        shutil.copy(save_path, "picture_firstdetect_" + tag)
                    else:
                        tag = "bicycle"
                        shutil.copy(save_path, "picture_firstdetect_" + tag)
        else:
            if not resp_dict["Result"].has_key("Vehicles" and "Pedestrian" and "NonMotorVehicles"):
                tag = "background"
                shutil.copy(save_path, "picture_firstdetect_" + tag)


def matrix_request(url_path, Port):
    url = "http://%s:%s/rec/image" % (IP, Port)
    source = {"Context": {"SessionId": SessionId, "Type": Type, "Functions": Functions},"Image": {"Data": {"URI":url_path}}}
    resp_dict, resp_code = post_request(url, source)
    return resp_dict


if __name__ == "__main__":
    IP = "192.168.2.17"
    Port = "6501" #matrix_1.4.7
    Type = 1
    Functions = [100,400]
    SessionId = "tag_classify"
    pool = mp.Pool(24)
    length = len(urllist)
    start = time.time()
    for i in range(length):
        pool.apply_async(tag_classify, args=(i, ))
        print "count: ", (i+1)
        i += 1
    pool.close()
    pool.join()
    end = time.time()
    print "cost_time_total: %s" % (end - start)
    print "cost_time_avg: %s" % ((end - start)/length)
