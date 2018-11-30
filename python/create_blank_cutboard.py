import os
import sys

def list_all_files(rootdir):  
    import os  
    _files = []  
    list = os.listdir(rootdir)
    for i in range(0,len(list)):  
           path = os.path.join(rootdir,list[i])  
           if os.path.isdir(path):  
              _files.extend(list_all_files(path))  
           if os.path.isfile(path):  
              _files.append(path)  
    return _files  

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Usage: \rpython walk.py [groudth directory] [true directory]"
        sys.exit(1)

    groudpath = sys.argv[1] # "/home/zhouping/scripts/ranker2/tocx/groudth"
    truepath = sys.argv[2] # "/home/zhouping/scripts/ranker2/tocx/truth"
    files = list_all_files(groudpath)
    for cfile in files:

        basename = os.path.basename(cfile)
        truedir = os.path.join(truepath, basename)
        if os.path.exists(truedir):
            pass
        else:
            print '{} is not exit, create it'.format(truedir)
            open(truedir,"w+").close()
