from vsock.vsock import VSock

class VSockVM(VSock):
    def __init__(self):
        super().__init__()

        self.user = "vm"
        CID_VM = 3
        self.CID = CID_VM
        self.PORT = 9998
    
    def start(self):
        try: 
            super()._start_tx()
            super()._start_rx()
        finally:
            super()._end_tx()
            super()._end_rx()
            
        return