import subprocess
import os,re
from cgroupspy import trees
from numba import jit
import numpy as np
import time
import psutil


@jit(nopython=True, cache=True)
def cal_pctg(arr_start_idle, arr_end_idle,arr_start_non_idle,arr_end_non_idle):
    arr_non_idle_time = arr_end_non_idle - arr_start_non_idle
    arr_idle_time = arr_end_idle - arr_start_idle
    arr_total = arr_non_idle_time + arr_idle_time
    arr_pctg = arr_non_idle_time * 100 / arr_total
    
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



class CPUMonitor():
    def __init__(self,env):
        t = trees.Tree()
        cpuacct = t.get_node_by_path('/cpuacct')
        self.ctrl = cpuacct.controller
        self.start_usage_percpu = None
        self.env_usage_percpu = None


        self.arr_start_idle = np.array([])
        self.arr_end_idle = np.array([])
        self.arr_start_non_idle = np.array([])
        self.arr_end_non_idle = np.array([])

        self.fd_stat = os.open('/proc/stat', os.O_RDONLY)
        return
    
    def start(self):
        #start record
        #self.start_usage_percpu = self.ctrl.usage_percpu
        self.arr_start_idle, self.arr_start_non_idle = self.__read_stat()
        return 
    
    def end(self):
        #end record
        #self.end_usage_percpu = self.ctrl.usage_percpu
        self.arr_end_idle, self.arr_end_non_idle = self.__read_stat()
        return
    
    def get(self,diff_time):
        result = cal_pctg(self.arr_start_idle, self.arr_end_idle,
                          self.arr_start_non_idle,self.arr_end_non_idle)
        """
        for start, end in zip(self.start_usage_percpu,self.end_usage_percpu):
            diff = end - start
            pctg = round(diff * 100 / diff_time, 3)
            result.append(pctg)
    
        for start_idle, end_idle, start_non_idle, end_non_idle \
            in zip(self.arr_start_idle, self.arr_end_idle, \
                self.arr_start_non_idle, self.arr_end_non_idle):

            pctg = self.__cal_pctg(start_idle, end_idle,
                                   start_non_idle,  end_non_idle)
            result.append(pctg)
        """

        return result

    
    
    def get_raw(self):
        self.arr_start_idle, self.arr_start_non_idle = self.__read_stat()
        return self.arr_start_idle, self.arr_start_non_idle
    
    
    def __read_stat(self):
        rst = psutil.cpu_times(percpu=True)
        arr_idle = np.array([])
        arr_non_idle = np.array([])
        arr_stat = np.empty((0, 10), np.float64)
        """
        cpu : user nice system idle iowait irq softirq steal guest guest_nice
        cpu0 : ...
        idle_time = idle + iowait
        non_idle_time = user + nice + system + irq + softirq + steal
        total = idle_time + non_idle_time
        previous_total = previous_idle + previous_non_idle
        current_total = current_idle + current_non_idle
        diff_total = current_total - previous_total
            diff_idle = current_idle - previous_idle
            cpu_usage_percentage = ( diff_total - diff_idle )/ diff_total * 100
        """

        start_time =time.time()
        arr_stat = np.array(rst)
        end_time =time.time()
        #print("read stat time: ",str((end_time - start_time) * 1000),'ms')

        arr_idle, arr_non_idle = cal_time(arr_stat)

        #arr_idle = np.append(arr_idle,idle_time)
        #arr_non_idle = np.append(arr_non_idle,non_idle_time)

        return arr_idle, arr_non_idle


   

    """
        cpu : user nice system idle iowait irq softirq steal guest guest_nice
        cpu0 : ...
        idle_time = idle + iowait
        non_idle_time = user + nice + system + irq + softirq + steal
        total = idle_time + non_idle_time
        previous_total = previous_idle + previous_non_idle
        current_total = current_idle + current_non_idle
        diff_total = current_total - previous_total
            diff_idle = current_idle - previous_idle
            cpu_usage_percentage = ( diff_total - diff_idle )/ diff_total * 100
    """

    
    """
    def __read_stat(self):
        arr_idle = np.array([])
        arr_non_idle = np.array([])
        arr_stat = np.empty((0, 10), np.float64)
        
        start_time =time.time()
        os.lseek(self.fd_stat, 0, 0)
        lines = os.read(self.fd_stat, 2000)
        lines = str(lines.decode())
        lines = lines.split("\n")

        for line in lines:
            if line.startswith("cpu"):
                stat = re.split("\s+", line.strip())[:11]
                cpu = stat[0]
                user, nice, sys, idle, iowait, irq, softirq, steal, guest, guest_nice = map(
                    int, stat[1:])

                if cpu == 'cpu':
                    continue
                arr = np.array([[user, nice, sys, idle, iowait, irq, softirq,
                                steal, guest, guest_nice]], dtype=np.float64)
                arr_stat = np.append(arr_stat, arr, axis=0)
        
        end_time =time.time()
        print("read stat time: ",str((end_time - start_time) * 1000),'ms')

        arr_idle, arr_non_idle = cal_time(arr_stat)

        #arr_idle = np.append(arr_idle,idle_time)
        #arr_non_idle = np.append(arr_non_idle,non_idle_time)

        return arr_idle, arr_non_idle
    """


        
   