from enum import Enum, auto
from pickle import MEMOIZE

class State(Enum):
    INC = auto()
    DEC = auto()
    STAY = auto()


class Vcoact():
    def __init__(self, env):
        return
    
    def step(self,rst):
        task_s, hq_s, vq_s, vcpu_s = State.STAY, State.STAY, State.STAY, State.STAY
        taskm_rst, hqm_rst, vqm_rst, vcpum_rst = rst

        action = None
        #decide load of each core allocation

        
        
        return action
    

