from vsock.vsock import VSock
from vsock.parser import Parser
from actor.actor_vm import ActorVM
import socket

class VSockVM(VSock):
    def __init__(self, actor_vm, env):
        super().__init__()

        self.env = env
        self.user = "vm"
        CID_VM = 3
        self.TX_CID = socket.VMADDR_CID_HOST
        self.TX_PORT = 9999
        self.RX_CID = CID_VM
        self.RX_PORT = 9998

        self.actor_vm = actor_vm

    
    def start(self):
        if self.env.vsock_enable == False:
            return None

        try: 
            super()._start_tx()
            super()._start_rx()

        except:
            print("vsock: start error in vm")
                        
        return
    
    def end(self):
        if self.env.vsock_enable == False:
            return None

        super()._end_tx()
        super()._end_rx()

    def set_e(self,start_e,end_e):
        self.start_e = start_e
        self.end_e = end_e
    
    def _cb_rx(self,buf):
        #trans

        self.rx_data.extend(buf)
        res, remainder = Parser.transPktToData(self.rx_data)
        self.rx_data = remainder


        #act

        for types, target, core_num, util in res:
            if types == "act":
                if target == "start":
                    self.start_e.set()

                elif target == "end":
                    self.end_e.set()

                elif target == "t":
                    self.actor_vm.alloc_t_core(core_num)

                elif target == "vq":
                    self.actor_vm.alloc_vq_core(core_num)

        return