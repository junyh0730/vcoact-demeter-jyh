from enum import Enum, auto
from pickle import MEMOIZE
import numpy as np
from numba import jit
import time


@jit(nopython=True, cache=True)
def cal_util(rst, cur_vm_core, cur_hq_core):
    vm_util = float(-1)
    vm_util_if_dec = float(-1)
    pkt_util = float(-1)
    pkt_util_if_dec = float(-1)

    arr_vm = np.split(rst, [cur_vm_core])[1]
    arr_pkt = np.split(rst, [cur_hq_core])[0]

    vm_util = np.average(arr_vm)
    pkt_util = np.average(arr_pkt)

    if len(arr_vm) != 1:
        vm_util_if_dec = np.sum(arr_vm)/(len(arr_vm) - 1)
    if len(arr_pkt) != 1:
        pkt_util_if_dec = np.sum(arr_pkt)/(len(arr_pkt) - 1)

    #print('vm_util:',vm_util,'pkt_util:',pkt_util)
    #print('vm_util_if:',vm_util_if_dec,'pkt_util_if:',pkt_util_if_dec)

    return vm_util, vm_util_if_dec, pkt_util, pkt_util_if_dec



class State(Enum):
    INC = auto()
    DEC = auto()
    STAY = auto()


class Vcoact():
    def __init__(self, env):
        self.env = env

        self.pkt_th = 80
        self.vcpu_th = 70

        self.margin = 0.1
        return
    
       
    def step(self,rst):
        #init
        action = None
        [vhost_core,hq_core,vq_core,vm_core,t_core] = self.env.get_cur_core()

        #state
        state_vcpu = State.STAY
        state_pkt = State.STAY

        #get monitor
        #[hqm_rst, cpum_rst] = rst


        #cal util
        cur_vm_core = self.env.cur_vm_core['start']
        cur_hq_core = self.env.cur_hq_core['end'] + 1
        vm_util, vm_util_if_dec, pkt_util, pkt_util_if_dec = cal_util(
            rst,cur_vm_core,cur_hq_core)
            

        if vm_util < 0 or pkt_util <0:
            return [vhost_core,hq_core,vq_core,vm_core,t_core] 

        if self.env.debug:
            print('vm_util:',vm_util,'pkt_util:',pkt_util)

        #comp threshold
        #for vm
        if vm_util_if_dec < self.vcpu_th * (1-self.margin):
                state_vcpu = State.DEC
        if vm_util > self.vcpu_th:
            state_vcpu = State.INC
                
        #for pkt
        if pkt_util_if_dec < self.pkt_th * (1-self.margin):
                state_pkt = State.DEC
        if pkt_util > self.pkt_th:
            state_pkt = State.INC

        #decide action
        #act dec
        if state_vcpu == State.DEC:
            if vm_core['start'] != self.env.max_core - 1:
                vm_core['start'] += 1
                t_core['end'] -= 1
        if state_pkt == State.DEC:
            if hq_core['end'] != 0:
                hq_core['end'] -= 1
                vq_core['end'] -= 1
                vhost_core['end'] -= 1
        
        #act inc 
        if state_vcpu == State.INC:
            if vm_core['start'] != hq_core['end'] + 1:
                vm_core['start'] -= 1
                t_core['end'] += 1
        if state_pkt == State.INC:
            if vm_core['start'] != hq_core['end'] + 1:
                hq_core['end'] += 1
                vq_core['end'] += 1
                vhost_core['end'] += 1
       
        action = [vhost_core,hq_core,vq_core,vm_core,t_core]



        if self.env.debug:
            print('util: ',rst)
            print('state_vcpu:',state_vcpu, 'state_pkt:',state_pkt)
            print("vhost: ", vhost_core, "hq_core: ", hq_core, "vq_core: ",
                  vq_core, 'vm_core: ', vm_core, 't_core: ', t_core)

        return action
        
        

        


        









        
        
    

