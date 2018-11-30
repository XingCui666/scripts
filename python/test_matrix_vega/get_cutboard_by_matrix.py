#!/usr/bin python
#!coding=utf-8
import sys
import os
import re
import shutil
import time
import multiprocessing as mp
from httpadapter import post_request
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def get_cutboard(i):
    url_path = "file://" + urllist[i].strip("\n")
    txt_name = re.search("(\d+).jpg", url_path).group(1)
    dir_name = "/data/cuixing/test_matrix_vega/result_txt/face_vega_matrix_face1/"
    #subdir_name = re.search("(\w+)_(\d+)", url_path).group(0)
    #save_name = dir_name + subdir_name + "/" + txt_name + ".txt"
    save_name = dir_name + txt_name + ".txt"
    resp_dict = matrix_request(url_path, Port)
    if resp_dict["Context"]["Status"] != "200":
        print "Error! Stop!"
        print "Error_image is: " ,url_path
    else:
        face_msg_list = resp_dict["Result"]["Faces"]
        for face in face_msg_list:
            x = face["Img"]["Cutboard"]["X"]
            y = face["Img"]["Cutboard"]["Y"]
            w = face["Img"]["Cutboard"]["Width"]
            h = face["Img"]["Cutboard"]["Height"]
            confidence = face["Confidence"]
            cutboard = [x, y, w, h, confidence]
            with open(save_name ,'a+') as f:
                save_str = str(cutboard).strip('[]').replace(",", "") + "\n"
                f.write(save_str)

def matrix_request(url_path, Port):
    url = "http://%s:%s/rec/image" % (IP, Port)
    source = {"Context": {"SessionId": SessionId, "Type": Type, "Functions": Functions},"Image": {"Data": {"URI":url_path}}}
    resp_dict, resp_code = post_request(url, source)
    return resp_dict


if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print "please start by [python] [file.list]"
        sys.exit(-1)
    url_list = sys.argv[1]
    with open(url_list) as f:
        urllist = f.readlines()
    IP = "192.168.2.17"
    Port = "7501" #matrix_1.4.6
    Type = 2
    Functions = [200,201,202,203,204,205]
    SessionId = "matrix_vega"
    pool = mp.Pool(24)
    length = len(urllist)
    start = time.time()
    for i in range(length):
        pool.apply_async(get_cutboard, args=(i, ))
        print "count: ", (i+1)
        i += 1
    pool.close()
    pool.join()
    end = time.time()
    print "cost_time_total: %s" % (end - start)
    print "cost_time_avg: %s" % ((end - start)/length)
