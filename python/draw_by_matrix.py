#!/usr/bin/env python
#!coding=utf-8

import cv2
from collections import defaultdict
import json
import urllib
import requests
import time
import sys
import os

font = cv2.FONT_HERSHEY_SIMPLEX

# usage
def help():

    '''
    Uage:
      python roi.py [MatrixUrl] [ImageUrl] [Type]
        MatrixUrl: eg. http://192.168.2.16:6501/rec/image
        ImageUrl: eg. http://192.168.2.17/dgtestdata/AlgorithmData/dgvehicle/big_pictures/facecover/12_facecover.jpg
        Type: 1 mean vehicle, 2 mean face, 3 mean all objects
    
    Eg:
      python roi.py http://192.168.2.16:6501/rec/image http://192.168.2.17/dgtestdata/AlgorithmData/dgvehicle/big_pictures/facecover/12_facecover.jpg 3
    '''
    pass


# post request
def post_request(url, source):
    jsource = json.dumps(source)
    #print json.dumps(jsource, indent=1)

    resp = requests.post(url, data = jsource)
    if resp.content == "":
        return None,resp.status_code
    else:
        rdict = json.loads(resp.content)
        return rdict,resp.status_code

# matrix query
class Matrix:
    def __init__(self, url):
        self.url = url

    def query(self, source):
        resp_dict, _ret = post_request(self.url, source)
        #print 'resp: ', json.dumps(resp_dict, indent=1)
        return resp_dict

# Get featureStr from Matrix
def getFeatreFrommatrix(mxUrl=None, imageUrl=None, type_=None):

    matrix_url = mxUrl
    matrixSession = Matrix(matrix_url)
    if type_ == 1:

        post_source = {"Context":{"SessionId":"matrix test","Type":1,"Functions":[100,101,102,103,104,105,106,107,108,109,110,111,112,300,301,400,401,402]},"Image":{"Data":{"URI":imageUrl}}}    
    elif type_ == 2:

        post_source = {"Context":{"SessionId":"matrix test","Type":2,"Functions":[200,201,202,203,204,205]},"Image":{"Data":{"URI":imageUrl}}}
    else:

        post_source = {"Context":{"SessionId":"matrix test","Type":3,"Functions":[100,101,102,103,104,105,106,107,108,109,200,201,202,203,204,205,110,111,112,300,301,400,401,402]},"Image":{"Data":{"URI":imageUrl}}}

    result = matrixSession.query(post_source)
    return result

# json to dict
def json_to_dict(response):

    res = json.loads(s=response)
    return res

# open the image
def cvopen(imageUrl):

    im = cv2.imread(imageUrl)
    im_copy = im.copy()
    return  im_copy

# draw cutboard
def drawCutboard(im_copy, cutboard, color='r'):

    imgInfo = cutboard
    #print 'imgInfo:', imgInfo
    roi = imgInfo

    x = roi[0]
    y = roi[1]
    x1 = roi[0] + roi[2]
    y1 = roi[1] + roi[3]
    if color == 'r':
        cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(0,0,255),3) # color: B-G-R
    elif color == 'b':
        cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(255,0,0),3) # color: B-G-R
    elif color == 'g':
        cv2.rectangle(im_copy,(int(x),int(y)),(int(x1),int(y1)),(0,255,0),3) # color: B-G-R

    return im_copy

    #cv2.imwrite("drawcar.png", im_copy)

# get cutboard
def getCurboard(mxUrl, imageUrl, type_=1):

    # get response from matrix
    res = getFeatreFrommatrix(mxUrl, imageUrl, type_)
 
    # get the image copy
    urllib.urlretrieve(imageUrl.strip(), "123.jpg") 
    time.sleep(2)
    im_copy = cvopen("123.jpg")
    #print 'im_copy:', im_copy

    # vehicle
    if type_ == 1:

        if res.has_key("Result"):
            if res["Result"].has_key("Vehicles"):
                vehicles = res["Result"]["Vehicles"]
                vehicleNum = len(vehicles)
                vehicle = defaultdict(list)
                for i in range(vehicleNum):

                    #vehicle[i] ={'cutboard':[],'plate':{'cutboard':[],'platetext':''}}

                    vx = vehicles[i]["Img"]["Cutboard"]["X"]
                    vy = vehicles[i]["Img"]["Cutboard"]["Y"]
                    vw = vehicles[i]["Img"]["Cutboard"]["Width"]
                    vh = vehicles[i]["Img"]["Cutboard"]["Height"]

                    cutboard = map(int, [vx,vy,vw,vh])

                    im_copy = drawCutboard(im_copy, cutboard, 'r')

                    #vehicle[i]['cutboard'] = [vx, vy, vw, vh]
                    if vehicles[i].has_key("Plates"):
                        plates = vehicles[i]["Plates"]
                        plateNum = len(plates)
                        for j in range(plateNum):
                            px = plates[j]["Cutboard"]["X"]
                            py = plates[j]["Cutboard"]["Y"]
                            pw = plates[j]["Cutboard"]["Width"]
                            ph = plates[j]["Cutboard"]["Height"]
                    
                            ptext = plates[j]["PlateText"]
     
                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]

                            #im_copy = cv2.putText(im_copy, '123', (int(vx)+int(px), int(vy)+int(py)), font, 1.2, (255, 255, 255), 2)

                            im_copy = drawCutboard(im_copy, cutboard, 'r')

                    if vehicles[i].has_key("Passengers"): 
                        passengers = vehicles[i]["Passengers"]
                        passengerNum = len(passengers)
                        for j in range(passengerNum):
                            px = passengers[j]["Img"]["Cutboard"]["X"]
                            py = passengers[j]["Img"]["Cutboard"]["Y"]
                            pw = passengers[j]["Img"]["Cutboard"]["Width"]
                            ph = passengers[j]["Img"]["Cutboard"]["Height"]

                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]
                            im_copy = drawCutboard(im_copy, cutboard, 'b')

            if res["Result"].has_key("Pedestrian"):
                pedestrians = res["Result"]["Pedestrian"]
                pedestrianNum = len(pedestrians)
                pedestrian = defaultdict(list)
                for i in range(pedestrianNum):

                    #vehicle[i] ={'cutboard':[],'plate':{'cutboard':[],'platetext':''}}

                    vx = pedestrians[i]["Img"]["Cutboard"]["X"]
                    vy = pedestrians[i]["Img"]["Cutboard"]["Y"]
                    vw = pedestrians[i]["Img"]["Cutboard"]["Width"]
                    vh = pedestrians[i]["Img"]["Cutboard"]["Height"]

                    cutboard = map(int, [vx,vy,vw,vh])

                    im_copy = drawCutboard(im_copy, cutboard, 'b')

            if res["Result"].has_key("NonMotorVehicles"):
                nonvehicles = res["Result"]["NonMotorVehicles"]
                vehicleNum = len(nonvehicles)
                vehicle = defaultdict(list)
                for i in range(vehicleNum):

                    #vehicle[i] ={'cutboard':[],'plate':{'cutboard':[],'platetext':''}}

                    vx = nonvehicles[i]["Img"]["Cutboard"]["X"]
                    vy = nonvehicles[i]["Img"]["Cutboard"]["Y"]
                    vw = nonvehicles[i]["Img"]["Cutboard"]["Width"]
                    vh = nonvehicles[i]["Img"]["Cutboard"]["Height"]

                    cutboard = map(int, [vx,vy,vw,vh])

                    im_copy = drawCutboard(im_copy, cutboard, 'g')

                    #vehicle[i]['cutboard'] = [vx, vy, vw, vh]
                    if nonvehicles[i].has_key("Plates"):
                        plates = nonvehicles[i]["Plates"]
                        plateNum = len(plates)
                        for j in range(plateNum):
                            px = plates[j]["Cutboard"]["X"]
                            py = plates[j]["Cutboard"]["Y"]
                            pw = plates[j]["Cutboard"]["Width"]
                            ph = plates[j]["Cutboard"]["Height"]
                    
                            ptext = plates[j]["PlateText"]
     
                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]

                            #im_copy = cv2.putText(im_copy, '123', (int(vx)+int(px), int(vy)+int(py)), font, 1.2, (255, 255, 255), 2)

                            im_copy = drawCutboard(im_copy, cutboard, 'g')

                    if nonvehicles[i].has_key("Passengers"): 
                        passengers = nonvehicles[i]["Passengers"]
                        passengerNum = len(passengers)
                        for j in range(passengerNum):
                            px = passengers[j]["Img"]["Cutboard"]["X"]
                            py = passengers[j]["Img"]["Cutboard"]["Y"]
                            pw = passengers[j]["Img"]["Cutboard"]["Width"]
                            ph = passengers[j]["Img"]["Cutboard"]["Height"]

                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]
                            im_copy = drawCutboard(im_copy, cutboard, 'b')

    # face
    elif type_ == 2:
        print json.dumps(res, indent=1)
        if res.has_key("Result"):
            if res["Result"].has_key("Faces"):
                faces = res["Result"]["Faces"]
                faceNum = len(faces)
                face = defaultdict(list)
                for i in range(faceNum):

                    vx = faces[i]["Img"]["Cutboard"]["X"]
                    vy = faces[i]["Img"]["Cutboard"]["Y"]
                    vw = faces[i]["Img"]["Cutboard"]["Width"]
                    vh = faces[i]["Img"]["Cutboard"]["Height"]

                    cutboard = map(int, [vx,vy,vw,vh])

                    im_copy = drawCutboard(im_copy, cutboard, 'g')

    # face and vehicle (all object)
    else:
        if res.has_key("Result"):
            if res["Result"].has_key("Vehicles"):
                vehicles = res["Result"]["Vehicles"]
                vehicleNum = len(vehicles)
                vehicle = defaultdict(list)
                for i in range(vehicleNum):

                    #vehicle[i] ={'cutboard':[],'plate':{'cutboard':[],'platetext':''}}

                    vx = vehicles[i]["Img"]["Cutboard"]["X"]
                    vy = vehicles[i]["Img"]["Cutboard"]["Y"]
                    vw = vehicles[i]["Img"]["Cutboard"]["Width"]
                    vh = vehicles[i]["Img"]["Cutboard"]["Height"]

                    cutboard = map(int, [vx,vy,vw,vh])

                    im_copy = drawCutboard(im_copy, cutboard, 'r')

                    #vehicle[i]['cutboard'] = [vx, vy, vw, vh]
                    if vehicles[i].has_key("Plates"):
                        plates = vehicles[i]["Plates"]
                        plateNum = len(plates)
                        for j in range(plateNum):
                            px = plates[j]["Cutboard"]["X"]
                            py = plates[j]["Cutboard"]["Y"]
                            pw = plates[j]["Cutboard"]["Width"]
                            ph = plates[j]["Cutboard"]["Height"]
                    
                            ptext = plates[j]["PlateText"]
     
                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]

                            #im_copy = cv2.putText(im_copy, '123', (int(vx)+int(px), int(vy)+int(py)), font, 1.2, (255, 255, 255), 2)

                            im_copy = drawCutboard(im_copy, cutboard, 'r')

                    if vehicles[i].has_key("Passengers"): 
                        passengers = vehicles[i]["Passengers"]
                        passengerNum = len(passengers)
                        for j in range(passengerNum):
                            px = passengers[j]["Img"]["Cutboard"]["X"]
                            py = passengers[j]["Img"]["Cutboard"]["Y"]
                            pw = passengers[j]["Img"]["Cutboard"]["Width"]
                            ph = passengers[j]["Img"]["Cutboard"]["Height"]

                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]
                            im_copy = drawCutboard(im_copy, cutboard, 'b')

                            if passengers[j].has_key("Face"):
                                faces = passengers[j]["Face"]
                                fx = faces["Img"]["Cutboard"]["X"]
                                fy = faces["Img"]["Cutboard"]["Y"]
                                fw = faces["Img"]["Cutboard"]["Width"]
                                fh = faces["Img"]["Cutboard"]["Height"]

                                cutboard = [int(vx)+int(fx), int(vy)+int(fy), int(fw), int(fh)]
                                im_copy = drawCutboard(im_copy, cutboard, 'b')

            if res["Result"].has_key("Pedestrian"):
                pedestrians = res["Result"]["Pedestrian"]
                pedestrianNum = len(pedestrians)
                pedestrian = defaultdict(list)
                for i in range(pedestrianNum):

                    #vehicle[i] ={'cutboard':[],'plate':{'cutboard':[],'platetext':''}}

                    vx = pedestrians[i]["Img"]["Cutboard"]["X"]
                    vy = pedestrians[i]["Img"]["Cutboard"]["Y"]
                    vw = pedestrians[i]["Img"]["Cutboard"]["Width"]
                    vh = pedestrians[i]["Img"]["Cutboard"]["Height"]

                    cutboard = map(int, [vx,vy,vw,vh])

                    im_copy = drawCutboard(im_copy, cutboard, 'b')

            if res["Result"].has_key("NonMotorVehicles"):
                nonvehicles = res["Result"]["NonMotorVehicles"]
                vehicleNum = len(nonvehicles)
                vehicle = defaultdict(list)
                for i in range(vehicleNum):

                    #vehicle[i] ={'cutboard':[],'plate':{'cutboard':[],'platetext':''}}

                    vx = nonvehicles[i]["Img"]["Cutboard"]["X"]
                    vy = nonvehicles[i]["Img"]["Cutboard"]["Y"]
                    vw = nonvehicles[i]["Img"]["Cutboard"]["Width"]
                    vh = nonvehicles[i]["Img"]["Cutboard"]["Height"]

                    cutboard = map(int, [vx,vy,vw,vh])

                    im_copy = drawCutboard(im_copy, cutboard, 'g')

                    #vehicle[i]['cutboard'] = [vx, vy, vw, vh]
                    if nonvehicles[i].has_key("Plates"):
                        plates = nonvehicles[i]["Plates"]
                        plateNum = len(plates)
                        for j in range(plateNum):
                            px = plates[j]["Cutboard"]["X"]
                            py = plates[j]["Cutboard"]["Y"]
                            pw = plates[j]["Cutboard"]["Width"]
                            ph = plates[j]["Cutboard"]["Height"]
                    
                            ptext = plates[j]["PlateText"]
     
                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]

                            #im_copy = cv2.putText(im_copy, '123', (int(vx)+int(px), int(vy)+int(py)), font, 1.2, (255, 255, 255), 2)

                            im_copy = drawCutboard(im_copy, cutboard, 'g')

                    if nonvehicles[i].has_key("Passengers"): 
                        passengers = nonvehicles[i]["Passengers"]
                        passengerNum = len(passengers)
                        for j in range(passengerNum):
                            px = passengers[j]["Img"]["Cutboard"]["X"]
                            py = passengers[j]["Img"]["Cutboard"]["Y"]
                            pw = passengers[j]["Img"]["Cutboard"]["Width"]
                            ph = passengers[j]["Img"]["Cutboard"]["Height"]

                            #vehicle[i]['cutboard']['plate']['cutboard'].append(px,py,pw,ph)


                            cutboard = [int(vx)+int(px), int(vy)+int(py), int(pw), int(ph)]
                            im_copy = drawCutboard(im_copy, cutboard, 'g')
    # save the image
    #cv2.namedWindow("draw", cv2.WINDOW_NORMAL)
    #cv2.imshow("draw", im_copy) 
    cv2.imwrite("draw.png", im_copy)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()

    # delete the temp image
    os.system('rm 123.jpg')

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print(help.__doc__)
        sys.exit(1)

    mxUrl = sys.argv[1] # "http://192.168.2.16:6501/rec/image"
    imageUrl = sys.argv[2] # "http://192.168.2.17/dgtestdata/AlgorithmData/dglp/abnormal/1.jpg"
    type_ = int(sys.argv[3])
    getCurboard(mxUrl, imageUrl, type_)
