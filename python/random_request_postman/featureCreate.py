#!/usr/bin/env python
#!coding=utf-8

import numpy as np
import math
import base64
import random

# create feature based on length
def featureCreate(featureLen=None):

    # Check the feature lenght is valid or not
    if featureLen is None:
        print("Please input feature length, eg. 384")
        return
        
    # Create the the feature
    f_list = []
    ff_sum = 0.0
    for _ in range(featureLen):
        f = random.uniform(-1,1)
        ff = f*f
        f_list.append(f)
        ff_sum = ff_sum + ff
    t = math.sqrt(ff_sum)
    featureFloat = []
    for f in f_list:
        featureFloat.append(f/t)
    featureFloat = np.array(featureFloat,dtype=np.float32)
    featureString = base64.b64encode(featureFloat)
    print('featureString:', featureString)
    
    return featureString

if __name__ == "__main__":
    featureCreate(384)