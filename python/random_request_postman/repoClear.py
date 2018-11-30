#!/usr/bin/env python
#!coding=utf-8 


from repoRanker2 import Ranker2Repo

# Assign ranker2 repo instance
repo = Ranker2Repo("http://192.168.2.17:6501/rank/repo")

# Do the repo query operation
print '::Do the repo query'
query_source = {"Context":{},"Repo":{"Operation":4,}}
resp_dict = repo.queryRepo(query_source)

# Do the repo delete operation (delete all repoes)
try:
    
    for repos in resp_dict['Repos']:
        delete_source = {"Context":{},"Repo":{"Operation":2,"RepoId":repos['RepoId']}}
        repo.deleteRepo(delete_source)
except:
    pass
    
