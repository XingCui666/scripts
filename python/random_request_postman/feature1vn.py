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
    "Context": {
        "SessionId": "test123"
    },
    "ObjectFeature": {
        "Feature": ""
    },
    "Params": [
        {
            "key": "ScoreTransform",
            "value": "false"
        }
    ],
    "ObjectCandidates": [
        {
            "Id": "2",
            "Feature": ""
        },
        {
            "Id": "1",
            "Feature": ""
        }
    ]
}

source["ObjectFeature"]["Feature"]='UfhGv2nOQD3pjw6+QjuaPh3iAL/4zdM+lxuHP2b/CL+kTN8+lygBv8I95r3+laC/N8v/Pmy/4b5um0y/cDRUv6CFa7y0pDA/oOZ0PxhvWb97cV0/3VDOvckMMr9H+2a/HDWWPvik975A7fo7hXfIvpK4Vj/QVQi+MMd0v1r13r2ohl4/KLskPx6SST9MOrS84oIvvxiKfz9tiha/sAZcvpxc3j4J+YY/T8jbPvaLej+ECYy/SNn1Ppxcmb5nVbm+lw7xvxWrBz8aWog+VuVLPo4AwL4fWqM+Yn+lPra07j4U04i/Btc6PgdpKD9n90M/jCHcPjLtXb8WZ9q97U9cP4nVHT+y3Fy/jrzNPu7WKj/cwfW+paKdP7eW6D5az/I/juBZvug7fz4cDwc/3aXdPjC20D1TBRU/0q7VPY8TRj8SFjI/NUCjPuWkVj5eO1e/ysGlPqLsqL4M4zk+JGniPorOeD7bm9K+d6KEPmyRPL9gtwG+oCnVPofhHb/tBx0/vwuOPzpyGD8hSCA/ebJ0P2RzHr4DjYE/D3AWP972hz9SCRi9SpOCPnEFSz+zVkA/wDTsPey21b5NYfU+imlVPgZXxD3siZG/dsaCPjTMgj+guGM/gArtPPouWb2ydIW+c8I6Po+BFr+YGh6/7sxqvzv2Pz/0PUQ9KhmFvvR8pDw='
source["ObjectCandidates"][0]["Feature"]='C38MP6YWNz+zTho/d30LP0jp2D5RWSU/bgvgPjxLZD+asnY/clLEPn6uSj+oZQc/XmsRP+fzbD9ae5E92XCyPQ2hpTyTJlU/SDVHPx65Xj+7hno/qJVMPwZH7D7D0Ec/3TnyPd3RIz80yxI+0tVxP9qXBT+STtQ+1XOHPi40Rj+JjOk+44QRPxHtmTxcHR4/TrIcP2PvHT95mXE/xosuP2sRuD6nwt8+9ZcyP/yudj05sSo/7K4rP4duVz5BBQQ+03+hPkw4uj5q+BE/YZDgPhEGfT/f/NA9yuNVPlIuJT4bMic/cK+BPknA7j60Sno+7MgiPl0M4j03BSg/1X8NPuNMST6Mybw+nSxSPwndxj2Pg1Y/Ps/EPT/5eT8N8+8+BA16PyjXGj9hQD0/YYMgPRPMkD6dKfY9sJ+XPoUn8z2xzqI+RxrUPsNfgz3aRTE/ywwRPyLhhz6W8wU/4mPAPTtxEz9b5m0/eBujPmjbKj8F9gY+OGE3PwktlD6Eljs+tiUWP5W4pDxqNVQ/gtyZO2KFLT98Poo+rTU8P/1Rdj8luX4+DH8TPw+QFz8afxI/g29kPlzncz+e7eQ+Pa5YPxMRMz+oSZg+DlVQP80Cyz77j2E/Tc4UP2m5YT/ASTE/RKo5P8tWAD/mwXQ/i9wkP4cD2T6WPBs/DjudPARomj4='
source["ObjectCandidates"][1]["Feature"]='UfhGv2nOQD3pjw6+QjuaPh3iAL/4zdM+lxuHP2b/CL+kTN8+lygBv8I95r3+laC/N8v/Pmy/4b5um0y/cDRUv6CFa7y0pDA/oOZ0PxhvWb97cV0/3VDOvckMMr9H+2a/HDWWPvik975A7fo7hXfIvpK4Vj/QVQi+MMd0v1r13r2ohl4/KLskPx6SST9MOrS84oIvvxiKfz9tiha/sAZcvpxc3j4J+YY/T8jbPvaLej+ECYy/SNn1Ppxcmb5nVbm+lw7xvxWrBz8aWog+VuVLPo4AwL4fWqM+Yn+lPra07j4U04i/Btc6PgdpKD9n90M/jCHcPjLtXb8WZ9q97U9cP4nVHT+y3Fy/jrzNPu7WKj/cwfW+paKdP7eW6D5az/I/juBZvug7fz4cDwc/3aXdPjC20D1TBRU/0q7VPY8TRj8SFjI/NUCjPuWkVj5eO1e/ysGlPqLsqL4M4zk+JGniPorOeD7bm9K+d6KEPmyRPL9gtwG+oCnVPofhHb/tBx0/vwuOPzpyGD8hSCA/ebJ0P2RzHr4DjYE/D3AWP972hz9SCRi9SpOCPnEFSz+zVkA/wDTsPey21b5NYfU+imlVPgZXxD3siZG/dsaCPjTMgj+guGM/gArtPPouWb2ydIW+c8I6Po+BFr+YGh6/7sxqvzv2Pz/0PUQ9KhmFvvR8pDw='
resp_dict,ret = post_request(rank_url,source)
print json.dumps(resp_dict, indent=1)        
        

