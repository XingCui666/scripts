#!/usr/bin/env python
#!coding=utf-8 


from repoRanker2 import Ranker2Repo
from featureRanker2 import Ranker2Feature
from featureCreate import featureCreate
from httpadapter import post_request
import json 

# Assign ranker2 repo and feature instance
rank_url = "http://192.168.2.17:6501/rank"

source = {
          "Features": {
              "Operation": 1,
              "RepoId": "world",
              "ObjectFeatures": [
              {
                "Feature": "UfhGv2nOQD3pjw6+QjuaPh3iAL/4zdM+lxuHP2b/CL+kTN8+lygBv8I95r3+laC/N8v/Pmy/4b5um0y/cDRUv6CFa7y0pDA/oOZ0PxhvWb97cV0/3VDOvckMMr9H+2a/HDWWPvik975A7fo7hXfIvpK4Vj/QVQi+MMd0v1r13r2ohl4/KLskPx6SST9MOrS84oIvvxiKfz9tiha/sAZcvpxc3j4J+YY/T8jbPvaLej+ECYy/SNn1Ppxcmb5nVbm+lw7xvxWrBz8aWog+VuVLPo4AwL4fWqM+Yn+lPra07j4U04i/Btc6PgdpKD9n90M/jCHcPjLtXb8WZ9q97U9cP4nVHT+y3Fy/jrzNPu7WKj/cwfW+paKdP7eW6D5az/I/juBZvug7fz4cDwc/3aXdPjC20D1TBRU/0q7VPY8TRj8SFjI/NUCjPuWkVj5eO1e/ysGlPqLsqL4M4zk+JGniPorOeD7bm9K+d6KEPmyRPL9gtwG+oCnVPofhHb/tBx0/vwuOPzpyGD8hSCA/ebJ0P2RzHr4DjYE/D3AWP972hz9SCRi9SpOCPnEFSz+zVkA/wDTsPey21b5NYfU+imlVPgZXxD3siZG/dsaCPjTMgj+guGM/gArtPPouWb2ydIW+c8I6Po+BFr+YGh6/7sxqvzv2Pz/0PUQ9KhmFvvR8pDw=",
                "Attributes": [ {"value": 7843,"key": "k000043"}],
                 "Time": 1666666666666,
                 "Id": "4dd5b46a-b227-11e7-a604-h33333",
                 "Location": "444"
               }
              ]
          },
         "Context": {"SessionId": "ss_743"}
        }

resp_dict,ret = post_request(rank_url,source)
print json.dumps(resp_dict, indent=1)        
        

