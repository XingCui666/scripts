#!/usr/bin/env python
#!coding=utf-8


from httpadapter import post_request
import json 

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
        #print '::update repo result is as follow!'
        #print 'resp: ', json.dumps(resp_dict, indent=1)
