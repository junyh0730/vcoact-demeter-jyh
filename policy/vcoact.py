from enum import Enum, auto
from pickle import MEMOIZE

class State(Enum):
    INC = auto()
    DEC = auto()
    STAY = auto()


class Vcoact():
    def __init__(self, env):
        self.env = env
        self.pkt_th = 90
        self.vcpu_th = 85
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
        [hqm_rst, cpum_rst] = rst

        #cal util
        vm_raw_util = cpum_rst[self.env.cur_vm_core['start']:self.env.cur_vm_core['end'] + 1] 
        vm_util =  sum(vm_raw_util) / len(vm_raw_util)
        pkt_raw_util =  cpum_rst[self.env.cur_hq_core['start']:self.env.cur_hq_core['end'] + 1]
        pkt_util =  sum(pkt_raw_util) / len(pkt_raw_util)

        print('vm_util:',vm_util,'pkt_util:',pkt_util)

        #comp threshold
        #for vm
        if len(vm_raw_util) > 1:
            vm_util_if_dec = sum(vm_raw_util) / (len(vm_raw_util) - 1)
            if vm_util_if_dec < self.vcpu_th * (1-self.margin):
                state_vcpu = State.DEC
        if vm_util > self.vcpu_th:
            state_vcpu = State.INC
                
        #for pkt
        if len(pkt_raw_util) > 1:
            pkt_util_if_dec = sum(pkt_raw_util) / (len(pkt_raw_util) - 1)
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
            print('util: ',cpum_rst)
            print('state_vcpu:',state_vcpu, 'state_pkt:',state_pkt)
            print("vhost: ", vhost_core, "hq_core: ", hq_core, "vq_core: ",
                  vq_core, 'vm_core: ', vm_core, 't_core: ', t_core)

        return action
        
        

        


        









        
        
    

