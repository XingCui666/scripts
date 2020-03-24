import pynvml as nv
import time
import os
import sys
#import psutil

gpu_id = 0
query_interval = 0.5
nv.nvmlInit()
handle = nv.nvmlDeviceGetHandleByIndex(gpu_id)
print "Driver Version: " , nv.nvmlSystemGetDriverVersion()
print "GPU", gpu_id, "Device Name: " ,nv.nvmlDeviceGetName(handle)
while (1):
    try:
        memory = nv.nvmlDeviceGetMemoryInfo(handle)
        device_util = nv.nvmlDeviceGetUtilizationRates(handle)
        print "Memory total:", memory.total / 1024 / 1024, "M.   ", "Memory used:", memory.used / 1024 / 1024, "M."
        print "Memory-util: %.2f" % (memory.used * 100.0 / memory.total), "%.     ", "GPU-util:", device_util.gpu, "%."
        time.sleep(query_interval)
    except IndexError,e:
        nv.nvmlShutdown()
        print "process  terminal!"
        sys.exit()
'''
while(1):
    try:
        pid_obj = os.popen('pgrep -f matrix_apps_config_8801')
        pid = int(pid_obj.read().split()[0])
        print pid
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
'''
