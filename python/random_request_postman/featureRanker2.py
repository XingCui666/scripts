#!/usr/bin/env python
#!coding=utf-8


from httpadapter import post_request
import json 

class Ranker2Feature:
    def __init__(self, url):
        self.url = url
    
    def addFeature(self, source):
        resp_dict, _ret = post_request(self.url, source)    
        #print '::Add feature result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)
        
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
