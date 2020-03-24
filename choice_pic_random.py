#!/usr/bin/env python
#!coding=utf-8


import sys,os
import shutil
import random

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage: python img_dir save_path"
        sys.exit(-1)

    img_dir = sys.argv[1]
    save_path = sys.argv[2]
    os.system("mkdir -p {}".format(save_path))
    img_lst = os.listdir(img_dir)
    
    len_img = len(img_lst)
    new_lst = random.sample(img_lst, 250)
    
    for img in new_lst:
        shutil.move(os.path.join(img_dir, img), save_path)

