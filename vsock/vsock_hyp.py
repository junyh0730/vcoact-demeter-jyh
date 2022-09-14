from vsock.vsock import VSock
from vsock.parser import Parser
import socket
import time

class VSockHYP(VSock):
    def __init__(self):
        super().__init__()
        self.user = "hyp"
        CID_VM = 3
        self.RX_CID = socket.VMADDR_CID_HOST
        self.RX_PORT = 9999
        self.TX_CID = CID_VM
        self.TX_PORT = 9998

        self.rx_data = bytearray() 

    
    def start(self):
        try: 
            super()._start_rx()
            time.sleep(3)
            super()._start_tx()
        finally:
            super()._end_rx()
            super()._end_tx()
            
        return
    
    def _cb_rx(self,buf):
        #trans
        self.rx_data.extend(buf)
        res, remainder = Parser.transPktToData(self.rx_data)
        self.rx_data = remainder

        for types, target, core_num, util in res:
            #collecct info
            if types == 'act':
                self.actor_vm.alloc(target, core_num)

        return