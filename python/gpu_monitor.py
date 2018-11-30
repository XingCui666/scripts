import pynvml as nv
import time
nv.nvmlInit()
print "Driver Version:", nv.nvmlSystemGetDriverVersion()
deviceCount = nv.nvmlDeviceGetCount()
while(1):
    for i in range(deviceCount):
        handle = nv.nvmlDeviceGetHandleByIndex(i)
        print "Device", i, ":", nv.nvmlDeviceGetName(handle)
        print "GPU-util", nv.nvmlDeviceGetUtilizationRates(handle)
    time.sleep(0.1)
nv.nvmlShutdown()





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
        pid_obj = os.popen('pgrep -f test_plate')
        pid = int(pid_obj.read().split()[0])
        pid_list = psutil.pids()
        if pid in pid_list:
            handle = nv.nvmlDeviceGetHandleByIndex(0)
            #print "Device", 0, ":", nv.nvmlDeviceGetName(handle)
            print "GPU-util", nv.nvmlDeviceGetUtilizationRates(handle)
            time.sleep(0.5)
    except IndexError,e:
        nv.nvmlShutdown()
        print "process test_plate terminal!"
        sys.exit()

