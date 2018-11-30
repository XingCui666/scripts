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

#prob_thres = [0.1, 0.15]
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


def get_gt_txt(gt_txt, scale_range):
	bbs = []
	lst = gt_txt.strip("\n").split()
	lst_len = len(lst)
	cycle = (lst_len - 1) / 4
	if lst_len != 1:
		for i in range(cycle):
			pred = map(int, lst[i*4+1:(i+1)*4+1])
			if pred[2] >= scale_range[0] and pred[2] < scale_range[1]:
				bbs.append(pred)
	else:
		pass
	return np.array(bbs)	#for example:[[1,2,3,4]
							#			  [5,6,7,8]]


def get_pred_txt(pred_txt, scale_range):
	probs = []
	bbs = []
	lst = pred_txt.strip("\n").split()
	lst_len = len(lst)
	cycle = (lst_len - 1) / 5
	if lst_len != 1:
		for i in range(cycle):
			pred = map(int, lst[i*5+1:(i+1)*5])
			score = float(lst[(i+1)*5])
			if pred[2] >= scale_range[0] and pred[2] < scale_range[1]:
				bbs.append(pred)
				probs.append(score)

	else:
		pass
	return np.array(bbs), np.array(probs)	#for example:[[1,2,3,4]
											#			  [5,6,7,8]]


def pr(gt_pred_list, save_dir, iou_thres, is_include_cls, resized_height, scale_range, rescale_thres=False):
	precisions = list()
	recalls = list()
	errors = list()
	cnt = 0
	max_prob = 1
	if rescale_thres is True:
		prob_list = list()
		for line in gt_pred_list:
			dump, pred_txt = line
			dump, probs = get_pred_txt(pred_txt, scale_range)
			prob_list.extend(probs)
		max_prob = max(prob_list)
	new_prob_thres = [one_prob_thres * max_prob for one_prob_thres in prob_thres]
	print "=========start transform========="
	for line in gt_pred_list:
		gt_txt, pred_txt = line
		gt = get_gt_txt(gt_txt, scale_range)
		pred, probs = get_pred_txt(pred_txt, scale_range)

		precisions.append(list())
		recalls.append(list())
		errors.append(list())
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
			if len(gt) == 0:
				error = 1.0
			else:
				error = len(pred_k)*(1 - c) / len(gt)
			errors[-1].append(float(error))
		cnt += 1
		if cnt % 100 == 0:
			print "precessed {}".format(cnt)
	print "=========end transform==========="
	precisions = np.array(precisions)
	recalls = np.array(recalls)
	errors = np.array(errors)
	pr_save_dir = "{}".format(save_dir)
	mean_p = np.mean(precisions, axis=0)
	mean_r = np.mean(recalls, axis=0)
	errors = np.mean(errors, axis=0)
	return (mean_p, mean_r, errors)		#([p[0] p[1] ... [pn]],[r[0] r[1] ... r[n]])


def get_gt_pred_list(gt_file, pred_file):
	with open(gt_file) as f_gt,  open(pred_file) as f_pred:
		all_gt_list = f_gt.readlines()
		all_pred_list = f_pred.readlines()
	gt_pred_list = zip(all_gt_list, all_pred_list)

	return gt_pred_list	#for example:[(gt.txt1,pred.txt1),(gt.txt2,pred.txt2),...,(gt.txtn,pred.txtn)]

def parse_args():
	parser = argparse.ArgumentParser(description='pr')
	parser.add_argument('--anno_file', dest='anno_file', help='gt file', type=str)
	parser.add_argument('--pred1_file', dest='pred1_file', help='pred_RFCN file', type=str)
	parser.add_argument('--pred2_file', dest='pred2_file', help='pred_SSD file', type=str)
	parser.add_argument('--save_dir', dest='save_dir', help='save dir', type=str)
	parser.add_argument('--resized_height', dest='resized_height', default=None, help='img height when test',
						type=float)
	parser.add_argument('--ious', dest='ious', default="(0.5,)", help='ious to compute pr, should be tuple or list',
						type=str)
	parser.add_argument('--scale_ranges', dest='scale_ranges', default="(0,1000)",
						help='split range scales to compute pr, "(s1,s2),(s3,s4),..."',
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
	if not os.path.exists("{}/{}_detect.xlsx".format(args.save_dir,save_name)):
		file = xlwt.Workbook(encoding = 'utf-8')
		sheet = file.add_sheet(save_name[2]) 
		sheet.write_merge(0,0,0,4,'RFCN')
		sheet.write(1, 0, u'阈值')
		sheet.write(1, 1, u'准确率')
		sheet.write(1, 2, u'召回率')
		sheet.write(1, 3, u'误检率')
		sheet.write(1, 4, u'漏检率')
		sheet.write_merge(0,0,5,9,'SSD')
		sheet.write(1, 5, u'阈值')
		sheet.write(1, 6, u'准确率')
		sheet.write(1, 7, u'召回率')
		sheet.write(1, 8, u'误检率')
		sheet.write(1, 9, u'漏检率')
	
																		
	for i in range(len(prob_thres)):
		sheet.write(i+2, 0, prob_thres[i])
		sheet.write(i+2, 1, mean_p1[i])
		sheet.write(i+2, 2, mean_r1[i])
		sheet.write(i+2, 3, err1[i])
		sheet.write(i+2, 4, 1-mean_r1[i])
	for j in range(len(prob_thres)):
		sheet.write(j+2, 5, prob_thres[j])
		sheet.write(j+2, 6, mean_p2[j])
		sheet.write(j+2, 7, mean_r2[j])
		sheet.write(j+2, 8, err2[j])
		sheet.write(j+2, 9, 1-mean_r2[j])

	file.save("{}/{}_detect.xlsx".format(args.save_dir,save_name[2]))  #save xlsx

def AUC(mean_r, mean_p):
	auc = 0
	for i in range(len(prob_thres)):
		if i == 0:
			continue
		auc += (mean_r[i-1] - mean_r[i]) * mean_p[i]
	return "%.6f" % auc

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')

	args = parse_args()
	gt_pred1_list = get_gt_pred_list(args.anno_file, args.pred1_file )
	gt_pred2_list = get_gt_pred_list(args.anno_file, args.pred2_file )
	scale_range_list = eval(args.scale_ranges)	#(0,1000)
	if not isinstance(scale_range_list[0], list) and not isinstance(scale_range_list[0], tuple):
		scale_range_list = (scale_range_list,)

	iou_list = eval(args.ious)  #(0.5,)
	if not isinstance(iou_list, list) and not isinstance(iou_list, tuple):
		iou_list = (iou_list,)
	
	plt.figure(figsize=(8, 7))
	stats1 = []
	stats2 = []
	for iou_thres in iou_list:
		for scale_range in scale_range_list:
			mean_p1, mean_r1, err1 = pr(gt_pred1_list, args.save_dir, iou_thres, args.include_cls,args.resized_height, scale_range, args.rescale_thres)
			mean_p2, mean_r2, err2 = pr(gt_pred2_list, args.save_dir, iou_thres, args.include_cls,args.resized_height, scale_range, args.rescale_thres)

			stats1.append([mean_p1, mean_r1])	#[[mean_p1[0] mean_p1[1] ... mean_p1[n]],[mean_r1[0] mean_r1[1] ... mean_r1[n]]]
			stats2.append([mean_p2, mean_r2])
	for mean_p1, mean_r1 in stats1:
		plt.plot(mean_p1, mean_r1, 'bo-')
	for mean_p2, mean_r2 in stats2:
		plt.plot(mean_p2, mean_r2,'ro-')
#	plt.plot([mean_p1[0], mean_p1[0]], [0, mean_r1[0]], color = 'blue', linewidth = 0.5, linestyle = "--")
#	plt.plot([0, mean_p1[0]], [mean_r1[0], mean_r1[0]], color = 'blue', linewidth = 0.5, linestyle = "--")
#	plt.plot([mean_p2[0], mean_p2[0]], [0, mean_r2[0]], color = 'red' , linewidth = 0.5, linestyle = "--")
#	plt.plot([0, mean_p2[0]], [mean_r2[0], mean_r2[0]], color = 'red' , linewidth = 0.5, linestyle = "--")
	auc1 = AUC(mean_r1, mean_p1)
	auc2 = AUC(mean_r2, mean_p2)
	plt.plot([0,1], color = 'red', linewidth = 1, linestyle = "--")
	plt.grid(True)
	plt.xlim([0, 1])
	plt.ylim([0, 1])
	plt.xlabel("Recall")
	plt.ylabel("Precision")
	scene_table = {"0.100000":"monitor", "0.900000":"licence"}
	save_name = os.path.basename(args.anno_file).split("_")
	plt.title("{}_{}_{}_iou[0.5]".format(save_name[0], scene_table[save_name[1]], save_name[2]))
	plt.legend( ["RFCN(AUC=%s)" % auc1 ,"SSD(AUC=%s)" % auc2] , loc = "upper left")
	plt.savefig("{}/{}_{}_{}_iou[0.5].jpg".format(args.save_dir, save_name[0], scene_table[save_name[1]], save_name[2]))
	save_xlsx()
