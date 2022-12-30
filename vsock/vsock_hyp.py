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
        """
        CID_VM_LC = 4
        CID_VM_BE = 3
        self.RX_CID_LC = socket.VMADDR_CID_HOST
        self.RX_CID_BE = socket.VMADDR_CID_HOST
        self.RX_PORT_LC = 9999
        self.RX_PORT_BE = 9998
        self.TX_CID_LC = CID_VM_LC
        self.TX_CID_BE = CID_VM_BE
        self.TX_PORT_LC = 9997
        self.TX_PORT_BE = 9996
        """
        self.rx_data = bytearray() 

    
    def start(self):
        if self.env.vsock_enable == False:
            return None

        try: 
            super()._start_rx(self.q)
            time.sleep(3)
            print("super()._start_tx()")
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
            elif types == 'info_traffic':
                self.monitor.set_info_traffic(target, core_num, util,q)
            elif types == 'act':
                if target == "hq":
                    self.actor.alloc_hq_core(core_num)
                elif target == "vhost":
                    self.actor.alloc_vhost_core(core_num)
                elif target == "vm":
                    self.actor.alloc_vm_core(core_num)


        return