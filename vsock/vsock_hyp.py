from vsock.vsock import VSock
from parser.parser import Parser
import socket

class VSockHYP(VSock):
    def __init__(self):
        super().__init__()
        self.user = "hyp"
        self.CID = socket.VMADDR_CID_HOST
        self.PORT = 9999
    
    def start(self):
        try: 
            super()._start_rx()
            super()._start_tx()
        finally:
            super()._end_rx()
            super()._end_tx()
            
        return
    
    def _cb_rx(self,buf):
        #trans
        [types, target, core_num, util] = Parser.transPktToData(buf)

        #collecct info
        self.actor_vm.alloc(target,core_num)
        return