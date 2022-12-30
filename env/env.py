import multiprocessing

class Environment():
    def __init__(self):
        self.max_core = multiprocessing.cpu_count()
        print("max_core: ", self.max_core)
        #self.netinf_name = "enp101s0f0"
        self.netinf_name = "enp101s0f0"
        self.vnetinf_name = "enp1s0"
        #self.server_ip = "10.150.21.215"
        self.server_ip = "10.150.21.215"
        self.lc_vm_name = "ubuntu18.04-lc"
        self.be_vm_name = "ubuntu18.04-be"

        self.debug = False
        #self.debug = True
        #self.mode = "monitor" 
        #self.mode = "vcoact" 
        self.mode = "demeter"
        #self.is_be=False
        self.is_be=True
        self.is_tracer = False #True
        #self.period = 0.1 #s
        self.period = 0.1#s .. for demeter
        self.hqm_ebpf_path = "monitor/hqm_ebpf.c"
        self.slo = 1

        self.vsock_enable = True

        half_core = int(self.max_core/2)

        #self.cur_lc_vcpu_core = {'start':int(half_core), 'end':int(self.max_core - 1)}
        #self.cur_be_vcpu_core = {'start':-1, 'end':-1}
        self.cur_vhost_core = {'start':0, 'end':int(half_core - 1)}
        self.cur_hq_core = {'start':0, 'end':int(half_core - 1)}
        self.cur_t_core = {'start':0, 'end':int(half_core - 1)}
        self.cur_vq_core = {'start':0, 'end':int(half_core - 1)}
        
        #demeter
        self.cur_lc_core = {'start':0, 'end':int(half_core - 1)}#'end':int(half_core - 1)}
        self.cur_be_core = {'start':int(half_core), 'end':int(self.max_core - 1)} # int(half_core)
        self.cur_cold_corenum = 0
    
    def get_cur_core(self):
        vhost_core = self.cur_vhost_core.copy()
        hq_core = self.cur_hq_core.copy()
        vq_core = self.cur_vq_core.copy()
        vm_core = self.cur_lc_core.copy()
        t_core = self.cur_t_core.copy()
        
        if self.mode == "demeter":
            lc_core = self.cur_lc_core.copy()
            be_core = self.cur_be_core.copy()
            cold = self.cur_cold_corenum
            cur_core = [lc_core, be_core, cold]
            return cur_core

        cur_core = [vhost_core,hq_core,vq_core,vm_core,t_core]
        return cur_core
    
    def set_cur_core(self,cur_core):
        [vhost_core,hq_core,vq_core,vm_core,t_core] = cur_core
        self.cur_vhost_core = vhost_core  
        self.cur_hq_core = hq_core 
        self.cur_vq_core = vq_core 
        self.cur_lc_vcpu_core = vm_core
        self.cur_t_core  = t_core 

    def set_cur_core_demeter(self,cur_core):
        [lc_core, be_core] = cur_core
        self.cur_lc_core = lc_core
        self.cur_be_core = be_core

    def set_cur_core_demeter(self,cur_core):
        [lc_core, be_core] = cur_core
        self.cur_lc_core = lc_core
        self.cur_be_core = be_core



