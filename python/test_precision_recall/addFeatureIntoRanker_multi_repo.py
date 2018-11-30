#!/usr/bin/env python
#!coding=utf-8

import re
import os
import string
import requests
import json
#import psycopg2

import numpy as np
import base64
from optparse import OptionParser
import math
#from helper import *
#from recognize_api import recognize_api
from ranker2 import *
from multiprocessing import Pool
import time
import helper
#fobj = open("/home/dell/data/cuixing/0/feature.list")
#allFeatures = fobj.readlines()[:100]
#fobj.close()

import time
from functools import wraps
 

def fn_timer(function):
  @wraps(function)
  def function_timer(*args, **kwargs):
    t0 = time.time()
    result = function(*args, **kwargs)
    t1 = time.time()
    print ("Total time running %s: %s seconds" %
        (function.func_name, str(t1-t0))
        )
    return result
  return function_timer

def addFeatreAsync(i):
    print 'i:', i
    line = allFeatures[i]
    feature_line = line.split(" ")
    feature_id = feature_line[0]
    feature_str = feature_line[1].strip("\n")

    print 'feature:[%s]' % feature_str
        
    featureSession = sessionFeature(rankerIp="192.168.2.17", rankerPort=6501)
    #repoId = "cx1"
    featureAdd(featureSession=featureSession, repoId=repoId, featureId=feature_id, featureStr=feature_str, time=0, location=0)

if __name__ == "__main__":
    t1 = time.time()
    for j in range(10):
        fobj = open("/home/dell/data/cuixing/0/feature.list")
        allFeatures = fobj.readlines()[1000*j:1000*j+1000]
        fobj.close()
        totalFeature = len(allFeatures)

        repoSession = sessionRepo(rankerIp="192.168.2.17", rankerPort=6501)
        repoId = "cx{}".format(j+1)
        print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
        addRepo(repoSession=repoSession, repoId=repoId, capacity=1000, level=3, featureLen=384, gPUThreads=[1,1,1,1])

        pool = Pool(processes=48)

        for i in range(totalFeature):
            pool.apply_async(addFeatreAsync, args=(i, ))        
            i += 1
        print("start")
        pool.close()
        pool.join()
        print("done")
        print 'total number = {}'.format(i)
    print time.time() - t1
