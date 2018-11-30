#!/usr/bin/env python
#!coding=utf-8

import re
import os
import string
import requests
import json
#import psycopg2
import sys
import numpy as np
import base64
from optparse import OptionParser
import math
#from helper import *
#from recognize_api import recognize_api
from ranker2 import *
from multiprocessing import Pool
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
#    attribute_id = "attr-%s"%i
    #print 'feature:[%s]' % feature_str

    featureSession = sessionFeature(rankerIp="192.168.2.17", rankerPort=8010)
    #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$44\n"
    repoId = "1000w_1822"
    attribute_id = "lic-%s" % i
    featureAddfse(featureSession=featureSession, repoId=repoId, featureId=feature_id, featureStr=feature_str, time=0, location=0,attributeId=attribute_id)
    #print "####################################################\n"
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Please start by: [python case] [feature.list]"
        sys.exit(1)
    file_path = sys.argv[1]
    fobj = open(file_path)
    allFeatures = fobj.readlines()
    fobj.close()

    t1 = time.time()

    totalFeature = len(allFeatures)

    pool = Pool(processes=24)
    for i in range(totalFeature):
        pool.apply_async(addFeatreAsync, args=(i, ))        
        i += 1
    print("start")
    pool.close()
    pool.join()
    print("done")
    print "total_addfeature: ",i
    print "total_addfeature_cost_time: ",time.time() - t1
