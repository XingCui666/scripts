#!/usr/bin/env python
#!coding=utf-8 

'''
Created on 2017年12月18日

@author: Administrator
'''
'''
from repoRanker2 import Ranker2Repo

# Assign ranker2 repo instance
repo = Ranker2Repo("http://192.168.2.17:6501/rank/repo")
        
# Do the repo add operation
print '::Do the repo add'
repoid = 'world'
add_source = {"Context":{},"Repo":{"Operation":1,"RepoId":repoid,"Level":3,"FeatureLen":256,"Capacity":100,"Params":[{"key":"GPUThreads","value":"[0,0,0,1]"}]}}
repo.addRepo(add_source)

# Do the repo query operation
print '\r::Do the repo query'
query_source = {"Context":{},"Repo":{"Operation":4,"RepoId":repoid}}
repo.queryRepo(query_source)
'''
