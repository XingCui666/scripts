#!/usr/bin/python
#coding:utf-8
#author:chunxiusun

import os
import json
import requests
import getopt
import re
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
#print sys.getdefaultencoding()

conf = dict(
        matrixIp = "192.168.2.122",
        matrixPort = "6601",
        mode = 1, #0 means single,1 means batch
        batchNum = 8,
        uriType = 2, #0 means local,1 means http,2 means url file
        imageFile = "yellow_lable.txt",
        uriHeader = 'http://192.168.2.217:8004/',
        photoPath = '/home/dell/data/pic/no_faild/',
        outputFile = "car_result.txt"
        
)

SESSION_ID = 0

stat = dict(
     imageCount = 0,
     httpCount = 0,
     httpErrorCount = 0,
     vehicleCount = 0,
     pedestrianCount = 0,
     nonMotorvehicleCount = 0
)

class AnalyzeMatrix():
    def __init__(self,fd):
        self.fd = fd
    def dealImgPath(self,root_path,img_file):
        img_list = []
        if conf["uriType"] == 0 or conf["uriType"] == 1:
            for sub_dir_name in os.listdir(root_path):
                temp_path = "%s/%s" %(root_path, sub_dir_name)
                if re.search("^\.", sub_dir_name) != None:
                    continue
                if os.path.isfile(temp_path):
                    if re.search("\.jpg", temp_path) == None:
                        continue                                                                                                               
                    img_list.append(temp_path)                                                                                            
                elif os.path.isdir(temp_path):                                                                                                 
                    dealImgPath(temp_path)
        if conf["uriType"] == 2:
            fd = open(img_file,'r')
            for line in fd.readlines():
                img_list.append(line.strip())                                                                                                
        return img_list

    def postRequest(self,img_list):
        global SESSION_ID
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        source = {"Context": {"SessionId": str(SESSION_ID),                                                                                      
                              "Functions": [100,101,102,103,104,105,106,107,108,300,301,400],        
                              "Type":1                                                                                                   
                             }                                                                                                            
                  }
        if conf["mode"] == 0:
            url = "http://%s:%s/rec/image"%(conf["matrixIp"],conf["matrixPort"])
            source["Image"] = img_list
        if conf["mode"] == 1:
            url = "http://%s:%s/rec/image/batch"%(conf["matrixIp"],conf["matrixPort"])
            source["Images"] = img_list
        SESSION_ID += 1
        jsource = json.dumps(source)
        #print jsource                                                                                                       
        resp = requests.post(url,data = jsource,headers=headers)                                                                                         
        status_code = resp.status_code                                                                                                     
        if status_code != 200:                                                                                                             
            rdict = {}                                                                                                                     
        else:                                                                                                                              
            rdict = json.loads(resp.content)#,encoding="UTF-8)                                                                              
        #print status_code                                                                                                                 
        return status_code,rdict

    def singleReq(self,img_list):
        for img in img_list:
            print img
            stat["imageCount"] += 1
            #img = "http://192.168.2.16:3002/Brand_Data/dayfront/SrcData2/changzhou/02//08/519020400601-20150102081019-8-1.jpg"
            query_dict = {}
            if conf["uriType"] == 0:
                query_dict = {'URI': 'file:///' + img}
            if conf["uriType"] == 1:
                query_dict = {'URI': conf["uriHeader"] + img.split('/')[-1]}
            if conf["uriType"] == 2:
                query_dict = {'URI': img}
            post_img = {"Data": query_dict}
            status_code,rdict = self.postRequest(post_img)
            stat["httpCount"] += 1
            if status_code != 200:
                stat["httpErrorCount"] += 1
                continue
            if "Result" not in rdict:
                print "No Result:%s"%str(post_img)
                continue
            result = rdict["Result"]
            im = result["Image"]["Data"]["URI"].split("/")[-1]
            self.analyzeVehicle(result,im)
            self.analyzePedestrian(result,im)
            self.analyzeNonMotorvehicle(result,im)
            #break
    
    def batchReq(self,img_list):
        post_img = []
        for i,img in enumerate(img_list):
            print img
            stat["imageCount"] += 1
            #img = "ftp://192.168.2.16/matrix_cases/person/791.jpg"
            query_dict = {}
            if conf["uriType"] == 0:
                query_dict = {'URI': 'file:///' + img}
            if conf["uriType"] == 1:
                query_dict = {'URI': conf["uriHeader"] + img.split("/")[-1]}
            if conf["uriType"] == 2:
                query_dict = {'URI': img}
            post_img.append({"Data": query_dict})
            if len(post_img) == conf["batchNum"] or (len(post_img) != 1 and i == len(img_list)-1):
                status_code,rdict = self.postRequest(post_img)
                stat["httpCount"] += 1
                if status_code != 200:
                    stat["httpErrorCount"] += 1
                    continue
                if "Results" not in rdict:
                    print "No Result:%s"%str(post_img)
                    continue
                for result in rdict["Results"]:
                    im = result["Image"]["Data"]["URI"].split("/")[-1]
                    self.analyzeVehicle(result,im)
                    self.analyzePedestrian(result,im)
                    self.analyzeNonMotorvehicle(result,im)
                post_img = []
            #break

    def analyzeVehicle(self,datadict,im):
        if "Vehicles" not in datadict:
            #self.fd.write("%s;Vehicle;\n"%im)
            return
        for vehicle in datadict["Vehicles"]:
            stat["vehicleCount"] += 1
            vehicle_dict = {}
            cartype = vehicle["ModelType"]["Style"]
            vehicle_dict["cartype"] = cartype
            brand = vehicle["ModelType"]["Brand"]
            vehicle_dict["brand"] = brand
            subrand = vehicle["ModelType"]["SubBrand"]
            vehicle_dict["subrand"] = subrand
            modelyear = vehicle["ModelType"]["ModelYear"]
            vehicle_dict["modelyear"] = modelyear
            pose = vehicle["ModelType"]["Pose"]
            vehicle_dict["pose"] = pose
            color = vehicle["Color"]["ColorName"]
            vehicle_dict["color"] = color
            cutboard = []
            for item in ["X","Y","Width","Height"]:
                cutboard_item = vehicle["Img"]["Cutboard"][item]
                cutboard.append(cutboard_item)
            vehicle_dict["cutboard"] = cutboard
            plates = ""
            if "Plates" in vehicle:
                for plate in vehicle["Plates"]:
                    plate_text = plate["PlateText"]
                    plate_color = plate["Color"]["ColorName"]
                    plates = plates + ":" + "%s&%s"%(plate_text,plate_color)
            vehicle_dict["plates"] = plates
            if "Symbols" in vehicle:
                symbols = vehicle["Symbols"]
                lst = ["label","tableware","pendant","tissue_box","left_sun_visor","right_sun_visor"]
                #for item in lst:
                    #vehicle_dict["%s_num"%item] = 0
                for symbol in symbols:
                    for i,item in enumerate(lst):
                        if symbol["SymbolId"] == i+1:
                            if "%s_num"%item not in vehicle_dict:
                                vehicle_dict["%s_num"%item] = 0
                            vehicle_dict["%s_num"%item] += 1

            if "Passengers" in vehicle:
                passengers = vehicle["Passengers"]
                for passenger in passengers:
                    if passenger["Driver"] == True:
                        vehicle_dict["driver_belt"] = passenger["BeltFlag"]
                        vehicle_dict["driver_phone"] = passenger["PhoneFlag"]
                    else:
                        vehicle_dict["codriver_belt"] = passenger["BeltFlag"]
                        vehicle_dict["codriver_phone"] = passenger["PhoneFlag"]
            self.fd.write("%s;Vehicle;"%im)
            v_lst = ["cutboard","brand","subrand","modelyear","cartype","pose","color","plates",
                   "label_num","tableware_num","pendant_num","tissue_box_num","left_sun_visor_num","right_sun_visor_num",
                   "driver_belt","driver_phone","codriver_belt","codriver_phone"]
            data_dict = {}
            for item in v_lst:                                                                                                  
                if item in vehicle_dict:                                                                                                      
                    data_dict[item] = vehicle_dict[item]                                                                                      
                #elif "num" in item:                                                                                                        
                    #data_dict[item] = 0
                else:
                    data_dict[item] = ""
            for key in v_lst:
                self.fd.write("%s;"%data_dict[key])   
            self.fd.write("\n")

    def analyzePedestrian(self,datadict,im):
        if "Pedestrian" not in datadict:
            #self.fd.write("%s;Pedestrian;\n"%im)
            return
        for pedestrian in datadict["Pedestrian"]:
            stat["pedestrianCount"] += 1                                                                                                  
            pedestrian_dict = {}                                                                                                               
            #Cutboard                                                                                                                          
            cutboard = []                                                                                                                      
            for item in ["X","Y","Width","Height"]:                                                                                                
                cutboard_item = pedestrian["Img"]["Cutboard"][item]                                                                                  
                cutboard.append(cutboard_item)                                                                                                 
            pedestrian_dict["cutboard"] = cutboard                                                                                             
            #Sex
            if "Sex" in pedestrian["PedesAttr"]:                                                                                                  
                sex = pedestrian["PedesAttr"]["Sex"]["Name"]                                                                                         
                pedestrian_dict["sex"] = sex                                                                                                       
            #Age
            if "Age" in pedestrian["PedesAttr"]:                                                                                                      
                age = pedestrian["PedesAttr"]["Age"]["Name"]                                                                                         
                pedestrian_dict["age"] = age                                                                                                       
            #National
            if "National" in pedestrian["PedesAttr"]:                                                                                  
                nation = pedestrian["PedesAttr"]["National"]["Name"]                                                                                 
                pedestrian_dict["nation"] = nation                                                                                                 
            #Category
            if "Category" in pedestrian["PedesAttr"]:                                                                                           
                for category in pedestrian["PedesAttr"]["Category"]:
                    category_id = category["Id"]
                    category_name = ""
                    for item in category["Items"]:
                        category_name = category_name + ":" + item["Name"]
                    c_lst = ["headwear","upper_color","upper_texture","lower_color","lower_type","bag"]
                    lst = [2,54,9,56,10,52]
                    for i,item in enumerate(lst):
                        if category_id == lst[i]:
                            pedestrian_dict[c_lst[i]] = category_name                                                                                 
            self.fd.write("%s;Pedestrian;"%im)
            p_list = ["cutboard","sex","age","nation","headwear","upper_color","upper_texture",                     
                       "lower_color","lower_type","bag"]
            for key in p_list:
                if key not in pedestrian_dict:
                    pedestrian_dict[key] = ""
                self.fd.write("%s;"%pedestrian_dict[key])                                                                                     
            self.fd.write("\n")

    def analyzeNonMotorvehicle(self,datadict,im):
        if "NonMotorVehicles" not in datadict:
            #self.fd.write("%s;NonMotorVehicle;\n"%im)
            return
        for nonmotorvehicle in datadict["NonMotorVehicles"]:
            stat["nonMotorvehicleCount"] += 1
            nonMotorvehicle_dict = {}
            #Cutboard
            cutboard = []
            for item in ["X","Y","Width","Height"]:
                cutboard_item = nonmotorvehicle["Img"]["Cutboard"][item]
                cutboard.append(cutboard_item)
            nonMotorvehicle_dict["cutboard"] = cutboard
            #Attributes
            if "Attributes" in nonmotorvehicle:
                for attribute in nonmotorvehicle["Attributes"]:
                    attribute_id = attribute["AttributeId"]
                    a_lst = ["nMVehicle_gesture","nMVehicle_type","nMVehicle_color"]
                    lst = [1,4,8]
                    for i,item in enumerate(lst):
                        if attribute_id == item:
                            nonMotorvehicle_dict[a_lst[i]] = attribute["ValueString"]
            if "Passengers" in nonmotorvehicle:
                for passenger in nonmotorvehicle["Passengers"]:
                    if passenger["Driver"] != True:
                        continue
                    if "Attributes" in passenger:
                        for attribute in passenger["Attributes"]:
                            attribute_id = attribute["AttributeId"]
                            a_lst = ["gender","nation","headwear","upper_color","upper_color_style","pack_style"]
                            lst = [16,19,3,5,6,2]
                            for i,item in enumerate(lst):
                                if attribute_id == item:
                                    nonMotorvehicle_dict[a_lst[i]] = attribute["ValueString"]
            self.fd.write("%s;NonMotorVehicle;"%im)
            n_lst = ["cutboard","nMVehicle_type","nMVehicle_gesture","nMVehicle_color","gender","nation",                    
                   "headwear","upper_color","upper_color_style","pack_style"]
            for key in n_lst:
                if key not in nonMotorvehicle_dict:
                    nonMotorvehicle_dict[key] = ""
                self.fd.write("%s;"%nonMotorvehicle_dict[key])
            self.fd.write("\n")

    def run(self):
        img_list = self.dealImgPath(conf["photoPath"],conf["imageFile"])
        if conf["mode"] == 0:
            self.singleReq(img_list)
        elif conf["mode"] == 1:
            self.batchReq(img_list)
        print "vehicleCount:%d"%stat["vehicleCount"]
        print "pedestrianCount:%d"%stat["pedestrianCount"]
        print "nonMotorvehicleCount:%d"%stat["nonMotorvehicleCount"]

def usage():
    print "Usage: \n",\
          "-h,--help (show help on all flags [tip: all flags can have two dashes])\n",\
          "--ip (matrix ip,defult:127.0.0.1)\n",\
          "--port (matrix port,defult:6505)\n",\
          "--mode (0 means single,1 means batch,defult:0)\n",\
          "--batchsize (batchsize,defult:8)\n",\
          "--imagefile (images url list file)\n",\
          "--outputfile (result file,defult:car_result.txt)\n",\
          "--info (Output file field meaning)"

def info():
    print "机动车:cutboard;主品牌;子品牌;年款;车型;车姿态;车身颜色;车牌号&车牌颜色;年检标数量;摆件数量;挂坠数量;纸巾盒数量;左遮阳板数量;右遮阳板数量;主驾安全带;主驾打电话;副驾安全带;副驾打电话\n",\
          "行人:cutboard;性别;年龄;民族;头部特征;上身颜色;上身纹理;下身颜色;下身类别;包款式\n",\
          "非机动车:cutboard;车辆类型;车辆角度;车身颜色;人员性别;人员民族;人员头部特征;人员上身颜色;人员上身样式;包款式\n"

def getOptions():
    try:
        options,args = getopt.getopt(sys.argv[1:],"h",["help","info","ip=","port=","mode=","batchsize=","imagefile=","outputfile="])
    except getopt.GetoptError:
        sys.exit()
    for name,value in options:
        if name in ("-h","--help"):
            usage()
            sys.exit()
        if name in ("--info"):
            info()
            sys.exit()
        if name in ("--ip"):
            conf["matrixIp"] = value
        if name in ("--port"):
            conf["matrixPort"] = value
        if name in ("--mode"):
            conf["mode"] = eval(value)
        if name in ("--batchsize"):
            conf["batchNum"] = eval(value)
        if name in ("--imagefile"):
            conf["imageFile"] = value
        if name in ("--outputfile"):
            conf["outputFile"] = value


if __name__ == '__main__':
    getOptions()
    fd = open(conf["outputFile"],'w')
    p = AnalyzeMatrix(fd)
    p.run()
    fd.close()
