import subprocess
from enum import Enum, auto
from pickle import MEMOIZE
import numpy as np
from numba import jit
import time


@jit(nopython=True, cache=True)
def cal_util(cpu_rst,vcpu_rst, cur_lc_core, cur_be_core):
    vm_util = float(-1)
    vm_util_if_dec = float(-1)
    pkt_util = float(-1)
    pkt_util_if_dec = float(-1)

    avg_cpu_rst = np.sum(cpu_rst)/(cur_lc_core) # for lc core
    #print(avg_cpu_rst)
    arr_vm = np.split(vcpu_rst, [cur_lc_core])[0]
    arr_pkt = np.split(cpu_rst, [cur_be_core])[0]
    vm_util = np.average(arr_vm)
    pkt_util = np.average(arr_pkt)

    if len(arr_vm) != 1:
        vm_util_if_dec = np.sum(arr_vm)/(len(arr_vm) - 1)
        #print(vm_util_if_dec)
    if len(arr_pkt) != 1:
        pkt_util_if_dec = np.sum(arr_pkt)/(len(arr_pkt) - 1)
        #print(pkt_util_if_dec)


    return avg_cpu_rst, vm_util_if_dec, pkt_util, pkt_util_if_dec


@jit(nopython=True, cache=True)
def cal_core_num(cpu_rst,vcpu_rst, cur_lc_core, cur_be_core, vm_th, pkt_th,max_core):
    arr_vm = np.split(vcpu_rst, [cur_lc_core])[0]
    arr_pkt = np.split(cpu_rst, [cur_be_core])[0]

    target_vm_core = int(np.ceil(np.sum(arr_vm) / vm_th))
    target_pkt_core = int(np.ceil(np.sum(arr_pkt) / pkt_th))

    if target_vm_core < 1:
        target_vm_core  = 1

    if target_pkt_core < 1:
        target_pkt_core  = 1

    if target_vm_core + target_pkt_core > max_core:
        total_core = target_vm_core + target_pkt_core
        target_vm_core = int(np.round(float(max_core) * target_vm_core / total_core))
        target_pkt_core = int(np.round(float(max_core) * target_pkt_core / total_core))


    return target_vm_core,target_pkt_core

"""
def read_freq(max_core, core_num):
    
    grep_cmd="cat /proc/cpuinfo | grep MHz"
    freq_arr = subprocess.check_output(grep_cmd,shell=True)

    freq_arr = freq_arr.decode('utf-8').split("\n")
    
    freq_avg = 0
    
    for i in range(max_core - core_num, max_core):
        line = freq_arr[i].split()
        freq_avg += float(line[3])
    
    freq_avg = freq_avg/core_num
    
    
    return freq_avg
"""



class State(Enum):
    INC = auto()
    DEC = auto()
    STAY = auto()


class Demeter():
    def __init__(self, env):
        self.env = env

        #memcached, vm th:  93 pkt th:  86
        self.pkt_th = 99
        self.vm_th = 99

        self.hot_area = 10
        self.warm_area = 10
        self.cold_area = 0
        
        self.margin = 0.1
        return
    
    def set_th(self, vm_th, pkt_th):
        if vm_th == -1:
            pass
        else:
            self.vm_th = vm_th

        if pkt_th == -1:
            pass
        else:
            self.pkt_th = pkt_th

        return None
    
    def __step_state_base(self,rst, traffic, wait_time):
        #init
        action = None
        [lc_core,be_core,cold] = self.env.get_cur_core()

        #state
        state_vcpu = State.STAY
        state_pkt = State.STAY

        #get monitor
        #[hqm_rst, cpum_rst] = rst

        #cal util
        cur_lc_core = self.env.cur_lc_core['end'] - self.env.cur_lc_core['start'] + 1
        cur_be_core = self.env.cur_be_core['end'] - self.env.cur_be_core['start'] + 1
        cpu_rst, vcpu_rst = rst
        vmtraffic = traffic
        #vm_util, vm_util_if_dec, pkt_util, pkt_util_if_dec = cal_util(
        #    cpu_rst, vcpu_rst ,cur_lc_core,cur_be_core)
        avg_cpu_rst, vm_util_if_dec, pkt_util, pkt_util_if_dec = cal_util(
            cpu_rst, vcpu_rst ,cur_lc_core,cur_be_core)    

        wait_time_lc = wait_time[0] #/cur_lc_core # need to implement
        wait_time_be = wait_time[1]
        # be_freq = read_freq(self.env.max_core ,cur_be_core)
        
        adjust_lc = 0
        cpv = (((self.cold_area + self.warm_area) * 10)/(10 + 10))
        scpv = (self.hot_area)*10/10
        print(wait_time, lc_core, be_core)
        
        if avg_cpu_rst < 0 or pkt_util <0:
            return [lc_core,be_core,cold]

        if self.env.debug:
            print('vm_util:',avg_cpu_rst,'pkt_util:',pkt_util)

        #line 6~10
        if wait_time_lc > 100: # 10us .. 10us(paper) 
            state_vcpu = State.INC
            adjust_lc = 1
            #print("wait...", adjust_lc, wait_time_lc)
        elif vmtraffic > 20000: # 200 MB/s  ...  need to change -> ingress_top(k,i)
            adjust_lc = max(cpv-scpv,0)
            #print("vmtraffic~ ", cpv, scpv, cpv-scpv)
        #line 15~20    
        if adjust_lc == 0:
            
            if wait_time_lc < 50: # 5 us(paper) (need to change the unit - this is not(implementation) 5 us)
                lcPreAdjust = cur_lc_core - 1
                edit_avg_cpu_rst = avg_cpu_rst * 100 # if this value < 1, some error occurred
                usage = edit_avg_cpu_rst / self.hot_area
                #print("# of hot area~~~ : ",self.hot_area)
                if edit_avg_cpu_rst / lcPreAdjust < (usage * 1.4): # line 17 of Demeter's main function... what is a etta function
                    #print("avg_cpu_rst... reduction", usage, edit_avg_cpu_rst / lcPreAdjust, " and wait~", wait_time_lc)
                    adjust_lc = adjust_lc - 1
            
        #algorithm 4
        
        wait = wait_time_lc * 0.95 # alpah is 0.05 ... record and forget mechanism
        
        if adjust_lc < 0:
            lcRducAdjust = cur_lc_core + adjust_lc
            if lcRducAdjust >= 1 and wait < 5000: # 5 means low lc threshhold 5 us, 1 means minimum number - this number is temporal number.
                # move one core from hot to cold
                # adjust pin range
                cur_lc_core -= 1
                if lc_core['end'] != 1:
                    lc_core['end'] -= 1
                    self.hot_area -= 1
                    self.cold_area += 1
                 # adjust core frequency to minimum
                 
        elif adjust_lc > 0:
            while adjust_lc > 0 and (lc_core['end'] != int(self.env.max_core - 2)):
                #move one core from warm/cold to hot
                
                cur_lc_core += 1
                if be_core['start'] == lc_core['end'] + 1: # no cold area
                    lc_core['end'] += 1
                    be_core['start'] += 1
                    self.hot_area += 1
                    self.warm_area -= 1
                else:
                    lc_core['end'] += 1
                    self.hot_area += 1
                    self.cold_area -= 1
                
                #adjust core frequency to maximum
                adjust_lc -= 1
        
        adjust_be = 0
        
        #line 24~27
        if wait_time_be > 10000: # 10us .. 10us(paper) 
            state_vcpu = State.INC
            adjust_be = 1
            #print("wait...be", adjust_be, wait_time_be)
        
        """
        #line 29~34    
        if adjust_be > 0 and be_freq < 2800:
            adjust_be = 0
        
        if be_freq < 2000:
            adjust_be = -(self.warm_area/2)
        """
            
        # Algorithm 5
        
        
        if adjust_be > 0:
            while adjust_be > 0 and (be_core['start'] > int(3)):
                #move one core from warm/cold to hot
                
                if be_core['start'] == lc_core['end'] + 1: # no cold area
                    break
                else:
                    be_core['start'] -= 1
                    self.warm_area += 1
                    self.cold_area -= 1
                    cur_be_core += 1
                
                #adjust core frequency to maximum
                adjust_be -= 1
            adjust_be = 0
                 
        elif adjust_be < 0:
            while adjust_be < 0 and (be_core['start'] != int(self.env.max_core - 2)):
                #move one core from warm to cold
                
                """
                if be_core['start'] == lc_core['end'] + 1: # no cold area
                    lc_core['end'] += 1
                    be_core['start'] += 1
                    self.hot_area += 1
                    self.warm_area -= 1
                else:
                """
                be_core['start'] += 1
                self.warm_area -= 1
                self.cold_area += 1
                cur_be_core -= 1
                #adjust core frequency to maximum
                adjust_be += 1
        
        action = [lc_core,be_core]



        if self.env.debug:
            print('util: ',rst)
            print('state_vcpu:',state_vcpu, 'state_pkt:',state_pkt)
            print("vhost: ", vhost_core, "hq_core: ", hq_core, "vq_core: ",
                  vq_core, 'vm_core: ', vm_core, 't_core: ', t_core)
            print('vm_th: ',self.vm_th,'pkt_th: ',self.pkt_th)

        return action
    
    def __step_util_base(self,rst):
        #init
        action = None
        [vhost_core,hq_core,vq_core,vm_core,t_core] = self.env.get_cur_core()
   
        #cal util
        cur_lc_core = self.env.cur_lc_core['end'] - self.env.cur_lc_core['start'] + 1
        cur_be_core = self.env.cur_be_core['end'] + 1
        
        cpu_rst, vcpu_rst = rst
        target_vm_core, target_pkt_core = cal_core_num(
            cpu_rst, vcpu_rst, cur_lc_core, cur_be_core, self.vm_th, self.pkt_th, self.env.max_core)
            
        vm_core['start'] = self.env.max_core - target_vm_core
        t_core['end'] = target_vm_core - 1
        hq_core['end'] = target_pkt_core - 1
        vq_core['end'] = target_pkt_core - 1
        vhost_core['end'] = target_pkt_core - 1

        action = [vhost_core,hq_core,vq_core,vm_core,t_core]

        if self.env.debug:
            print('util: ',rst)
            print("vhost: ", vhost_core, "hq_core: ", hq_core, "vq_core: ",
                  vq_core, 'vm_core: ', vm_core, 't_core: ', t_core)
            print('vm_th: ',self.vm_th,'pkt_th: ',self.pkt_th)

        return action


       
    def step(self,rst, traffic, wait_time):
        action = self.__step_state_base(rst, traffic, wait_time)
        #action = self.__step_util_base(rst)
        return action