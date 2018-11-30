#!/usr/bin/env python
#!coding=utf-8

'''
   usage:  adapter http get/post/dell/put request
   author: hongjiangli@deepglint.com
   date:   2016-08-03
'''
import requests
import json

def post_request(url, source):
    jsource = json.dumps(source)
#    resp = requests.post(url, data = jsource)
    resp = requests.post(url,jsource)
#    print '#############################\n'
    #print 'jsource:', jsource
#    print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n'
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code,jsource

def get_request(url):
    resp = requests.get(url)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

def del_request(url):
    resp = requests.delete(url)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

def put_request(url, source):
    jsource = json.dumps(source)
    resp = requests.put(url, data = jsource)
    if resp.content == "":
        return None,resp.status_code
    else:  
        rdict = json.loads(resp.content)
        return rdict,resp.status_code
