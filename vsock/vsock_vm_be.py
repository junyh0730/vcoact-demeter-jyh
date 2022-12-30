from vsock.vsock import VSock
from vsock.parser import Parser
from actor.actor_vm import ActorVM
import socket
import threading

class VSockVM(VSock):
    def __init__(self, actor_vm, env, start_e=None,end_e=None):
        super().__init__()

        self.env = env
        self.user = "vm"
        
        """
        CID_VM = 4
        self.TX_CID = socket.VMADDR_CID_HOST
        self.TX_PORT = 9999
        self.RX_CID = CID_VM
        self.RX_PORT = 9998
        """
        CID_VM_LC = 4
        CID_VM_BE = 3
        self.TX_CID_LC = socket.VMADDR_CID_HOST
        self.TX_CID_BE = socket.VMADDR_CID_HOST
        self.TX_PORT_LC = 9999
        self.TX_PORT_BE = 9998
        self.RX_CID_LC = CID_VM_LC
        self.RX_CID_BE = CID_VM_BE
        self.RX_PORT_LC = 9997
        self.RX_PORT_BE = 9996
        
        self.actor_vm = actor_vm
        self.rx_data = bytearray()

        self.start_e = start_e
        self.end_e = end_e

    
    def start(self):
        if self.env.vsock_enable == False:
            return None

        try: 
            super()._start_tx_be()
            print("super()._start_rx(None)")
            super()._start_rx_be(None)

        except:
            print("vsock: start error in vm")
                        
        return
    ## jyh - send
    """def send(self, s):
        if self.env.vsock_enable == False:
            return None

        try: 
            print("super().send")
            super().send(s)

        except:
            print("vsock: send error in vm")
                        
        return
    """
    def end(self):
        if self.env.vsock_enable == False:
            return None

        super()._end_tx()
        super()._end_rx()

    def set_e(self,start_e,end_e):
        self.start_e = start_e
        self.end_e = end_e
    
    def _cb_rx(self,buf,q):
        #trans
        self.rx_data.extend(buf)
        res, remainder = Parser.transPktToData(self.rx_data)
        self.rx_data = remainder

        #act
        for types, target, arg0, arg1 in res:
            if types == "act":
                if target == "start":
                    self.end_e.clear()
                    self.start_e.set()

                elif target == "end":
                    self.start_e.clear()
                    self.end_e.set()

                elif target == "t":
                    core_num = {'start':int(arg0), 'end':int(arg1)}
                    #self.actor_vm.alloc_t_core(core_num)
                    t = threading.Thread(target=self.actor_vm.alloc_t_core, args=(core_num,))
                    t.start()

                elif target == "vq":
                    core_num = {'start':int(arg0), 'end':int(arg1)}
                    #self.actor_vm.alloc_vq_core(core_num)
                    t = threading.Thread(target=self.actor_vm.alloc_vq_core, args=(core_num,))
                    t.start()


        return
