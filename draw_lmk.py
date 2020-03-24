#!/usr/bin/env python
#!coding=utf-8

'''
Author: xingcui
Function: draw landmark on images
'''

import cv2
import os
import sys


def draw_circle(img, point):
	point_size = 1
	point_color = (255, 255, 0)  # BGR
	thickness = 0  # 可以为 0 、4、8
	cv2.circle(img, point, point_size, point_color, thickness)
	cmd = os.path.dirname(os.path.abspath(__file__)) + '/'
	cv2.imwrite(cmd + save_name, img)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "case input_lmk_file"
		sys.exit(-1)
	input = sys.argv[1]
	with open(input) as f:
		lmk_lst = f.readlines()
	for lmk in lmk_lst:
		if lmk.split() == 1:
			print("{} lmk is empty,please check!".format(lmk.split()[0]))
			sys.exit(-1)
		else:
			img = lmk.split()[0]
			save_name = os.path.basename(img)
			img = cv2.imread(img)
			scale = img.shape
			h = scale[0]
			w = scale[1]
			#point_lst = lmk.strip('\n').split()[1:]
			point_lst = lmk.strip('\n').split()[6:]
			for i in range(0, len(point_lst), 2):
				point = tuple([int(eval(dot)) for dot in point_lst[i:i+2]])
				#x = float(eval(point_lst[i:i+2][0]))
				#y = float(eval(point_lst[i:i+2][1]))
				#x = int(x * w)
				#y = int(y * h)
				#point = (x, y)
				#print point
				#point = tuple([dot for dot in point_lst[i:i+2]])
				draw_circle(img, point)
