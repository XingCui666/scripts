#!/usr/bin/env python
#!coding=utf-8

import re
import os
import string
import requests
import json
import psycopg2

import numpy as np
import base64
from optparse import OptionParser
import math
from helper import *
#from recognize_api import recognize_api
from ranker2 import *

def _1v1RankerFromFile(repoId=None, featureFile=None):

    # Create a session
    featureSession = sessionFeature(rankerIp="192.168.2.17", rankerPort=8010)

    # Fetch all features
    fObj = open(featureFile)
    allFeatures = fObj.readlines()
    fObj.close()

    # Write error  into file
    tobj = open('toplist_1000w.file.1822', 'w')
    #robj = open('result_1300w.file', 'w')

    # Do through all features
    for line in allFeatures:
        feature_line = line.split(" ")
        feature_id = feature_line[0]
        feature_str = feature_line[1].strip("\n")
        print "[%s] [%s]" % (feature_id, feature_str)

        if feature_str == str(None):
            continue

        match = re.search(r"(\d+)_(\d+)", feature_id)
        head = match.group(1)
        print "head: ", head

        vnResult = vN_by_fse(rankUrl="http://192.168.2.17:8010/rank", repoId=repoId, location=0, featureStr=feature_str)

        print 'vnResult: ', vnResult
        print 'type: ', type(vnResult),type(eval(vnResult))
        print 'eval(vnResult): ', eval(vnResult)
        ev_vnResults = eval(vnResult)["Candidates"]
        flag = 1

        topLists_id = []
        topLists_score = []

        for ev_vnResult in ev_vnResults:
            topLists_id.append(ev_vnResult["Id"])
            topLists_score.append(ev_vnResult["Score"])

            try:
                begin = "/data/dgtestdata/AlgorithmData/dgface/bankVip/licenseCard100/"
                topIndex = topLists_id.index("%s%s%s" % (begin,head, "_0.jpg"))
                #print 'topIndex:', topIndex
            except:
                topIndex = -1

       	tobj.write("%s  %s   %s   %s%s" % (feature_id, feature_str, topIndex,topLists_score[topIndex],os.linesep))

            #for ev_vnResult in ev_vnResults:
            #    print "%s:%s:%s" % (feature_id, ev_vnResult["Id"], ev_vnResult["Score"]),
            #    robj.write("%s:%s:%s " % (feature_id, ev_vnResult["Id"], ev_vnResult["Score"]))
            #robj.write(os.linesep)

    tobj.close()

if __name__ == "__main__":
    repoId = "1000w_1822"
    featureFile = "/data/cuixing/dgface_rank_by_dif_version/0/feature_life100x10.list.1822"
    _1v1RankerFromFile(repoId, featureFile)
