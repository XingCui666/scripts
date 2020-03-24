#!/usr/bin/env python
#!encoding=utf-8

import json
import os
import cv2
import sys


def main(origin_res_path, save_path):
    
    images = []
    categories = []
    annotations = []
    box_id = 0
    slide_id = 0
    
    for category in category_conf:
        category_data = {
            "id": category_conf[category],
            "name": category
        }
        categories.append(category_data)
    
    with open(origin_res_path, 'r') as f:
        data_list = json.load(f)
    images_distinct = []
    for image_name in data_list:
        data = data_list[image_name]
        image_url = data['image_url']
        cap = cv2.VideoCapture(image_url)
        ret, img = cap.read()
        sp = img.shape
        img_data = {
            "file_name": image_name,
            "id": image_name,
            "width": sp[1],
            "height": sp[0]
        }
        if image_name not in images_distinct:
            images_distinct.append(image_name)
            images.append(img_data)
        for box in data['data']:
            x = round(box['bbox'][0], 0)
            y = round(box['bbox'][1], 0)
            w = round(box['bbox'][2], 0)
            h = round(box['bbox'][3], 0)
            bbox = [int(x), int(y), int(w), int(h)]
            if box['type'] == 'body':
                category_id = category_conf['body']
            elif box['type'] == 'head':
                category_id = category_conf['head']
            elif box['type'] == 'face' or box['type'] == 'realface':
                if model == 'f':
                    category_id = category_conf['face']
                else:
                    if box["values"]["angle"] == 0:  #0:正脸  1:侧脸
                        category_id = category_conf['face']
                    else:
                        slide_id += 1
                        continue
            annotation_data = {
                "segmentation": [],
                "area": int(w * h),
                "iscrowd": 0,
                "image_id": image_name,
                "bbox": bbox,
                "category_id": category_id,
                "id": box_id
            }
            box_id += 1
            annotations.append(annotation_data)
    print 'skip side face: ', slide_id
    result = {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }
    with open(os.path.join(save_path,res_file), 'w') as f:
        json.dump(result, f, indent=4)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "usage: python convert_anno_to_coco.py anno_json_file model save_path"
        sys.exit(-1)
    origin_res_path = sys.argv[1]
    model = sys.argv[2]
    save_path = sys.argv[3]
    if model == 'bhf':
        category_conf = {"body": 1, "head": 2, "face": 3}
    elif model == 'hf':
        category_conf = {"head": 1, "face": 2}
    elif model == 'f':
        category_conf = {"face": 1}
    res_file = os.path.basename(origin_res_path)[0:-4] + 'coco'
    main(origin_res_path, save_path)

