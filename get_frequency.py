import subprocess
import os,re
import numpy as np

def read_stat(core_num):
    
    
    grep_cmd="cat /proc/cpuinfo | grep MHz"
    freq_arr = subprocess.check_output(grep_cmd,shell=True)
    print(freq_arr)
    freq_arr = freq_arr.decode('utf-8').split("\n")
    
    print(freq_arr)
    
    freq_avg = 0
    
    for i in range(0,core_num):
        line = freq_arr[i].split()
        print(line)
        freq_avg += float(line[3])
    
    freq_avg = freq_avg/core_num
    
    print(freq_avg)
    """
    arr_wait = np.array([])
    
    pid_fd = os.open("/var/run/libvirt/qemu/" + str(vm) +
                                ".pid", os.O_RDONLY)
    
    os.lseek(pid_fd, 0, 0)
    lines = os.read(pid_fd, 2000)
    vm_pid = str(lines.decode())
    os.close(pid_fd)
    
    vm_fd = os.open("/proc/" + str(vm_pid) +
                                "/schedstat", os.O_RDONLY)
    
    
    os.lseek(vm_fd, 0, 0)
    lines = os.read(vm_fd, 5000)
    lines = str(lines.decode())
    stat = re.split("\s+", lines.strip())[:3]
    wait = int(stat[1])
    
    os.close(vm_fd)
    """
    """
    for line in lines:
        if line.startswith("cpu"):
            stat = re.split("\s+", line.strip())[:10]
            cpu = stat[0]
            wait_time = int(stat[8]) # ns\
            print(stat[0], stat[8])
            #print(type(wait_time))
            #print(cpu, wait_time)

            #if cpu == 'cpu':
            arr_wait = np.append(arr_wait, wait_time)
                
    #print(arr_wait)
    
    return arr_wait
    """
            
    return freq_arr

if __name__ == "__main__":
    try:
        read_stat(16)
    except KeyboardInterrupt:
        sys.exit(0)