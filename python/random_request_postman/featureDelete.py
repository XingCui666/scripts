#!/usr/bin/env python
#!coding=utf-8 


from featureRanker2 import Ranker2Feature

# Assign ranker2 repo and feature instance
repoid = 'world'
FeatureLen = 256
featureid = "4dd5b46a-b227-11e7-a604-408d5c1565b5"
feature_url = "http://192.168.2.17:6501/rank/feature"

fea = Ranker2Feature(feature_url)
        
# Do the feature delete operation
print '\r::Do the feature delete'
delete_source = {"Context":{},"Features": {"Operation":2,"ObjectFeatures":[{"Id":featureid}]}}
fea.deleteFeature(delete_source)

# Do the feature query operation
print '\r::Do the feature query'
query_source = {"Context":{},"Features": {"Operation":4,"ObjectFeatures":[{"Id":featureid}]}}
fea.queryFeature(query_source)
