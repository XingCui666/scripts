#!/usr/bin/env python
#!coding=utf-8

import re
import os
import string
import requests
import json

import numpy as np
import base64
from optparse import OptionParser
import math

def array2feature(array):
    aList = [eval(i) for i in array.split()]
    featureFloat = np.array(aList,dtype=np.float32)
    array = np.array(featureFloat)
    array = array/math.sqrt(2)
    feature = base64.b64encode(array)
    #print 'feature:', feature

    return feature


# Get the string that we need
def getStringRe(pattern, subject):

    #result = re.findall(r"center_x:([0-9.]+) center_y:([0-9.]+) size_width:([0-9.]+) size_height:([0-9.]+) angle:(-?\d+)", subject)
    result = re.findall(pattern, subject)
    return result

# check input is image or image_directory
def fileDirectoryCheck(path):

    if os.path.isdir(path):
        return 0
    elif os.path.isfile(path):
        return 1

def post_request(url, source):
    jsource = json.dumps(source)
    resp = requests.post(url, data = jsource)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

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

# Get jpg file under specific directory
def getJpgFile(file_dir):
    L=[]
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if string.lower(os.path.splitext(file)[1]) == '.jpg':
                #L.append(os.path.join(root, file))  
                L.append(os.path.join("ftp://192.168.2.16/matrix_cases/nemon/nemo_debug", file))
    return L

# Get jpg file under specific directory
def getJpgName(file_dir):
    L=[]
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if string.lower(os.path.splitext(file)[1]) == '.jpg':
                #L.append(os.path.join(root, file))  
                L.append(os.path.join(root, file))
    return L

# Connect to postgresql
def connectSql(database="deepface_v5", user="postgres", password="123456", host="192.168.2.164", port="5432"):

    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    return conn

# Query for postgresql
def querySql(conn=None, query="select * from faces"):

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows
