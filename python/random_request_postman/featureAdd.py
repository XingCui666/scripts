#!/usr/bin/env python
#!coding=utf-8 


from repoRanker2 import Ranker2Repo
from featureRanker2 import Ranker2Feature
from featureCreate import featureCreate

# Assign ranker2 repo and feature instance
repoid = 'world'
FeatureLen = 256 
featureid = '4rd5b46a-b227-11e7-a604-408d5c1565b5'
repo_url = "http://192.168.2.17:6501/rank/repo"
feature_url = "http://192.168.2.17:6501/rank/feature"

repo = Ranker2Repo(repo_url)
fea = Ranker2Feature(feature_url)
        
# Do the repo add operation
print '::Do the repo add'
add_source = {"Context":{},"Repo":{"Operation":1,"RepoId":repoid,"Level":3,"FeatureLen":FeatureLen,"Capacity":100,"Params":[{"key":"GPUThreads","value":"[0,0,0,1]"}]}}
repo.addRepo(add_source)

# Do the repo query operation
print '\r::Do the repo query'
query_source = {"Context":{},"Repo":{"Operation":4,"RepoId":repoid}}
repo.queryRepo(query_source)

# Do the feature add operation
print '::Do the feature add'
feature = featureCreate(FeatureLen)

add_source = {
         "Features": {
             "Operation": 1,
             "RepoId": repoid,
             "ObjectFeatures": [
             {   
               "Feature": feature,
               "Attributes": [ {"value": 43,"key": "k43"}],
                "Time": 1509480666000,
                "Id": featureid,
                "Location": "l44"
              }   
             ]   
         },  
        "Context": {"SessionId": "ss_743"}
        } 

print('add_source:', add_source)
fea.addFeature(add_source)

# Do the feature query operation
print '\r::Do the feature query'
query_source = {"Context":{},"Features": {"Operation":4,"ObjectFeatures":[{"Id":featureid}]}}
fea.queryFeature(query_source)
