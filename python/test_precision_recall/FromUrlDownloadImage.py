#!/usr/bin/env python
#!coding=utf-8

import time
import re
import os
import string
import requests
import json
from urllib import urlretrieve
from multiprocessing import Pool


#import shenfenzheng filelist
imagelist = open("/data/dgtestdata/AlgorithmData/dgface/shenfenzheng/cards_lq_1500w")
allimagelist = imagelist.readlines()
imagelist.close()
#global lines

#from URL download image
def DownimagefromURL(i):
    path = "http://192.168.3.253/"

    print 'i:', i
    urlretrieve(path+str(allimagelist[i]).strip("\n"),"picture/%d.jpg" % (i))


if __name__ == "__main__":

    t1 = time.time()

    pool = Pool(processes=48)

    for i in range(len(allimagelist)):
        pool.apply_async(DownimagefromURL, args=(i, ))

    print("start")
    pool.close()
    pool.join()
    print("done")

    print time.time() - t1

