#!/usr/env python
#!coding=utf-8

import os
import sys
import numpy as np 
import cv2
import string
import matplotlib.pyplot as plt 

iou_thres = 0.5
scale_range = 1000


def get_pred1_pred2_list(pred1_dir, pred2_dir):
	pred1_list = os.listdir(pred1_dir)
	full_pred1_txt = []
	full_pred2_txt = []
	for pred1_txt in pred1_list:
		full_pred2_txt.append(os.path.join(pred2_dir, pred1_txt))
		if os.path.exists(full_pred2_txt[pred1_list.index(pred1_txt)]):
			full_pred1_txt.append(os.path.join(pred1_dir, pred1_txt))
	pred1_pred2_list = zip(full_pred1_txt, full_pred2_txt)

	return pred1_pred2_list     #for example:[(1.txt, 1.txt),(2.txt, 2.txt), ... (n.txt, n.txt)]


def get_pred_txt(pred_path):
	bbs = []
	if os.path.getsize(pred_path) == 0:
		return np.array(bbs)
	with open(pred_path, 'r') as f:
		try:
			while True:
				line = f.next().strip('\n')
				lst = line.split()    #lst_type is list!   
				pred = map(int, lst[:4])
				if pred[2] >= 0 and pred[2] < scale_range:
					bbs.append(pred)

		except StopIteration:
			pass

		return np.array(bbs)    #for example:[[1 2 3 4]
 							#			  [5 6 7 8]]



#check iou and get value
#the format b is: x, y, w, h
def get_iou_value(b1, b2):
	iou_val = 0.0
	x1 = np.max([b1[0], b2[0]])
	y1 = np.max([b1[1], b2[1]])
	x2 = np.min([b1[0] + b1[2], b2[0] + b2[2]])
	y2 = np.min([b1[1] + b1[3], b2[1] + b2[3]])
	w = np.max([0, x2 - x1])
	h = np.max([0, y2 - y1])
	if w != 0 and h != 0:
		iou_val = float(w * h) / (b1[2] * b1[3] + b2[2] * b2[3] - w * h)
	return iou_val


def cal_cutboard_and_save_img(img_dir, bbox1, bbox2):

	img = cv2.imread(img_dir)
	img_name = os.path.basename(img_dir)

	if len(bbox1) == 0 and len(bbox2) == 0:
		print "!!!!!!!!!!!!"
		return
	elif len(bbox1) != 0 and len(bbox2) == 0:
		for b1 in bbox1:
			cv2.rectangle(img, (b1[0], b1[1]), (b1[0] + b1[2], b1[1] + b1[3]), (255, 255, 0), 1)  #rfcn_bbox1 blue
		cv2.imwrite("../result_photo/" + str(img_obspath_file).strip('.list') + "/" + img_name,  img)
	elif len(bbox1) == 0 and len(bbox2) != 0:
		for b2 in  bbox2:
			cv2.rectangle(img, (b2[0], b2[1]), (b2[0] + b2[2], b2[1] + b2[3]), (0, 0, 255), 1)    #pengfei_bbox2  red
		cv2.imwrite("../result_photo/motor/"+ str(img_obspath_file).strip('.list') + "/" + img_name,  img)	
	else:
		if len(bbox1) != len(bbox2):
			for b1 in bbox1:
				for b2 in bbox2:
					cv2.rectangle(img, (b1[0], b1[1]), (b1[0] + b1[2], b1[1] + b1[3]), (255, 255, 0), 1)  #rfcn_bbox1    blue
					cv2.rectangle(img, (b2[0], b2[1]), (b2[0] + b2[2], b2[1] + b2[3]), (0, 0, 255), 1)    #pengfei_bbox2 red
			cv2.imwrite("../result_photo/"+ str(img_obspath_file).strip('.list') + "/" + img_name,  img)
		else:
			bbox_list = []
			bboxL = len(bbox1)
			for b1 in bbox1:
				for b2 in bbox2:
					bbox_list.append(get_iou_value(b1,b2))
			if bboxL == (len(bbox_list) - bbox_list.count(0)):
				pass
			else:
				for i in range(bboxL):
					cv2.rectangle(img, (bbox1[i][0], bbox1[i][1]), (bbox1[i][0] + bbox1[i][2], bbox1[i][1] + bbox1[i][3]), (255, 255, 0), 1)  #rfcn_bbox1    blue
					cv2.rectangle(img, (bbox2[i][0], bbox2[i][1]), (bbox2[i][0] + bbox2[i][2], bbox2[i][1] + bbox2[i][3]), (0, 0, 255), 1)    #pengfei_bbox2 red
				cv2.imwrite("../result_photo/"+ str(img_obspath_file).strip('.list') + "/" + img_name,  img)

if __name__ == "__main__":

	if (len(sys.argv) < 4):
		print "please start by: [python] [pred1_dir] [pred2_dir] [img_dir]"
		exit(-1)

	pred1_dir = sys.argv[1]   #/home/deepglint/Downloads/nonvehicle_face/result_txt/rfcn/motor/
	pred2_dir = sys.argv[2]   #/home/deepglint/Downloads/nonvehicle_face/result_txt/pengfei/motor/ 		    
	img_obspath_file = sys.argv[3]

	with open(img_obspath_file) as f:
		all_img_list = f.readlines()

	pred1_pred2_list = get_pred1_pred2_list(pred1_dir, pred2_dir)
	all_txt = len(pred1_pred2_list)
	print all_txt
	for i in range(all_txt):
		pred1_path, pred2_path = pred1_pred2_list[i]
		sub_name = os.path.basename(pred1_path).strip('.txt')
		for img_list in all_img_list:
			if sub_name in img_list:
				index = all_img_list.index(os.path.dirname(img_list) + "/" + sub_name + ".jpg\n")
		img_dir = all_img_list[index].strip('\n')
		print "img_dir: ", img_dir
		bbox1 = get_pred_txt(pred1_path)
		bbox2 = get_pred_txt(pred2_path)
		cal_cutboard_and_save_img(img_dir, bbox1, bbox2)
