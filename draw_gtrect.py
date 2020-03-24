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
    gt_lst = gt_dict['annotations']
    for gt in gt_lst:
        image_id = gt['image_id']
        image_name = image_id
        if image_name not in os.listdir(img_dir):
            continue
        bbox = gt['bbox']
        category = gt['category_id']
        if image_id not in gt_info:
            gt_info[image_id] = []
        if category == 2:
            gt_info[image_id].append(bbox)
    for image in gt_info.keys():
        img = os.path.join(img_dir, image)
        img = cv2.imread(img)
        bbox_gt = gt_info[image]
        if len(bbox_gt) != 0:
            for box in bbox_gt:
                box = [int(b) for b in box]
                x1 = box[0]
                y1 = box[1]
                x2 = box[0] + box[2]
                y2 = box[1] + box[3]
                img_rect = cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,0), 2) #blue:gt
            save_name = os.path.join(save_path, image)
            cv2.imwrite(save_name, img_rect)

if __name__ == '__main__':
    if (len(sys.argv) < 4):
        print "python draw_rect.py gt_coco_file img_dir save_path"
        sys.exit(-1)
    gt_file = sys.argv[1]
    img_dir = sys.argv[2]
    save_path = sys.argv[3]
    os.system("mkdir -p {}".format(save_path))
    with open(gt_file) as f:
        gt_dict = json.load(f)
    run()
