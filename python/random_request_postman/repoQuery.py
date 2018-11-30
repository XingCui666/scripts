#!/usr/bin/env python
#!coding=utf-8 


from repoRanker2 import Ranker2Repo

# Assign ranker2 repo instance
repo = Ranker2Repo("http://192.168.2.17:6501/rank/repo")

# Do the repo query operation
print '::Do the repo query'
query_source = {"Context":{},"Repo":{"Operation":4,}}
print('query_source:', type(query_source))

while True:
    resp_dict = repo.queryRepo(query_source)
    print 'resp_dict:', resp_dict
