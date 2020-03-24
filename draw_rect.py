#!/usr/bin/env python
#!coding=utf-8

'''
Author: xingcui
Function: draw bbox of groundtruth and predict on images
'''
import os
import cv2
import sys
import json



def run():
    cwd = os.getcwd()
    gt_info = {}
    pred_info = {}
    gt_lst = gt_dict['annotations']
    for gt in gt_lst:
        image_id = gt['image_id']
        bbox = gt['bbox']
        if image_id not in gt_info:
            gt_info[image_id] = []
        if gt['category_id'] == 2:  #只画face框
            gt_info[image_id].append(bbox)
    for pred in pred_lst:
        category = pred['category_id']
        if category == 2:  #face
            image_id = pred['image_id']
            bbox = pred['bbox']
            score = pred['score']
            if image_id not in pred_info:
                pred_info[image_id] = []
            if float(score) > 0:
                pred_info[image_id].append((bbox, score))
    for item in gt_info.keys():
        img = os.path.join(img_dir, item)
        img = cv2.imread(img)
        bbox_gt = gt_info[item]
        for box in bbox_gt:
            box = [int(b) for b in box]
            x1 = box[0]
            y1 = box[1]
            x2 = box[0] + box[2]
            y2 = box[1] + box[3]
            img_rect = cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,0), 2) #blue:gt
        if item not in pred_info:
            pass
        else:
            bbox_pred = pred_info[item]
            for box, score in bbox_pred:
                box = [int(b) for b in box]
                x1 = box[0]
                y1 = box[1]
                x2 = box[0] + box[2]
                y2 = box[1] + box[3]
                img = cv2.putText(img, str(round(score,2)), (box[0], box[1]), cv2.FONT_HERSHEY_TRIPLEX, 1, (0,0,255), 2)
                img_rect = cv2.rectangle(img, (x1,y1), (x2,y2), (0,0,255), 2) #red:pred
        save_name = os.path.join(save_path, item)
        cv2.imwrite(save_name, img_rect)

if __name__ == '__main__':
    if (len(sys.argv) < 5):
        print "python draw_rect.py gt_coco_file pred_json_file img_dir save_path"
        sys.exit(-1)
    gt_file = sys.argv[1]
    pred_file = sys.argv[2]
    img_dir = sys.argv[3]
    save_path = sys.argv[4]
    os.system("mkdir -p {}".format(save_path))
    with open(gt_file) as f1, open(pred_file) as f2:
        gt_dict = json.loads(f1.read())
        pred_lst = json.loads(f2.read())
    run()
