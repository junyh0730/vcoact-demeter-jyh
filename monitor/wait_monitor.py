import subprocess
import os,re
from cgroupspy import trees
from numba import jit
import numpy as np
import time
import psutil


@jit(nopython=True, cache=True)
def cal_pctg(arr_start_traffic, arr_end_traffic):
    arr_idle_time = arr_end_traffic - arr_start_traffic
    arr_pctg = arr_idle_time#arr_non_idle_time * 100 / arr_total
    
    '''
    non_idle_time = end_non_idle - start_non_idle
    idle_time = end_idle - start_idle
    total = non_idle_time + idle_time
    pctg = round(non_idle_time * 100 / total, 3)
    '''
    return arr_pctg


@jit(nopython=True, cache=True)
def cal_time(arr_stat):
    arr_idle = arr_stat[:, 3] + arr_stat[:, 4]
    arr_non_idle = arr_stat[:, 0] + arr_stat[:, 1] +\
        arr_stat[:, 2] + arr_stat[:, 5] + arr_stat[:, 6] + arr_stat[:, 7]
    #idle_time = idle + iowait
    #non_idle_time = user + nice + sys + irq + softirq + steal
    return arr_idle, arr_non_idle



class WaitMonitor():
    def __init__(self,env):
        t = trees.Tree()
        cpuacct = t.get_node_by_path('/cpuacct')
        self.env = env
        self.ctrl = cpuacct.controller
        #self.fd_stat = os.open('/proc/schedstat',os.O_RDONLY)
        self.lc_vm = self.env.lc_vm_name
        self.be_vm = self.env.be_vm_name

        self.start_wait_lc = None
        self.end_wait_lc = None
        self.start_wait_be = None
        self.end_wait_be = None

        #self.fd_stat = os.open("/sys/class/net/" + str(self.env.vnetinf_name) +
        #                         "/statistics/rx_bytes", os.O_RDONLY)
        return
    
    def start(self):
        #start record
        #self.start_usage_percpu = self.ctrl.usage_percpu
        self.start_wait_lc = self.__read_stat(self.lc_vm)
        self.start_wait_be = self.__read_stat(self.be_vm)
        #print("wait monitor start~~",self.start_wait, self.end_wait)
        return 
    
    def end(self):
        #end record
        #self.end_usage_percpu = self.ctrl.usage_percpu
        #self.end_traffic = self.__read_stat()
        self.end_wait_lc = self.__read_stat(self.lc_vm)
        self.end_wait_be = self.__read_stat(self.be_vm)
        #print("wait monitor end~~",self.end_wait)
        return
    
    def get(self,diff_time):
        
        result = []
        result_lc = self.end_wait_lc - self.start_wait_lc
        result_be = self.end_wait_be - self.start_wait_be
        
        result.append(result_lc)
        result.append(result_be)
        #print(arr_result)
        #arr_result = np.subtract(self.end_wait - self.start_wait)
        
        # print((self.env.cur_lc_core['end'] + 1))
        
        #result = np.sum(arr_result) # /(self.env.cur_lc_core['end'] + 1) 
        
        #print(result)
        
        #result = self.start_wait #self.end_traffic - self.start_traffic
        #result = cal_pctg(self.start_traffic, self.end_traffic)
        
        return result

    
    
    def get_raw(self):
        self.arr_start_traffic = self.__read_stat()
        return self.arr_start_traffic
    
    
    def __read_stat(self, vm):
        
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
                
        return wait