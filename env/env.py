import multiprocessing

class Environment():
    def __init__(self):
        self.max_core = multiprocessing.cpu_count()
        print("max_core: ", self.max_core)
        self.netinf_name = "enp101s0f0"
        self.vnetinf_name = "enp1s0"
        self.server_ip = "10.150.21.215"
        self.vm_name = "ubuntu18.04"

        self.debug = True
        self.period = 1 #s
        self.hqm_ebpf_path = "monitor/hqm_ebpf.c"

        self.vsock_enable = False 
