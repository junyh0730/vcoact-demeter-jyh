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



class TrafficMonitor():
    def __init__(self,env):
        t = trees.Tree()
        cpuacct = t.get_node_by_path('/cpuacct')
        self.env = env
        self.ctrl = cpuacct.controller


        self.start_traffic = None
        self.end_traffic = None

        self.fd_stat = os.open("/sys/class/net/" + str(self.env.netinf_name) +
                                 "/statistics/rx_bytes", os.O_RDONLY)
        return
    
    def start(self):
        #start record
        #self.start_usage_percpu = self.ctrl.usage_percpu
        self.start_traffic = self.__read_stat()
        return 
    
    def end(self):
        #end record
        #self.end_usage_percpu = self.ctrl.usage_percpu
        self.end_traffic = self.__read_stat()
        return
    
    def get(self,diff_time):
        
        result = self.end_traffic - self.start_traffic
        #result = cal_pctg(self.arr_start_traffic, self.arr_end_traffic)
        
        

        return result

    
    
    def get_raw(self):
        self.arr_start_traffic = self.__read_stat()
        return self.arr_start_traffic
    
    
    def __read_stat(self):
        traffic = 0
        os.lseek(self.fd_stat, 0, 0)
        lines = os.read(self.fd_stat, 2000)
        lines = str(lines.decode())
        #lines = lines.split("\n")
        
        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        traffic = int(lines)
        #print(traffic)
        #print(lines)

        return traffic

