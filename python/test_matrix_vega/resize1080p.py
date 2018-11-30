import cv2
import numpy as np
import re
import sys

def imageResize1980x1080(imgList):

    mat=np.zeros((1080,1920,3),np.uint8)    #MAT((1920,1080),CV_8U3)

    pshape=mat.shape
    print(pshape)

    fobj = open(imgList)
    allImgs = fobj.readlines()
    fobj.close()

    for img in allImgs:
        img = img.strip("\n")
        subimage=cv2.imread(img)
        sshape=subimage.shape
        print(sshape)
        start_row=int((pshape[0]-sshape[0])/2)
        start_col=int((pshape[1]-sshape[1])/2)

        # mat[:,:,:]=200
        name = re.search("(\d+).jpg", img, re.DOTALL).group(1)
        try:

            mat[start_row:start_row+sshape[0],start_col:start_col+sshape[1],     :]=subimage
            cv2.imwrite(r'face_1_resized/%s.jpg' % name,mat)
        except:
            pass


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.exit(-1)
    image_list = sys.argv[1]
    imageResize1980x1080(image_list)
