#!/usr/bin/env python

import numpy as np
import os
import string
import math
import base64

# bin to feature
def bin2Feature(srcPath):

    fobj = open("feature.list", "w+")

    for root, dirs, files in os.walk(srcPath):
        for file in files:
            if string.lower(os.path.splitext(file)[1]) == '.bin':
                pc = np.fromfile(os.path.join(root, file), dtype=np.float32)
                featureFloat = np.array(pc,dtype=np.float32)
                array = np.array(featureFloat)
                array = array/math.sqrt(2)
                feature = base64.b64encode(array)
                print 'feature:', feature

                fobj.write("%s%s" % (feature, os.linesep))

    fobj.close()

if __name__ == "__main__":
    bin2Feature("/home/xingcui/")
