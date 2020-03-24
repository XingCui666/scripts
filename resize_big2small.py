import cv2
import sys
import os

def resize(size_tuple):
	with open(imglist) as f:
		imglst = f.readlines()
	for img in imglst:
		name = os.path.basename(img.strip('\n'))
		img = cv2.imread(img.strip('\n'))
		img_resize = cv2.resize(img, size_tuple, interpolation=cv2.INTER_AREA)
		cv2.imwrite(save_path + '/' + name, img_resize)

#cv2.imshow('Skewedsize', img_scaled)
#cv2.waitKey()
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("case imglist save_path")
		sys.exit(-1)
	imglist = sys.argv[1]
	save_path = sys.argv[2]
	size_tuple = (1280, 720)
	resize(size_tuple)
