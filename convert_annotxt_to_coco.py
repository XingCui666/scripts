#!/usr/bin/env python
#!encoding=utf-8

import json
import os
import cv2
import sys


def main(origin_res_path, save_path, img_dir):
    
    images = []
    categories = []
    annotations = []
    box_id = 0
    
    for category in category_conf:
        category_data = {
            "id": category_conf[category],
            "name": category
        }
        categories.append(category_data)
    
    with open(origin_res_path, 'r') as f:
        data_list = f.readlines()
    for data in data_list:
        parts = data.strip().split(',')
        image_name = os.path.basename(parts[0])
        abs_images_name = os.path.join(img_dir, image_name)
        img = cv2.imread(abs_images_name)
        sp = img.shape
        img_data = {
            "file_name": image_name,
            "id": image_name,
            "width": sp[1],
            "height": sp[0]
        }
        images.append(img_data)
        bboxs = parts[1:]
        box_num = int(len(bboxs) / 5)
        for i in range(box_num):
            x = int(bboxs[i*5 + 0])
            y = int(bboxs[i*5 + 1])
            w = int(bboxs[i*5 + 2])
            h = int(bboxs[i*5 + 3])
            category_id = int(bboxs[i*5 + 4])
            bbox = [x, y, w, h]
            annotation_data = {
                "segmentation": [],
                "area": w * h,
                "iscrowd": 0,
                "image_id": image_name,
                "bbox": bbox,
                "category_id": category_id,
                "id": box_id
            }
            box_id += 1
            annotations.append(annotation_data)
    result = {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }
    with open(os.path.join(save_path,res_file), 'w') as f:
        json.dump(result, f, indent=4)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "usage: python convert_anno_to_coco.py anno_txt_file model save_path img_dir"
        sys.exit(-1)
    origin_res_path = sys.argv[1]
    model = sys.argv[2]
    save_path = sys.argv[3]
    img_dir = sys.argv[4]
    if model == 'bhf':
        category_conf = {"body": 1, "head": 2, "face": 3}
    elif model == 'hf':
        category_conf = {"head": 1, "face": 2}
    elif model == 'f':
        category_conf = {"face": 1}
    res_file = os.path.basename(origin_res_path)[0:-3] + 'coco'
    main(origin_res_path, save_path, img_dir)

