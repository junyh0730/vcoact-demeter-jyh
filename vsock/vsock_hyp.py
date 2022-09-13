from vsock.vsock import VSock
from vsock.parser import Parser
import socket

class VSockHYP(VSock):
    def __init__(self):
        super().__init__()
        self.user = "hyp"
        CID_VM = 3
        self.RX_CID = socket.VMADDR_CID_HOST
        self.RX_PORT = 9999
        self.TX_CID = CID_VM
        self.TX_PORT = 9998

    
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
        if types == 'act':
            self.actor_vm.alloc(target, core_num)

        return