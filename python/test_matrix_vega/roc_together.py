#!/usr/bin python
#!coding=utf-8

import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shutil
import sys
import argparse
import xlwt
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import cv2
import xlrd
from xlutils.copy import copy


prob_thres = [0.1, 0.15, 0.20, 0.25,0.3, 0.4, 0.5, 0.6, 0.7, 0.8,
			  0.9, 0.92, 0.94, 0.95, 0.96, 0.97,
			  0.971, 0.972, 0.973, 0.974, 0.975, 0.976, 0.977, 0.978, 0.979, 0.98,
			  0.981, 0.982, 0.983, 0.984, 0.985, 0.986, 0.987, 0.988, 0.989,
			  0.99, 0.991, 0.992, 0.993, 0.994, 0.995, 0.996, 0.997, 0.998, 0.999, 0.9999, 0.99999]


def iou(b1, b2):
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


def recall(pred, gt, thres):
	n = len(gt)
	if len(gt) == 0:
		reca = 1.0
		return reca
	if len(pred) == 0:
		reca = 0.0
		return reca

	m = 0
	for b1 in gt:
		for b2 in pred:
			if iou(b1, b2) > thres:
				m += 1
				break
	reca = float(m) / n
	return reca


def precision(pred, gt, thres):
	n = len(pred)
	if len(pred) == 0:
		prec = 1.0
		return prec
	if len(gt) == 0:
		prec = 1.0 / (len(pred) + 1)
		return prec
	m = 0
	for b1 in pred:
		for b2 in gt:
			if iou(b1, b2) > thres:
				m += 1
				break
	prec = float(m) / n
	return prec


def get_gt_txt(file_path, is_include_cls, scale_range):
	bbs = []
	with open(file_path, 'r') as f:
		try:
			while True:
				line = f.next().strip()
				lst = line.split()
				if is_include_cls:
					pred = map(int, lst[1:5])
				else:
					pred = map(int, lst[:4])
				if pred[2] >= scale_range[0] and pred[2] < scale_range[1]:
					bbs.append(pred)
		except StopIteration:
			pass

	return np.array(bbs)	#for example:[[1,2,3,4]
							#			  [5,6,7,8]]


def get_pred_txt(file_path, is_include_cls, scale_range):
	probs = []
	bbs = []
	with open(file_path, 'r') as f:
		try:
			while True:
				line = f.next().strip()
				lst = line.split()
				if is_include_cls:
					pred = map(int, lst[1:5])
					score = float(lst[5])
				else:
					pred = map(int, lst[:4])
					score = float(lst[4])
				if pred[2] >= scale_range[0] and pred[2] < scale_range[1]:
					bbs.append(pred)
					probs.append(score)
		except StopIteration:
			pass

	return np.array(bbs), np.array(probs)	#for example:[[1,2,3,4]
											#			  [5,6,7,8]]


def roc(gt_pred_list, save_dir, iou_thres, is_include_cls, resized_height, scale_range, rescale_thres=False):
	precisions = list()
	recalls = list()
	cnt = 0
	max_prob = 1
	if rescale_thres is True:
		prob_list = list()
		for line in gt_pred_list:
			dump, pred_file = line
			dump, probs = get_pred_txt(pred_file, is_include_cls, scale_range)
			prob_list.extend(probs)
		max_prob = max(prob_list)
	new_prob_thres = [one_prob_thres * max_prob for one_prob_thres in prob_thres]
	
	print "=========start transform========="
	for line in gt_pred_list:
		gt_file, pred_file = line
		gt = get_gt_txt(gt_file, is_include_cls, scale_range)
		pred, probs = get_pred_txt(pred_file, is_include_cls, scale_range)

		precisions.append(list())
		recalls.append(list())
		for k in range(len(new_prob_thres)):
			if len(pred) > 0:
				I = probs > new_prob_thres[k]
				prob_k = probs[I]
				pred_k = pred[I, :]
			else:
				pred_k = []
			c = precision(pred_k, gt, iou_thres)
			precisions[-1].append(c)
			r = recall(pred_k, gt, iou_thres)
			recalls[-1].append(r)

		cnt += 1
		if cnt % 100 == 0:
			print "precessed {}".format(cnt)
	print "=========end transform==========="
	precisions = np.array(precisions)
	recalls = np.array(recalls)

	roc_save_dir = "{}".format(save_dir)

	#np.save("%s/precision_iou%.3f.npy" % (roc_save_dir, iou_thres), precisions)
	#np.save("%s/recall_iou%.3f.npy" % (roc_save_dir, iou_thres), recalls)

	mean_p = np.mean(precisions, axis=0)
	mean_r = np.mean(recalls, axis=0)
	return (mean_p, mean_r)		#([p[0] p[1] ... [pn]],[r[0] r[1] ... r[n]])


def get_gt_pred_list(gt_dir, pred_dir):
	gt_list = os.listdir(gt_dir)
	gt_pred_list = []
	for gt_txt in gt_list:
		full_pred_txt = os.path.join(pred_dir, gt_txt)
		if os.path.exists(full_pred_txt):
			full_gt_txt = os.path.join(gt_dir, gt_txt)
			gt_pred_list.append((full_gt_txt, full_pred_txt))

	return gt_pred_list	#for example:[(anno.txt1,pred.txt1),(anno.txt2,pred.txt2),...,(anno.txtn,pred.txtn)]

def parse_args():
	parser = argparse.ArgumentParser(description='roc')
	parser.add_argument('--anno_dir', dest='anno_dir', help='gt dir', type=str)
	parser.add_argument('--pred1_dir', dest='pred1_dir', help='pred_vega_docker dir', type=str)
	parser.add_argument('--pred2_dir', dest='pred2_dir', help='pred_vega_V2 dir', type=str)
	parser.add_argument('--pred3_dir', dest='pred3_dir', help='pred_vega_matrix dir', type=str)
	parser.add_argument('--save_dir', dest='save_dir', help='save dir', type=str)
	parser.add_argument('--resized_height', dest='resized_height', default=None, help='img height when test',
						type=float)
	parser.add_argument('--ious', dest='ious', default="(0.5,)", help='ious to compute roc, should be tuple or list',
						type=str)
	parser.add_argument('--scale_ranges', dest='scale_ranges', default="(0,1000)",
						help='split range scales to compute roc, "(s1,s2),(s3,s4),..."',
						type=str)
	parser.add_argument('--include_cls', dest='include_cls', help='flag to note whether include cls in pred_file',
						action='store_true')
	parser.add_argument('--rescale_thres', dest='rescale_thres', help='flag to note whether rescale the score thresholds',
						action='store_true')
	parser.add_argument('--show', dest='show', help='whether to show plot figure',
						action='store_true')

	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()
	return args



def save_xlsx():
	table = {"face_1":0 ,"face_3":1, "face_5":2, "face_6":3, "face_7":4}	#save face_1 first!
	if not os.path.exists("{}/face_detect.xlsx".format(args.save_dir)):
		file = xlwt.Workbook(encoding = 'utf-8')
		sheet_0 = file.add_sheet(sorted(table.keys())[0]) 
		sheet_1 = file.add_sheet(sorted(table.keys())[1])
		sheet_2 = file.add_sheet(sorted(table.keys())[2])
		sheet_3 = file.add_sheet(sorted(table.keys())[3])
		sheet_4 = file.add_sheet(sorted(table.keys())[4])
	else:
		file = xlrd.open_workbook("{}/face_detect.xlsx".format(args.save_dir), formatting_info = True)
		file = copy(file)
		sheet_0 = file.get_sheet(table[save_name])
	sheet_0.write_merge(0,0,0,4,'Vega_docker')
	sheet_0.write(1, 0, u'阈值')
	sheet_0.write(1, 1, u'准确率')
	sheet_0.write(1, 2, u'召回率')
	sheet_0.write(1, 3, u'误检率')
	sheet_0.write(1, 4, u'漏检率')
	sheet_0.write_merge(0,0,5,9,'Vega_V2')
	sheet_0.write(1, 5, u'阈值')
	sheet_0.write(1, 6, u'准确率')
	sheet_0.write(1, 7, u'召回率')
	sheet_0.write(1, 8, u'误检率')
	sheet_0.write(1, 9, u'漏检率')
	sheet_0.write_merge(0,0,10,14,'Vega_Matrix')
	sheet_0.write(1, 10, u'阈值')
	sheet_0.write(1, 11, u'准确率')
	sheet_0.write(1, 12, u'召回率')
	sheet_0.write(1, 13, u'误检率')
	sheet_0.write(1, 14, u'漏检率')
																		
	for i in range(len(prob_thres)):
		sheet_0.write(i+2, 0, prob_thres[i])
		sheet_0.write(i+2, 1, mean_p1[i])
		sheet_0.write(i+2, 2, mean_r1[i])
		sheet_0.write(i+2, 3, 1-mean_p1[i])
		sheet_0.write(i+2, 4, 1-mean_r1[i])
	for j in range(len(prob_thres)):
		sheet_0.write(j+2, 5, prob_thres[j])
		sheet_0.write(j+2, 6, mean_p2[j])
		sheet_0.write(j+2, 7, mean_r2[j])
		sheet_0.write(j+2, 8, 1-mean_p2[j])
		sheet_0.write(j+2, 9, 1-mean_r2[j])
	for u in range(len(prob_thres)):
		sheet_0.write(u+2, 10, prob_thres[u])
		sheet_0.write(u+2, 11, mean_p3[u])
		sheet_0.write(u+2, 12, mean_r3[u])
		sheet_0.write(u+2, 13, 1-mean_p3[u])
		sheet_0.write(u+2, 14, 1-mean_r3[u])

	file.save("{}/face_detect.xlsx".format(args.save_dir))  #save xlsx



if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')
	args = parse_args()
	save_name = args.anno_dir.split("/")[-1]
	print "save_name" ,save_name
	gt_pred1_list = get_gt_pred_list(args.anno_dir, args.pred1_dir )
	gt_pred2_list = get_gt_pred_list(args.anno_dir, args.pred2_dir )
	gt_pred3_list = get_gt_pred_list(args.anno_dir, args.pred3_dir )
	scale_range_list = eval(args.scale_ranges)	#(0,1000)
	if not isinstance(scale_range_list[0], list) and not isinstance(scale_range_list[0], tuple):
		scale_range_list = (scale_range_list,)

	iou_list = eval(args.ious)  #(0.5,)
	if not isinstance(iou_list, list) and not isinstance(iou_list, tuple):
		iou_list = (iou_list,)
	
	plt.figure(figsize=(8, 7))
	stats1 = []
	stats2 = []
	stats3 = []
	for iou_thres in iou_list:
		for scale_range in scale_range_list:
			mean_p1, mean_r1 = roc(gt_pred1_list, args.save_dir, iou_thres, args.include_cls,args.resized_height, scale_range, args.rescale_thres)
			mean_p2, mean_r2 = roc(gt_pred2_list, args.save_dir, iou_thres, args.include_cls,args.resized_height, scale_range, args.rescale_thres)
			mean_p3, mean_r3 = roc(gt_pred3_list, args.save_dir, iou_thres, args.include_cls,args.resized_height, scale_range, args.rescale_thres)

			stats1.append([mean_p1, mean_r1])	#[[mean_p1[0] mean_p1[1] ... mean_p1[n]],[mean_r1[0] mean_r1[1] ... mean_r1[n]]]
			stats2.append([mean_p2, mean_r2])
			stats3.append([mean_p3, mean_r3])

	for mean_p1, mean_r1 in stats1:
		plt.plot(mean_p1, mean_r1, 'o-')
	for mean_p2, mean_r2 in stats2:
		plt.plot(mean_p2, mean_r2,'*-')
	for mean_p3, mean_r3 in stats3:
		plt.plot(mean_p3, mean_r3, 'o-')

	plt.grid(True)
	plt.xlim([0, 1])
	plt.ylim([0, 1])
	plt.xlabel("precision")
	plt.ylabel("recall")
	plt.title("face_detect_iou[0.5]_scale[0-1000]")
	#plt.legend(['iou: {} scale: [{}, {}]'.format(iou_thres, scale_range[0], scale_range[1]) for iou_thres in iou_list for scale_range in scale_range_list], loc="upper left")
	plt.legend( ["Vega_docker","Vega_V2","Vega_Matrix"], loc = "upper left")
	plt.savefig("{}/{}.png".format(args.save_dir,save_name))
	save_xlsx()
