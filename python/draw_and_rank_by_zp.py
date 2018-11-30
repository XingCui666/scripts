#!/usr/bin/env python
#!coding=utf-8

import os
import sys
import cv2


font = cv2.FONT_HERSHEY_SIMPLEX

def calRatio(pos1, pos2):
    ratio = 0.0
    x1 = float(pos1[0])
    x2 = float(pos2[0])
    y1 = float(pos1[1])
    y2 = float(pos2[1])
    width1 = float(pos1[2])
    width2 = float(pos2[2])
    height1 = float(pos1[3])
    height2 = float(pos2[3])

    startx = min(x1, x2)
    endx = max(x1+width1, x2+width2)
    width = width1 + width2 - (endx - startx)

    starty = min(y1, y2)
    endy = max(y1+height1, y2+height2)
    height = height1 + height2 - (endy - starty)

    if (width <= 0) or (height <= 0):
        ratio = 0.0
    else:
        area = width * height
        area1 = width1 * height1
        area2 = width2 * height2
        ratio = area*1.0 / (area1 + area2 - area)
    return ratio

def checkRoiIn(aroi, brois):

    inflag = False
    for broi in brois:
        iou = calRatio(aroi, broi)
        if iou > 0.5:
            return broi

    return inflag

# draw
def drawSingle(img, arois, atype, head):

    img = "12imagesall/" + img.split("/")[-2] + "/" + img.split("/")[-1]
    #print('img:', img)
    im = cv2.imread(img.strip("\r\n"))
    im_copy = im.copy()

    for aroi in arois:
        x = aroi[0]
        y = aroi[1]
        x1 = aroi[0]+aroi[2]
        y1 = aroi[1]+aroi[3]
        cv2.putText(im_copy, str(atype), (x, y), font, 1, (0, 0, 255), 3)
        cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(0,0,255),3) # color: B-G-R

    imgname = img.split("/")
    imgname = head + "/" + imgname[-2] + "_" + imgname[-1]
    #print('imgname:', imgname)
    cv2.imwrite(imgname, im_copy)

# draw
def draw(img, arois, brois, head):

    img = "12imagesall/" + img.split("/")[-2] + "/" + img.split("/")[-1]
    #print('img:', img)
    im = cv2.imread(img.strip("\r\n"))
    im_copy = im.copy()

    for aroi, broi in zip(arois, brois):
        #print('roi:', roi)
        atype = aroi[-1]
        btype = broi[-1]
        x = aroi[0]
        y = aroi[1]
        x1 = aroi[0]+aroi[2]
        y1 = aroi[1]+aroi[3]
        cv2.putText(im_copy, str(atype), (x, y), font, 1, (0, 0, 255), 1)
        cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(0,0,255),3) # color: B-G-R

        x = broi[0]
        y = broi[1]
        x1 = broi[0]+broi[2]
        y1 = broi[1]+broi[3]
        cv2.putText(im_copy, str(btype), (x, y+30), font, 1, (255, 0, 0), 1)
        cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(255,0,0),3) # color: B-G-R

    imgname = img.split("/")
    imgname = head + "/" + imgname[-2] + "_" + imgname[-1]
    #print('imgname:', imgname)
    cv2.imwrite(imgname, im_copy)

# draw
def drawroi(img=None, aroi=None, broi=None, head=None):

    img = "12imagesall/" + img.split("/")[-2] + "/" + img.split("/")[-1]
    #print('img:', img)
    im = cv2.imread(img.strip("\r\n"))
    im_copy = im.copy()

    x = aroi[0]
    y = aroi[1]
    x1 = aroi[0]+aroi[2]
    y1 = aroi[1]+aroi[3]
    cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(0,0,255),1) # color: B-G-R

    x = broi[0]
    y = broi[1]
    x1 = broi[0]+broi[2]
    y1 = broi[1]+broi[3]
    cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(255,0,0),1) # color: B-G-R

    imgname = img.split("/")
    imgname = head + "/" + imgname[-2] + "_" + imgname[-1]
    #print('imgname:', imgname)
    cv2.imwrite(imgname, im_copy)

def typeCheck(aDir, bDir):

    saveDir = aDir.split("_")[-1]

    a32a48 = 0
    b32b48 = 0
    for (a, b) in zip(os.listdir(aDir), os.listdir(bDir)):

        raDir = os.path.realpath(aDir)
        rbDir = os.path.realpath(bDir)

        ra = raDir + "/" + a
        rb = rbDir + "/" + b

        #print('ra:{} rb:{}'.format(ra, rb))
        with open(ra) as fa, open(rb) as fb:
            for linea, lineb in zip(fa, fb):
                #print('linea:{} lineb:{}'.format(linea, lineb))

                # deal with ra
                ajpg = linea.split(" ")[0]
                nonjpg = linea.split(".jpg ")[-1]
                nonjpg_split = nonjpg.split(" ")
                len_nonjpg_split = len(nonjpg_split)
                len_nonjpg_split_per6 = len_nonjpg_split/6

                actypes = []
                awidths = []
                arois = []
                for i in range(len_nonjpg_split_per6):
                    ctype = nonjpg_split[i*6+1]

                    ax = int(nonjpg_split[i*6+2])
                    ay = int(nonjpg_split[i*6+3])
                    aw =  int(nonjpg_split[i*6+4])
                    ah = int(nonjpg_split[i*6+5])

                    actypes.append(ctype)
                    awidths.append(aw)
                    arois.append([ax,ay,aw,ah])

                # deal with rb
                bjpg = lineb.split(" ")[0]
                nonjpg = lineb.split(".jpg ")[-1]
                nonjpg_split = nonjpg.split(" ")
                len_nonjpg_split = len(nonjpg_split)
                len_nonjpg_split_per6 = len_nonjpg_split/6

                bctypes = []
                bwidths = []
                brois = []
                for i in range(len_nonjpg_split_per6):
                    ctype = nonjpg_split[i*6+1]
                    bx = int(nonjpg_split[i*6+2])
                    by = int(nonjpg_split[i*6+3])
                    bw =  int(nonjpg_split[i*6+4])
                    bh = int(nonjpg_split[i*6+5])

                    bctypes.append(ctype)
                    bwidths.append(bw)
                    brois.append([bx,by,bw,bh])

                # check iou
                index = 0
                draw_arois1 = []
                draw_brois1 = []

                draw_arois2 = []
                draw_brois2 = []

                draw_arois3 = []
                draw_brois3 = []

                draw_arois4 = []
                draw_brois4 = []

                for actype, aroi in zip(actypes, arois):
                    if int(actype) == 1:
                        broi = checkRoiIn(aroi, brois)
                        if not broi:  
                            draw_arois1.append(aroi)
                        else:
                            draw_brois1.append(broi)

                    elif int(actype) == 2:
                        broi = checkRoiIn(aroi, brois)
                        if not broi:
                            draw_arois2.append(aroi)
                        else:
                            draw_brois2.append(broi)

                    elif int(actype) == 3:
                        broi = checkRoiIn(aroi, brois)
                        if not broi:
                            draw_arois3.append(aroi)
                        else:
                            draw_brois3.append(broi)

                    elif int(actype) == 4:
                        broi = checkRoiIn(aroi, brois)
                        if not broi:
                            draw_arois4.append(aroi)
                        else:
                            draw_brois4.append(broi)

                if len(draw_arois1) != 0:
                    #print('arois:', arois)
                    #print('brois:', brois)
                    #print('draw_arois1:', draw_arois1)
                    #print('ajpg:', ajpg)
                    drawSingle(ajpg, draw_arois1, 1, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/vehicle_{}".format(saveDir))
                    #drawSingle(ajpg, draw_brois1, 1, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/vehicle_0.7.1.2")

                if len(draw_arois2) != 0:
                    drawSingle(ajpg, draw_arois2, 2, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/pedestrian_{}".format(saveDir))
                    #drawSingle(ajpg, draw_brois2, 2, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/pedestrian_0.7.1.2")

                if len(draw_arois3) != 0:
                    drawSingle(ajpg, draw_arois3, 3, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/bicycle_{}".format(saveDir))
                    #drawSingle(ajpg, draw_brois3, 3, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/bicycle_0.7.1.2")

                if len(draw_arois4) != 0:
                    drawSingle(ajpg, draw_arois4, 4, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/tricycle_{}".format(saveDir))
                    #drawSingle(ajpg, draw_brois4, 4, "/root/zhouping/Triumpth0.0.7/testResult/detector/drawResult/tricycle_0.7.1.2")

                
if __name__ == "__main__":
    aDir = sys.argv[1]
    bDir = sys.argv[2]
    typeCheck(aDir, bDir)
