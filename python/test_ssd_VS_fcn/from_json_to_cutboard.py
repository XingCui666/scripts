#!/usr/env python
#!coding=utf-8

import json
import string
import os
import sys
import re

def json_to_txt():
	length = len(all_anno)
	print "all_anno_len: ", length

	for i in range(length):
		anno = all_anno[i]
		anno = json.loads(anno)
		anno_name_path = anno["url_image"]
		#anno_name = os.path.basename(anno_name_path)
		anno_name = re.search("(\d+).jpg", anno_name_path).group(1)

		if anno["result"] == []:
			open(save_path + anno_name + ".txt", 'w').close()
			continue

		with open(save_path + anno_name + ".txt", 'a') as f:
			for v in anno["result"]:
				cutboard = str(v["data"]).strip("[ ]").replace(",","")
				f.write("{}{}".format(cutboard, os.linesep))
		#print "saved anno_txt: ", anno_name		

if __name__ == "__main__":
	if(len(sys.argv) < 2):
		print "start by [python] [jsonlist]"
		sys.exit(-1)
	json_file = sys.argv[1]
	with open(json_file) as f:
		all_anno = f.readlines()
	save_path = "Anno_txt/"
	json_to_txt()
