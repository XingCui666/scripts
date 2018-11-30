#!/usr/bin/env python
#!coding=utf-8 


from repoRanker2 import Ranker2Repo

# Assign ranker2 repo instance
repo = Ranker2Repo("http://192.168.2.17:6501/rank/repo")
        
# Do the repo add operation
print '::Do the repo update'
update_source = {"Context":{},"Repo":{"Operation":3,"RepoId":"world","Level":3,"FeatureLen":256,"Capacity":100,"Params":[{"key":"GPUThreads","value":"[0,0,0,1]"}]}}
repo.updateRepo(update_source)

# Do the repo query operation
print '\r::Do the repo query'
query_source = {"Context":{},"Repo":{"Operation":4,"RepoId":"world"}}
repo.queryRepo(query_source)
