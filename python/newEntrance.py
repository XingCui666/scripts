#!/usr/bin/env python
#!coding=utf-8
'''
Created on 2018年4月24日

@author: Simba
'''

import os

import logService.logService as logService
import logging
import ftpModule
import multiprocessing
from multiprocessing import Value
#from queue import Queue
import time
import exception.myException as MYEXCEPTION
import math
import sys
import datetime
import config.config as CONFIG
import tokenBucket

total_count = 12588
uploadCount = Value('i', 0)

# 获得所有图片的绝对路径列表
def getImagesPathList(imagesDir):
    imagesList = os.listdir(imagesDir)
    imagePathList = []
    logging.info("Start to get imagePathList.")
    for i in imagesList:
        imagePathList.append(os.path.join(imagesDir, i))
    logging.info("Get imagePathList completed.")
    return imagePathList


# 将列表分为m份
def chunks(arr, m):
    n = int(math.ceil(len(arr) / float(m)))
    return [arr[i:i + n] for i in range(0, len(arr), n)]


# ftp上传文件
def uploadFileByFtp(iTup):
    # ip, port, ftpDir, user, passwd, passiveVal, fileList
    count = 0
    firstTime = datetime.datetime.now()
    ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
    # logService.initLogging()
    pidCount = 0
    for i in iTup[6]:
        nowtime = datetime.datetime.now()
        if 100 <= (nowtime - firstTime).seconds:
            ftp.quit()
            ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
            firstTime = datetime.datetime.now()
            count += 1

        ftpModule.uploadFile(ftp, i)
        #timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
        #print( "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i))
        infoStr = "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i)
        logging.info(infoStr)
        pidCount = pidCount + 1
    ftp.quit()
    countDic = {}
    countDic["reconnectNum"] = count
    countDic["uploadNum"] = pidCount
    return countDic
    # logService.destoryLogging()


# 不重连
def newUploadFileByFtp(iTup):
    # ip, port, ftpDir, user, passwd, passiveVal, fileList
    ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
    # logService.initLogging()
    uploadCount = 0
    discardCount = 0
    # 限流，如果令牌桶中有令牌，则上传图片，如果没有，则丢弃图片
    # 每秒往桶中存放3个令牌
    token = tokenBucket.TokenBucket(3, 200000)
    token._current_amount = 1000
    for i in iTup[6]:
        if token.consume(1):
            ftpModule.uploadFile(ftp, i)
            #timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
            #print( "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i))
            infoStr = "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i)
            logging.info(infoStr)
            uploadCount = uploadCount + 1
        else:
            discardCount = discardCount + 1
            print( time.time())
    print ("uploadcount is: ", uploadCount)
    ftp.quit()
    countDic = {}
    countDic["uploadNum"] = uploadCount
    countDic["discardNum"] = discardCount
    return countDic


# 检查ftp连接状态
def checkFtpStatus(ftp):
    if ftp.voidcmd("NOOP") == "200 OK":
        return True
    else:
        return False


# 子进程异常处理
def errInfo(e):
    raise

def bucketUploadFileByFtp(iTup):
    # ip, port, ftpDir, user, passwd, passiveVal, fileList
    #ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
    # logService.initLogging()
    #uploadCount = 0
    # 限流，如果令牌桶中有令牌，则上传图片，如果没有，则空循环
    # 每秒往桶中存放3个令牌
    global total_count, uploadCount
    #uploadCount = 0
    token = tokenBucket.TokenBucket(3, 1000000)
    token._current_amount = 1
    index = 0
    #lock = multiprocessing.Lock()
    try:
        while index < len(iTup[6]):
            if token.consume(1):
                ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
                ftpModule.uploadFile(ftp, iTup[6][index])
                #timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
                with uploadCount.get_lock():
                #with lock:
                    uploadCount.value += 1
                    #uploadCount += 1
                    print( "No. %d/%d pid:%s--file: %s has been uploaded." % (uploadCount.value, total_count, os.getpid(), iTup[6][index]))
                index = index + 1
                #print( "current_upload_image_count is: ", uploadCount)
                ftp.quit()
    except Exception, e:
        print( e)
        raise MYEXCEPTION.MyException(e)
    countDic = {}
    nameStr = "pid:" + str(os.getpid)
    countDic[nameStr] = uploadCount
    return countDic


#
def run():
    parameterList = sys.argv[1]
    numOfPiece = parameterList

    originalFilePathList = getImagesPathList(r"/data/ftp/cut_images")

    superFilePathList = chunks(originalFilePathList, numOfPiece)

    imagesCount = 0
    for i in superFilePathList:
        imagesCount = imagesCount + len(i)

    pool = multiprocessing.Pool(processes=int(numOfPiece))
    #lock = multiprocessing.Lock()
    paraList = []
    for i in superFilePathList:
        iTup = ("192.168.2.17", "8001", "1234567890", "admin", "admin", True, i)
        paraList.append(iTup)

    startTime = time.time()
    resultList = []
    #resultList = multiprocessing.Manager().Queue()
    try:
        for i in paraList:
            resultList.append(pool.apply_async(bucketUploadFileByFtp, args=(i,)))
            #resultList.put(pool.apply_async(bucketUploadFileByFtp, args=(i,)))
    except Exception, e:
        print e
    finally:
        pool.close()
        pool.join()
        endTime = time.time()
        print ("end")
        print ("starttime: ",startTime)
        print ("endtime: ",endTime)
        print ("cost_time: ",endTime-startTime)
    #resInfo = []

    #for i in resultList:
    #while not resultList.empty():
    #    print (i.get())
    #print( "len ",len(resultList))
    #print "i_type: %s,i_dir: %s" % (type(i),dir(i))
        #info = i.get()
        #resInfo.append(info)
        #print "resultList_member_length: ", len(info)
    #for j in resInfo:
    #    print j



if __name__ == '__main__':
    '''
    :param 脚本本身
    :param 进程数
    '''
    run()
