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
        self.mode = "monitor" 
        #self.mode = "vcoact" 
        self.period = 0.1 #s
        self.hqm_ebpf_path = "monitor/hqm_ebpf.c"

        self.vsock_enable = True

        self.cur_vm_core = {'start':int(self.max_core/2), 'end':int(self.max_core - 1)}
        self.cur_vhost_core = {'start':0, 'end':int(self.max_core/2 - 1)}
        self.cur_hq_core = {'start':0, 'end':int(self.max_core/2 - 1)}
        self.cur_t_core = {'start':0, 'end':int(self.max_core - 1)}
        self.cur_vq_core = {'start':0, 'end':int(self.max_core/2 - 1)}



