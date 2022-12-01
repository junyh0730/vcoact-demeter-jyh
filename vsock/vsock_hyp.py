from vsock.vsock import VSock
from vsock.parser import Parser
import socket
import time

class VSockHYP(VSock):
    def __init__(self,env,monitor,actor,q):
        super().__init__()
        self.env = env
        self.q = q
        self.user = "hyp"
        self.monitor = monitor
        self.actor = actor

        CID_VM = 3
        self.RX_CID = socket.VMADDR_CID_HOST
        self.RX_PORT = 9999
        self.TX_CID = CID_VM
        self.TX_PORT = 9998

        self.rx_data = bytearray() 

    
    def start(self):
        if self.env.vsock_enable == False:
            return None

        try: 
            super()._start_rx(self.q)
            time.sleep(3)
            super()._start_tx()
        except:
            print("vsock: start error in hyp")

                        
        return
    
    def end(self):
        if self.env.vsock_enable == False:
            return None

        super()._end_rx()
        super()._end_tx()

    
    def _cb_rx(self,buf,q):
        #trans
        self.rx_data.extend(buf)
        res, remainder = Parser.transPktToData(self.rx_data)
        self.rx_data = remainder

        for types, target, core_num, util in res:
            #collecct info
            if types == 'info':
                self.monitor.set_info(target, core_num, util,q)

            elif types == 'act':
                if target == "hq":
                    self.actor.alloc_hq_core(core_num)
                elif target == "vhost":
                    self.actor.alloc_vhost_core(core_num)
                elif target == "vm":
                    self.actor.alloc_vm_core(core_num)


        return