from vsock.vsock import VSock
from vsock.parser import Parser
from in_vm.actor_vm import ActorVM

class VSockVM(VSock):
    def __init__(self,actor_vm):
        super().__init__()

        self.user = "vm"
        CID_VM = 3
        self.CID = CID_VM
        self.PORT = 9998

        self.actor_vm = actor_vm
    
    def start(self):
        try: 
            super()._start_tx()
            super()._start_rx()
        finally:
            super()._end_tx()
            super()._end_rx()
            
        return
    
    def _cb_rx(self,buf):
        #trans
        [types, target, core_num] = Parser.transPktToData(buf)

        #alloc core
        self.actor_vm.alloc(target,core_num)
        return