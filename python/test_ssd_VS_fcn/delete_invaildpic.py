#!/usr/bin python
#!coding=utf-8

with open("model2.txt") as f:
	lines = f.readlines()

with open("nonepic.txt") as f_none:
	lines_none = f_none.readlines()

with open("model2.txt.new", 'w') as f_w:
	for line in lines:
		tmp = line.strip('\n').split()[0]
		if (tmp+".jpg\n") in lines_none:
			print tmp
			continue
		f_w.write(line)

