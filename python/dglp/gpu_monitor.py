import pynvml as nv
import time
import os
import sys
import psutil

nv.nvmlInit()
#print "Driver Version:", nv.nvmlSystemGetDriverVersion()
#deviceCount = nv.nvmlDeviceGetCount()
while(1):
    try:
        pid_obj = os.popen('pgrep -f dgLP_test')
        pid = int(pid_obj.read().split()[0])
        pid_list = psutil.pids()
        if pid in pid_list:
            handle = nv.nvmlDeviceGetHandleByIndex(1)
            #print "Device", 0, ":", nv.nvmlDeviceGetName(handle)
            print "GPU-util", nv.nvmlDeviceGetUtilizationRates(handle)
            time.sleep(0.5)
    except IndexError,e:
        nv.nvmlShutdown()
        print "process dgLP_test terminal!"
        sys.exit()
