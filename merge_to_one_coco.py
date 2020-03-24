#!/usr/bin/env python
#!coding=utf-8

'''
Author: xingcui
Function: Combine multiple coco files into one coco file
'''
import os
import sys
import json


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "python merge_to_one_coco.py coco_dir save_name"
        sys.exit(-1)
    coco_dir = sys.argv[1]
    save_name = sys.argv[2]
    json_lst = os.listdir(coco_dir)
    gt_new = {}
    pic_map = {}
    id = 0
    for json_file in json_lst:
        print json_file
        with open(coco_dir + '/' + json_file, 'r') as jf:
            gt_info = json.loads(jf.read())
        if "images" not in gt_new:
            gt_new["images"] = []
        for img_dict in gt_info['images']:
            if img_dict['file_name'] not in pic_map:
                pic_map[img_dict['file_name']] = 1
                gt_new["images"].append(img_dict)
        if "annotations" not in gt_new:
            gt_new["annotations"] = []
        for bbox_info in gt_info['annotations']:
            bbox_info['id'] = id
            id += 1
            gt_new["annotations"].append(bbox_info)
        if "categories" not in gt_new:
            #gt_new["categories"] = [{"id": 1, "name": "body"}, {"id": 2, "name": "head"}, {"id": 3, "name": "face"}]
            #gt_new["categories"] = [{"id": 1, "name": "head"}, {"id": 2, "name": "face"}]
            gt_new["categories"] = [{"id": 1, "name": "face"}]
    with open(coco_dir + '/' + save_name, 'w') as f:
        json.dump(gt_new, f, indent=4)
