import multiprocessing

class Environment():
    def __init__(self):
        self.max_core = multiprocessing.cpu_count()
        print("max_core: ", self.max_core)
        self.netinf_name = "enp101s0f0"
        self.vnetinf_name = "enp1s0"
        self.server_ip = "10.150.21.215"
        self.vm_name = "ubuntu18.04"

        self.debug = False
        #self.debug = True
        self.mode = "monitor" 
        #self.mode = "vcoact" 
        self.is_tracer = True
        self.period = 0.1 #s
        self.hqm_ebpf_path = "monitor/hqm_ebpf.c"
        self.slo = 1

        self.vsock_enable = True

        half_core = int(self.max_core/2)

        self.cur_vm_core = {'start':int(half_core), 'end':int(self.max_core - 1)}
        self.cur_vhost_core = {'start':0, 'end':int(half_core - 1)}
        self.cur_hq_core = {'start':0, 'end':int(half_core - 1)}
        self.cur_t_core = {'start':0, 'end':int(half_core - 1)}
        self.cur_vq_core = {'start':0, 'end':int(half_core - 1)}
    
    def get_cur_core(self):
        vhost_core = self.cur_vhost_core.copy()
        hq_core = self.cur_hq_core.copy()
        vq_core = self.cur_vq_core.copy()
        vm_core =  self.cur_vm_core.copy()
        t_core = self.cur_t_core.copy()

        cur_core = [vhost_core,hq_core,vq_core,vm_core,t_core]
        return cur_core
    
    def set_cur_core(self,cur_core):
        [vhost_core,hq_core,vq_core,vm_core,t_core] = cur_core
        self.cur_vhost_core = vhost_core  
        self.cur_hq_core = hq_core 
        self.cur_vq_core = vq_core 
        self.cur_vm_core = vm_core 
        self.cur_t_core  = t_core 




