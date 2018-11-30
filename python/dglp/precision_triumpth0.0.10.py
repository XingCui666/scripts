#!/usr/bin/env python
#!coding=utf-8
import sys
import os
import threading
import multiprocessing as mp
import time

reload(sys)
sys.setdefaultencoding('utf-8')

num_Count = mp.Value('i', 0)
col_Count = mp.Value('i', 0)

def cal_dglp_number(i):
    global num_Count
    gt_name = gt_list[i].strip("\n").split(";")[0]
    gt_number = ":" + gt_list[i].strip("\n").split(";")[1].split(",")[0]
    if gt_name in pred_name_list:
        for pred in pred_list:
            pred_name = pred.strip("\n").split()[0]
            pred_len = len(pred.strip("\n").split())
            if gt_name == pred_name and pred_len != 1:
                if gt_number in pred.strip("\n").split():
                    with num_Count.get_lock():
                        num_Count.value += 1
                        print "num_Count ", num_Count.value
                else:
                    with open("mis_num.list", 'a+') as f:
                        f.write(gt_name + "\n")
                        break
    else:
        with open("lose_img.list", 'a+') as f:
            f.write(gt_name + "\n")
    return num_Count.value

def cal_dglp_color(i):
    global col_Count
    gt_color_table = {"B":"blue", "G":"green", "K":"black", "W":"white", "X":"yellowgreen", "Y":"yellow"}
    pred_color_table = {"0":"unknowd", "1":"blue", "2":"yellow", "3":"white", "4":"black", "5":"green", "6":"yellowgreen"}
    gt_color = gt_color_table[gt_list[i].strip("\n").split(";")[1].split(",")[1]]
    gt_name = gt_list[i].strip("\n").split(";")[0]
    gt_number = gt_list[i].strip("\n").split(";")[1].split(",")[0]
    if gt_name in pred_name_list:
        for pred in pred_list: 
            pred_name = pred.strip("\n").split()[0]
            pred_len = len(pred.strip("\n").split())
            cycle = (pred_len - 1) / 9
            if gt_name == pred_name and pred_len !=1: 
                for j in range(cycle):
                    pred_number = pred.strip("\n").split()[(j+1)*9].strip(":")
                    pred_score = float(pred.strip("\n").split()[(j+1)*9-1].split(":")[1])
                    pred_color = pred_color_table[pred.strip("\n").split()[(j+1)*9-2].strip(":")]
                    if gt_number == pred_number:
                        if pred_score > 0.5:
                            if gt_color == pred_color:
                                with col_Count.get_lock():
                                    col_Count.value += 1
                                    print "col_Count ", col_Count.value
                            else:
                                with open("mis_col.list", 'a+') as f:
                                    f.write(gt_name + "\n")
                                    break

                            with open("mis_col.list", 'a+') as f:
                                f.write(gt_name + "\n")
                                break
    return col_Count.value


def dglp_number():
    global result_num
    for i in range(total):
        result_num = pool.apply_async(cal_dglp_number, args=(i,))

def dglp_color():
    global result_col
    for i in range(total):
        result_col = pool.apply_async(cal_dglp_color, args=(i,))

if __name__ == '__main__':
    if(len(sys.argv) < 3):
        print "start with: python gt_list pred_file"
        sys.exit(-1)
    gt_file = sys.argv[1]
    pred_file = sys.argv[2]

    if os.path.exists("mis_num.list"):
        os.system('rm mis_num.list')
    if os.path.exists("mis_col.list"):
        os.system('rm mis_col.list')
    if os.path.exists("lose_img.list"):
        os.system('rm lose_img.list')

    start = time.time()
    with open(gt_file) as f_gt, open(pred_file) as f_pred:
        gt_list = f_gt.readlines()
        pred_list = f_pred.readlines()
    total = len(gt_list)
    pred_name_list = []
    for pred in pred_list:
        pred_name_list.append(pred.split()[0])
    pool = mp.Pool()
    job1 = threading.Thread(target = dglp_number)
    job2 = threading.Thread(target = dglp_color)
    job1.setDaemon(True)
    job2.setDaemon(True)
    job1.start()
    job2.start()
    job1.join()
    job2.join()
    pool.close()
    pool.join()
    print "wait all task done..."
    time.sleep(7)
    number_Count = result_num.get()
    color_Count = result_col.get()
    print "total right number is: ", number_Count
    print "total right color is: ", color_Count
    num_precision = float(number_Count)/total
    col_precision = float(color_Count)/total
    print "num_precision: ", num_precision
    print "col_precision: ", col_precision
    end = time.time()
    print "cost total time: ", (end - start)
	
