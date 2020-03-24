#!/usr/bin/env python
#!coding=utf-8

import os
import sys
import random
import cv2

frame_interval = 350
store = "gloria_beijing_hgbh"

def extract(video_path, save_path):
    channel_lst = os.listdir(video_path)
    for channel in channel_lst:
        channel_path = os.path.join(video_path, channel)
        video_lst = os.listdir(channel_path)
        des_video_lst = random.sample(video_lst, 10) #随机抽取10段视频
        for video in des_video_lst:
            video_file = os.path.join(channel_path, video)
            print "reading video:", video_file
            #cmd_extract = "select=not(mod(n\,%d))" % frame_interval
            #cmd = 'ffmpeg -i ' + video_file + ' -q:v 2 -vf "%s" -vsync 0 ' % cmd_extract + save_path + '/{}.%05d.jpg'.format(video)
            cap = cv2.VideoCapture(video_file)
            cap.open(video_file)
            frame_index = 0
            if cap.isOpened():
                status = True
            else:
                status = False
                print "open video failed!"

            while(status):
                status, frame = cap.read()
                print "---> read frame:%d" % frame_index, status

                frame_index += 1
                if frame_index % frame_interval == 0:
                    cv2.imwrite(save_path + '/' + store + '_' + video + ".%d.jpg" % frame_index, frame)

            cap.release()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage: python video_path save_pic_path"
        sys.exit(-1)

    video_path = sys.argv[1]
    save_path = sys.argv[2]
    extract(video_path, save_path)
