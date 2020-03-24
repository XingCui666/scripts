#!/usr/bin/env python
#!coding=utf-8


import os
import sys
import json

def merge(anno_dir, save_name):
    new_anno = {}

    anno_lst = os.listdir(anno_dir)
    for anno_file in anno_lst:
        anno_file = os.path.join(anno_dir, anno_file)
        with open(anno_file, 'r') as f:
            anno_data = json.load(f)
        for anno in anno_data:
            new_anno[anno] = anno_data[anno]

    with open(anno_dir + '/' + save_name, 'w') as f:
        json.dump(new_anno, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "python merge_to_one_json.py anno_json_dir save_name"
        sys.exit(-1)
    anno_dir = sys.argv[1]
    save_name = sys.argv[2]
    merge(anno_dir, save_name)
