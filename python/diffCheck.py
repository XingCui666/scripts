#!/usr/bin/env python
#!coding=utf-8

import os
from collections import defaultdict
import re

oldobj = open("shenfenzheng.big_new")
oldLines = oldobj.readlines()
oldobj.close()

oldjpg = [line.split(" ")[0].split("/")[-1].split(".")[0] for line in oldLines]

newobj = open("feature_1100card.list")
newLines = newobj.readlines()
newobj.close()

newDict = defaultdict(list)

fobj = open("list.diff", 'w')
for line in newLines:
    line = line.strip("\n")
    jpg, feature = line.split(" ")
    re_jpg  = re.sub(r".jpg.bin", r"", jpg)

    print 're_jpg:', re_jpg
    if re_jpg in oldjpg:
        pass
    else:
        fobj.write("%s%s" % (line, os.linesep))

fobj.close()
