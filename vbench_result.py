import subprocess
import os,re
from cgroupspy import trees
from numba import jit
import numpy as np
import time
import psutil


def read_stat():
    
    """
    wait_time = 0.0
    #lines = lines.split("\n")
    a = subprocess.run(["/home/vm/vcoact-demeter/vcoact/perf_sched.sh", "arguments"], shell=True, capture_output=True)
    grep_cmd="sed -n '/memcached/p' result.txt"
    wait_time_arr = subprocess.check_output(grep_cmd,shell=True)
    wait_time_arr = wait_time_arr.decode('utf-8').split()
    
    if (wait_time_arr): # not empty
        wait_time = wait_time_arr[8]
    else:
        wait_time = 0
    #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #print(lines)
    """
    
    fd_stat = os.open('/home/vm/vcoact-demeter/vbench/result.txt',os.O_RDWR)
    
    os.lseek(fd_stat, 0, 0)
    lines = os.read(fd_stat, 5000)
    lines = str(lines.decode())
    lines = lines.split(",")
    
    total_time = 0
    
    for line in lines:
        if (not line.startswith("#")):
            stat = re.split("\s+", line.strip())[:4]
            trans_time = int(stat[1])
            total_time += trans_time

    os.write(fd_stat,"total time")
    os.write(fd_stat,total_time)
    os.close(fd_stat)
    #print(arr_wait)
    
    print("vbench transcoding total time : ", total_time)
    
    return total_time

if __name__ == "__main__":
    try:
        read_stat()
    except KeyboardInterrupt:
        sys.exit(0)