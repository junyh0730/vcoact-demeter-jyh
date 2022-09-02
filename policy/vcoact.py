from enum import Enum, auto
from pickle import MEMOIZE
from env.actor import Actor

class State(Enum):
    INC = auto()
    DEC = auto()
    STAY = auto()


class Vcoact():
    def __init__(self, env):
        self.actor = Actor(env)
        return
    
    def step(self,rst):
        task_s, hq_s, vq_s, vcpu_s = State.STAY, State.STAY, State.STAY, State.STAY
        taskm_rst, hqm_rst, vqm_rst, vcpum_rst = rst

        #decide load of each core allocation

        
        #chanage core allocation. 
        #for task
        if task_s == State.INC:
            self.actor.inc_task_core()
        elif task_s == State.DEC:
            self.actor.dec_task_core()

        #for hq
        if hq_s == State.INC:
            self.actor.inc_hq_core()
        elif hq_s == State.DEC:
            self.actor.dec_hq_core()
        
        #for vq
        if vq_s == State.INC:
            self.actor.inc_vq_core()
        elif vq_s == State.DEC:
            self.actor.dec_vq_core()

        #for vcpu
        if vcpu_s == State.INC:
            self.actor.inc_vcpu_core()
        elif vcpu_s == State.DEC:
            self.actor.dec_vcpu_core()

        return
    

