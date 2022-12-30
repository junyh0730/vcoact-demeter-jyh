from cgroupspy import trees
from cgroupspy.trees import VMTree
import threading
import subprocess
import os
import time

class ActorHyp():
    def __init__(self,env):
        self.env = env

        x=bin((1<<self.env.max_core) - 1)
        x=format((int(x,2)),'x')
        self.HEX_CPUMASK_ALL = x.rjust(4,'0').encode() 

        self.l_fd_xps = list()
        self.cset_ctrl_vhost = None
        #self.cset_ctrl_lc_vcpu = None
        #self.cset_ctrl_be_vcpu = None
        #self.freezer_ctrl_be_vcpu = None
        self.vsock = None
        self.lc_vm = None
        self.be_vm = None
        self.fd_freezer = None

        #self.fd_test = os.open("/sys/fs/cgroup/cpuset/vhost/cpuset.cpus", os.O_WRONLY)

        self.__open_fd_xps()
        self.__init_cset_ctrl()
        self.__init_actor()

        return
    
    def act(self,action):
        [vhost_core,hq_core,vq_core,lc_vcpu_core,t_core] = action
        cur_core_alloc = action
        prev_core_alloc = [self.env.cur_vhost_core, self.env.cur_hq_core,
                           self.env.cur_vq_core, self.env.cur_lc_vcpu_core, self.env.cur_t_core]

        start_time = time.time()
        if self.env.cur_hq_core != hq_core:
            #self.__alloc_hq_core(hq_core)
            t = threading.Thread(target=self.__alloc_hq_core,args=(hq_core,))
            t.start()

        if self.env.cur_vhost_core != vhost_core:
            #self.__alloc_vhost_core(vhost_core)
            t = threading.Thread(target=self.__alloc_vhost_core,args=(vhost_core,))
            t.start()
        
        if self.env.cur_vq_core != vq_core:
            #self.__alloc_vq_core(vq_core)
            t = threading.Thread(target=self.__alloc_vq_core,args=(vq_core,))
            t.start()

        if self.env.cur_lc_vcpu_core != lc_vcpu_core:
            #self.__alloc_lc_vcpu_core(lc_vcpu_core)
            t = threading.Thread(target=self.__alloc_lc_vcpu_core,args=(lc_vcpu_core,))
            t.start()

        if self.env.cur_t_core != t_core:
            #self.__alloc_t_core(t_core)
            t = threading.Thread(target=self.__alloc_t_core,args=(t_core,))
            t.start()

        if self.env.is_be:
            """
            be_vcpu_core = {'start':-1, 'end':-1}
            be_vcpu_core['end'] = lc_vcpu_core['start'] - 1
            be_vcpu_core['start'] = vq_core['end'] + 1
            if be_vcpu_core['start'] > be_vcpu_core['end']:
                be_vcpu_core['start'] = -1
                be_vcpu_core['end'] = -1 
            """
            #print('be start and end:', be_vcpu_core['start'], '-', be_vcpu_core['end'])

            if self.env.cur_be_vcpu_core != be_vcpu_core:
                t = threading.Thread(target=self.__alloc_be_vcpu_core,args=(be_vcpu_core,))
                t.start()

            
        end_time = time.time()
        if self.env.debug:
            print('act time: ',(end_time - start_time) * 1000 * 1000, "us")

        self.env.set_cur_core(action)
        return prev_core_alloc, cur_core_alloc
    
    def act_demeter(self,action):
        [lc_vcpu_core, be_vcpu_core] = action
        cur_core_alloc = action
        prev_core_alloc = [self.env.cur_lc_core, self.env.cur_be_core]

        start_time = time.time()

        if self.env.cur_lc_core != lc_vcpu_core:
            #self.__alloc_lc_vcpu_core(lc_vcpu_core)
            t1 = threading.Thread(target=self.__alloc_lc_vcpu_core,args=(lc_vcpu_core,))
            t2 = threading.Thread(target=self.__alloc_t_core,args=(lc_vcpu_core,))
            #print("t = threading.Thread(target=self.__alloc_lc_vcpu_core,args=(lc_vcpu_core,))")
            t1.start()
            t2.start()
            t1.join()
            t2.join()

        if self.env.is_be:
            """
            be_vcpu_core = {'start':-1, 'end':-1}
            be_vcpu_core['end'] = lc_vcpu_core['start'] - 1
            be_vcpu_core['start'] = vq_core['end'] + 1
            if be_vcpu_core['start'] > be_vcpu_core['end']:
                be_vcpu_core['start'] = -1
                be_vcpu_core['end'] = -1 
            """
            #print('be start and end:', be_vcpu_core['start'], '-', be_vcpu_core['end'])

            if self.env.cur_be_core != be_vcpu_core:
                t1 = threading.Thread(target=self.__alloc_be_vcpu_core,args=(be_vcpu_core,))
                t2 = threading.Thread(target=self.__alloc_t_core,args=(be_vcpu_core,))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
            
        end_time = time.time()
        if self.env.debug:
            print('act time: ',(end_time - start_time) * 1000 * 1000, "us")

        self.env.set_cur_core_demeter(action)
        return prev_core_alloc, cur_core_alloc
    
    def __init_actor(self):
        self.__alloc_lc_vcpu_core(self.env.cur_lc_core)
        #self.__alloc_vhost_core(self.env.cur_vhost_core)
        #self.__alloc_hq_core(self.env.cur_hq_core)
        self.__alloc_be_vcpu_core(self.env.cur_be_core)
        return
    
    def __alloc_be_vcpu_core(self,target):
        if target['start'] == -1:
            #self.freezer_ctrl_be_vcpu.state = 'FROZEN'
            os.write(self.fd_freezer, 'FROZEN'.encode())
            #print('be frozen')
        else:
            #self.freezer_ctrl_be_vcpu.state = 'THAWED'
            #self.cset_ctrl_be_vcpu.cpus = range(target['start'],target['end'] + 1)
            os.write(self.fd_freezer, 'THAWED'.encode())

            for t in self.be_vm.children:
                t.cpuset.cpus = range(target['start'],target['end'] + 1)

    
    def __alloc_lc_vcpu_core(self,target):
        """
        for cpu in range(self.env.max_core):
            cmd = "virsh vcpupin " + self.env.vm_name + " " + \
                str(cpu) + " " + str(target['start']) + \
                "-" + str(target['end'])
            subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            #subprocess.Popen(cmd, shell=True)
        """
        #self.cset_ctrl_lc_vcpu.cpus = range(target['start'],target['end'] + 1)
        for t in self.lc_vm.children:
            #print(t)
            t.cpuset.cpus = range(target['start'],target['end'] + 1)
            #print(range(target['start'],target['end'] + 1))
        return
    
    def __alloc_vhost_core(self,target):
        self.cset_ctrl_vhost.cpus = range(target['start'],target['end'] + 1)
        #strings = str(target['start'])+'-'+str(target['end'])
        #os.write(self.fd_test, strings.encode())
        return
    
    def __alloc_vq_core(self,target):
        alloc_str = "".join(["act vq " , str(target['start']) , " " , str(target['end']) , " \n"])

        pkt = alloc_str.encode('utf-8')
        self.vsock.send(pkt)
        return
    
    def __alloc_t_core(self,target):
        alloc_str = "".join(["act t " , str(target['start']) , " " , str(target['end']) , " \n"])

        pkt = alloc_str.encode('utf-8')
        self.vsock.send(pkt)
        return

    def __alloc_hq_core(self, target):
        num = int(target['end'] - target['start'] + 1)

        #rss
        ethtool_str = "ethtool -X " + \
            str(self.env.netinf_name) + " equal " + str(num)
        subprocess.Popen(ethtool_str, shell=True)

        #xps
        for i, fd in enumerate(self.l_fd_xps):
            if i < num:
                os.write(fd, self.HEX_CPUMASK_ALL)
            else:
                os.write(fd, '00'.encode())
        return
    
    def __open_fd_xps(self):
        for core in range(self.env.max_core):
            fd = os.open("/sys/class/net/" + str(self.env.netinf_name) +
                                 "/queues/tx-" + str(core) + "/xps_cpus", os.O_WRONLY)
            self.l_fd_xps.append(fd)
        return
    
    def __close_fd_xps(self):
        for fd in self.l_fd_xps:
            os.close(fd)
        return
    
    def __init_cset_ctrl(self):
        #for vhost
        t = trees.Tree()
        cset = t.get_node_by_path('/cpuset/')
        cset_vhost = None
        try:
            cset_vhost = cset.create_cgroup('vhost')
        except:
            cset_vhost = t.get_node_by_path('/cpuset/vhost')

        self.cset_ctrl_vhost = cset_vhost.controller

        grep_cmd="ps -eLF | grep \"vhost-\"[0-9] |awk '{print $4}'"
        vhost_tids = subprocess.check_output(grep_cmd,shell=True)
        vhost_tids = vhost_tids.decode('utf-8').split()

        self.cset_ctrl_vhost.mems = [0]
        for t in vhost_tids:
            try:
                self.cset_ctrl_vhost.tasks = [t]
            except:
                continue
        
        
        #for lc vcpu
        vmt = VMTree()
        name = ''
        for vm_name in vmt.vms: 
            if self.env.lc_vm_name in vm_name:
                name = vm_name
                print(name)

        self.lc_vm = vmt.get_vm_node(name)

        """
        cset_lc_vcpu = None
        try:
            cset_lc_vcpu = cset.create_cgroup('vcpu-lc')
        except:
            cset_lc_vcpu = t.get_node_by_path('/cpuset/vcpu-lc')

        self.cset_ctrl_lc_vcpu = cset_lc_vcpu.controller

        grep_cmd="ps -eLF | grep " + self.env.lc_vm_name  +" |awk '{print $4}'"
        vcpu_tids = subprocess.check_output(grep_cmd,shell=True)
        vcpu_tids = vcpu_tids.decode('utf-8').split()
        print('lc tid',vcpu_tids)
        self.cset_ctrl_lc_vcpu.mems = [0]

        for t in vcpu_tids:
            try:
                self.cset_ctrl_lc_vcpu.tasks = [t]
            except:
                continue
        """
        

        name = None
        #for be vcpu
        for vm_name in vmt.vms: 
            if self.env.be_vm_name in vm_name:
                name = vm_name
                print(name)

        self.be_vm = vmt.get_vm_node(name)


        self.fd_freezer = os.open("/sys/fs/cgroup/freezer/machine/"+name+'/freezer.state', os.O_WRONLY)

        """
        t = trees.Tree()
        freezer = t.get_node_by_path('/freezer/')
        cset_be_vcpu = None
        freezer_be_vcpu = None
        try:
            cset_be_vcpu = cset.create_cgroup('vcpu-be')
        except:
            cset_be_vcpu = t.get_node_by_path('/cpuset/vcpu-be')
        root_cset_be_vcpu = t.get_node_by_path('/cpuset/')

        try:
            freezer_be_vcpu = freezer.create_cgroup('vcpu-be')
        except:
            freezer_be_vcpu = t.get_node_by_path('/freezer/vcpu-be')
        root_freezer_be_vcpu = t.get_node_by_path('/freezer/')

        self.cset_ctrl_be_vcpu = cset_be_vcpu.controller
        print(freezer_be_vcpu)
        self.freezer_ctrl_be_vcpu = freezer_be_vcpu.controller
        print(self.freezer_ctrl_be_vcpu)

        grep_cmd="ps -eLF | grep " + self.env.be_vm_name  +" |awk '{print $4}'"
        vcpu_tids = subprocess.check_output(grep_cmd,shell=True)
        vcpu_tids = vcpu_tids.decode('utf-8').split()
        print('be tid',vcpu_tids)
        self.cset_ctrl_be_vcpu.cpus = range(0,self.env.max_core)
        self.cset_ctrl_be_vcpu.mems = [0]

        for t in vcpu_tids:
            try:
                root_cset_be_vcpu.tasks = [t]
                self.cset_ctrl_be_vcpu.tasks = [t]
            except:
                print('BE cset failed')
                pass
            try:
                root_freezer_be_vcpu.tasks = [t]
                #self.freezer_ctrl_be_vcpu.tasks = [t]
            except:
                print('BE Freezer failed')
                pass
        """

        return
    
    def set_vsock(self,vsock):
        self.vsock = vsock
        self.__alloc_vq_core(self.env.cur_vq_core)
        self.__alloc_t_core(self.env.cur_t_core)

        return None