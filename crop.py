#!/usr/bin/env python
#!coding=utf8
'''
crop pic by gt_file
XingCui
'''
import os,sys
import json
import cv2
import numpy as np

def padding(part_img_array, enlarg_box_w, enlarg_box_h):
    H, W = enlarg_box_h, enlarg_box_w
    h = part_img_array.shape[0]
    w = part_img_array.shape[1]
    img_array = np.zeros((H, W, 3), dtype=np.uint8())
    img_array[(H - h) // 2 : (H + h) // 2, (W - w) // 2 : (W + w) // 2, :] = part_img_array
    return img_array


def crop(full_img_array, bbox, ratio_left, ratio_top, ratio_right, ratio_bottom):
    x, y, w, h = map(int, bbox)[:]
    sp = full_img_array.shape
    X1 = x - int(ratio_left * w)
    Y1 = y - int(ratio_top * h)
    W = w + int(w * (ratio_left + ratio_right))
    H = h + int(h * (ratio_top + ratio_bottom))
    X2 = X1 + W
    Y2 = Y1 + H
    if 0<=X1<=sp[1] and 0<=Y1<=sp[0]:
        if 0<=X2<=sp[1] and 0<=Y2<=sp[0]:
            crop_img_array = full_img_array[Y1:Y2, X1:X2] #左上、右下坐标均在图片像素内
        else:
            tmp_img_array = full_img_array[Y1:min(Y1+H, sp[0]), X1:min(X1+W, sp[1])] #左上坐标点在图片像素内，右下坐标点在像素外
            crop_img_array = padding(tmp_img_array, W, H)

    else:
        tmp_img_array = full_img_array[max(Y2-H, 0):min(Y2, sp[0]), max(X2-W, 0):min(X2, sp[1])] #左上坐标点不在图片像素内，右下坐标点在/不在像素内
        crop_img_array = padding(tmp_img_array, W, H)

    return crop_img_array


def loadGT_COCO(gt_coco):
    img_bbox = {}
    img_id = {}
    with open(gt_coco) as f:
        data = json.load(f)
    anno_data = data['annotations']
    img_data = data['images']

    for img in img_data:
        img_name = img['file_name']
        idx = img['id']
        img_id[idx] = img_name
        img_bbox[img_name] = []
    for anno in anno_data:
        image_id = anno['image_id']
        img_name = img_id[image_id]
        bbox = anno['bbox']
        category = anno['category_id']
        if category == 1: #1:head 2:face or 1:body 2:head 3:face
            img_bbox[img_name].append(bbox)
    return img_bbox


def loadGT_TXT(gt_txt):
    with open(gt_txt) as f:
        gt_data = f.readlines()
    img_bbox = {}
    for gt in gt_data:
        parts = gt.strip().split(',')
        img_name = os.path.basename(parts[0])
        if img_name not in img_bbox:
            img_bbox[img_name] = []
        cnt = (len(parts) - 1) / 5
        for i in range(cnt):
            bbox = parts[i * 5 + 1:i * 5 + 5]
            img_bbox[img_name].append(bbox)
    return img_bbox


def readPicCrop(gt_file, img_dir, targetPath):
    try:
        if os.path.splitext(gt_file)[1] == '.coco':
            img_bbox_dict = loadGT_COCO(gt_file)
        elif os.path.splitext(gt_file)[1] == '.txt':
            img_bbox_dict = loadGT_TXT(gt_file)
        for img_name in img_bbox_dict.keys():
            count = 1
            img_full_path = os.path.join(img_dir, img_name)
            bboxs = img_bbox_dict[img_name]
            img = cv2.imread(img_full_path)
            if img is None:
                continue
            else:
                if type(img) != str:
                    if len(bboxs) != 0:
                        for bbox in bboxs:
                            if bbox[2] > 0 and bbox[3] > 0:
                                cropped = crop(img, bbox, 0.6, 0.15, 0.6, 0.5) #left top right bottom, 向左右各扩60%，向上外扩10%，向下外扩50%
                                cv2.imwrite(targetPath + os.sep + '%s_crop_%s.jpg' % (img_name[:-4], count), cropped)
                                count += 1
                    else:
                        #如果图中没有目标，则取图片中心像素的256*256区域保存
                        H, W = img.shape[:2]
                        cropped = img[H // 2 - 128:H // 2 + 128, W // 2 - 128:W // 2 + 128]
                        cv2.imwrite(targetPath + os.sep + '%s_crop.jpg' % (img_name[:-4]), cropped)

    except Exception as err:
        print err
 
 
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "usage: python crop.py gt_coco_file img_dir pic_save_path"
        sys.exit(-1)
    gt_coco = sys.argv[1] #gt coco file
    img_dir = sys.argv[2] #img dir path
    targetPath = sys.argv[3] #croped save path
    os.system("mkdir -p {}".format(targetPath))
    readPicCrop(gt_coco, img_dir, targetPath)
