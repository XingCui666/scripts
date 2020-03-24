#!/usr/bin/env python
#!coding=utf-8

'''
Author: xingcui
Function: get cos similarity with two feature
'''
import numpy as np
import sys
import numpy
from itertools import combinations
import matplotlib.pyplot as plt
import numpy as np

def draw(scores):

    counter = {}
    for item in scores:
        if item not in counter:
            counter[item] = 1
        else:
            counter[item] += 1
    # Counter data, counter is your counter object
    
    keys = counter.keys()
    y_pos = np.arange(len(keys))
    # get the counts for each key, assuming the values are numerical
    performance = [counter[k] for k in keys]
    # not sure if you want this :S
    error = np.random.rand(len(keys))
    plt.figure(figsize=(8, 7))
    print y_pos
    print keys
    plt.barh(y_pos, performance, height=0.1, xerr=error, align='center', alpha=1)
    plt.yticks(y_pos, keys)
    plt.xlabel('Counts')
    plt.title('2080Ti_bgr VS 2070_bgr')
    
    plt.savefig("2080Ti_bgr_VS_2070_bgr.png")
    plt.show()

def cos_distance(fe1, fe2):

	scores = []
	with open(fe1) as f1, open(fe2) as f2:

		for l1, l2 in zip(f1, f2):
			fea1 = l1.strip("\r\n ").split('.jpg')[-1]
			fea2 = l2.strip("\r\n ").split('.jpg')[-1]

			a = [float(i) for i in fea1.split()]
			b = [float(i) for i in fea2.split()]

			vec1 = np.array(a)
			vec2 = np.array(b)
			
			score = np.dot(vec1,vec2)/(np.linalg.norm(vec1)*(np.linalg.norm(vec2)))
			score = (score + 1) / 2.0
#print('cos_dictance:{}'.format(score))
			print score
			#raw_input()
			#print "cos_distance %s" % score
			#scores.append(round(score, 6))
			scores.append(score)
#    draw(scores)

if __name__ == "__main__":
    fe1 = sys.argv[1]
    fe2 = sys.argv[2]
    cos_distance(fe1, fe2)
