#!/usr/bin/env python
#!coding=utf-8

from helper import post_request
import json
import numpy as np
import math
import base64
import random

# Repo class of Ranker2
class Ranker2Repo:
    def __init__(self, url):
        self.url = url

    def addRepo(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print '::Add repo result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)

    def queryRepo(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print '::Query repo result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)
        return resp_dict

    def deleteRepo(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print '::Delete repo result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)

    def updateRepo(self, source):
        resp_dict, _ret = post_request(self.url, source)
        return resp_dict
        #print '::update repo result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)

# Repo function
# Create repo session
def sessionRepo(rankerIp=None, rankerPort=None):

    # Assign the repo session
    repoSession = Ranker2Repo("http://%s:%s/rank/repo" % (rankerIp, rankerPort))

    return repoSession

# Add repo into ranker2
def addRepo(repoSession=None, repoId=None, capacity=None, level=3, featureLen=384, gPUThreads=[1,0,0,0]):

    # Assign ranker2 repo instance
    # repo = repoSession

    # Do the repo add operation
    print '::Do the repo add'
    add_source = {"Context":{},"Repo":{"Operation":1,"RepoId":repoId,"Level":3,"FeatureLen":int(featureLen),"FeatureDataType":3,"Capacity":int(capacity),"Params":{"GPUThreads":"%s" % gPUThreads}}}
    repoSession.addRepo(add_source)

# Feature class of Ranker2
class Ranker2Feature:
    def __init__(self, url):
        self.url = url

    def addFeature(self, source):
        resp_dict, _ret = post_request(self.url, source)
        print '::Add feature result is as follow!'
        print 'resp: ', json.dumps(resp_dict, indent=1)

    def queryFeature(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print '::Query feature result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)

    def deleteFeature(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print '::Delete feature result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)

    def updateFeature(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print '::update feature result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)

# Feature function
# create feature based on length
def featureCreate(featureLen=None):

    # Check the feature lenght is valid or not
    if featureLen is None:
        print("Please input feature length, eg. 384")
        return

    # Create the the feature
    f_list = []
    ff_sum = 0.0
    for _ in range(featureLen):
        f = random.uniform(-1,1)
        ff = f*f
        f_list.append(f)
        ff_sum = ff_sum + ff
    t = math.sqrt(ff_sum)
    featureFloat = []
    for f in f_list:
        featureFloat.append(f/t)
    featureFloat = np.array(featureFloat,dtype=np.float32)
    featureString = base64.b64encode(featureFloat)
    print('featureString:', featureString)

    return featureString

# Add feature into repo
def featureAddranker2(featureSession=None, repoId=None, featureId=None, featureStr=None, time=None, location=None):

    add_source={"Features":{"Operation":1,"RepoId":str(repoId),"ObjectFeatures":[{"Feature":featureStr,"Attributes":{"how_many":1000},"Time":int(time),"Id":str(featureId),"Location":str(location)}]},"Context":{"SessionId":"ss_743"}}
    featureSession.addFeature(add_source)

def featureAddfse(featureSession=None, repoId=None, featureId=None, featureStr=None, time=None, location=None,attributeId=None):

    add_source={"Features":{"Operation":1,"RepoId":str(repoId),"ObjectFeatures":[{"Feature":featureStr,"Attribute":{"Id":attributeId,"Attributes":{"sex":"male","age":"27"}},"Time":int(time),"Id":str(featureId),"Location":str(location)}]},"Context":{"SessionId":"ss_743"}}
    featureSession.addFeature(add_source)
'''
def featureAddfse():

#    feature = featureCreate(384)
#    fea = Ranker2Feature("http://39.104.109.10:9000/rank/feature")
    for i in range(random.randint(5, 15)):
#        print "total do cycle %s times" % s
        feature = featureCreate(384)
        fea = Ranker2Feature("http://39.104.109.10:9000/rank/feature")
        repoid = "world%s"% i
        add_source = {"Features":{"Operation":1,"RepoId":repoid,"ObjectFeatures":[{"Feature":feature,"Attribute":{"Id":"attr-%s"%i,"Attributes": {"sex": "male", "age": "27"}},"Time":86400000,"Id":"id-%s"%i,"Location":"l45"}]},"Context":{"SessionId":"ss_743"}}
        fea.addFeature(add_source)
        print "featureAdd do the %s times" % (i+1)
'''


# Create ranker session
def sessionFeature(rankerIp=None, rankerPort=None):

    # Assign the feature session
    featureSession = Ranker2Feature("http://%s:%s/rank/feature" % (rankerIp, rankerPort))

    return featureSession

# Do the 1vN ranker
def vN_by_ranker2(rankUrl="http://192.168.2.19:6501/rank", repoId=None, location=None, featureStr=None):

     source = {"Params":{"RepoId":repoId,"Normalization":"false","Locations":str(location),"StartTime":"0","EndTime":"9999999999999"},"ObjectFeature":{"Feature":featureStr},"Context":{"SessionId":"test123"}}

     resp_dict,ret = post_request(rankUrl,source)
     return json.dumps(resp_dict, indent=1)
     try:
         return resp_dict["Candidates"][0]["Score"],resp_dict["Candidates"][0]["Id"]
     except:
         return None
def vN_by_fse(rankUrl="http://192.168.2.19:6501/rank", repoId=None, location=None, featureStr=None):

     source = {"Params":{"RepoId":repoId,"Normalization":"false","Locations":str(location),"StartTime":"0","EndTime":"9999999999999","MaxCandidates":"10"},"ObjectFeature":{"Feature":featureStr},"Context":{"SessionId":"test123"}}

     resp_dict,ret = post_request(rankUrl,source)
     return json.dumps(resp_dict, indent=1)
     try:
         return resp_dict["Candidates"][0]["Score"],resp_dict["Candidates"][0]["Id"]
     except:
         return None
