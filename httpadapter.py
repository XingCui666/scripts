# -*- coding: utf-8 -*-

import requests
import json


def post_request(url, source):
    # print(url, source)
    jsource = json.dumps(source)
    resp = requests.post(url, data=jsource)
#print('resp', resp)
    if resp.content == "":
        return None, resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict, resp.status_code


def get_request(url):
    resp = requests.get(url)
    if resp.content == "":
        return None, resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict, resp.status_code


def del_request(url):
    resp = requests.delete(url)
    if resp.content == "":
        return None, resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict, resp.status_code


def put_request(url, source):
    jsource = json.dumps(source)
    resp = requests.put(url, data=jsource)
    if resp.content == "":
        return None, resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict, resp.status_code
