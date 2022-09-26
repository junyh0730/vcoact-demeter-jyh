from enum import Enum, auto
from pickle import MEMOIZE

class State(Enum):
    INC = auto()
    DEC = auto()
    STAY = auto()


class Vcoact():
    def __init__(self, env):
        self.env = env
        self.pkt_th = 70
        self.vcpu_th = 90
        self.margin = 0.1
        return
    
    def step(self,rst):
        #init
        action = None
        vhost_core = self.env.cur_vhost_core
        hq_core = self.env.cur_hq_core
        vq_core = self.env.cur_vq_core
        vm_core =  self.env.cur_vm_core
        t_core = self.env.cur_t_core

        #state
        state_vcpu = State.STAY
        state_pkt = State.STAY

        #get monitor
        [hqm_rst, cpum_rst] = rst

        #comp threshold
        util = cpum_rst[self.env.cur_vm_core['start']:self.env.cur_vm_core['end']] 
        vm_util = 100 * sum(util) / len(util)
        vm_util_if_dec = 100 * sum(util) / (len(util) - 1)
        if vm_util > self.vcpu_th:
            state_vm = State.INC
        elif vm_util_if_dec < self.vcpu_th * (1-self.margin):
            state_vm = State.DEC
        
        util =  cpum_rst[self.env.cur_hq_core['start']:self.env.cur_hq_core['end']]
        pkt_util = 100 * sum(util) / len(util)
        pkt_util_if_dec = 100 * sum(util) / (len(util) - 1)
        if pkt_util > self.pkt_th:
            state_pkt = State.INC
        elif pkt_util_if_dec < self.pkt_th * (1-self.margin):
            state_pkt = State.DEC
        
        #decide action
        #decide vcpu 
        if state_vcpu == State.INC:
            vm_core['start'] -= 1
            t_core['end'] += 1
        elif state_vcpu == State.DEC:
            if vm_core['start'] != self.env.max_core - 1:
                vm_core['start'] += 1
                t_core['end'] -= 1
        
        #decide pkt 
        if state_pkt == State.INC:
            hq_core['end'] += 1
            vq_core['end'] += 1
            vhost_core['end'] += 1
        elif state_pkt == State.DEC:
            if hq_core['end'] != 0:
                hq_core['end'] -= 1
                vq_core['end'] -= 1
                vhost_core['end'] -= 1
        
        action = [vhost_core,hq_core,vq_core,vm_core,t_core]

        if self.env.debug:
            print("vhost: ", vhost_core, "hq_core: ", hq_core, "vq_core: ",
                  vq_core, 'vm_core: ', vm_core, 't_core: ', t_core)

        return action
        
        

        


        









        
        
        return action
    

