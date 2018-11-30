import shutil
import os

img_list = os.listdir("test_set2")
x = 0
for img in img_list:
	shutil.copy("/data/cuixing/data_ssd_VS_fcn/test_set2/" + img, "test_set2_1w")
	x += 1
	print x
	if x >= 10000:
		break
