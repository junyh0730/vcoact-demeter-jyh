from cgroupspy import trees
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
        self.cset_ctrl_vcpu = None
        self.vsock = None

        #self.fd_test = os.open("/sys/fs/cgroup/cpuset/vhost/cpuset.cpus", os.O_WRONLY)

        self.__open_fd_xps()
        self.__init_cset_ctrl()
        self.__init_actor()

        return
    
    def act(self,action):
        [vhost_core,hq_core,vq_core,vm_core,t_core] = action
        cur_core_alloc = action
        prev_core_alloc = [self.env.cur_vhost_core, self.env.cur_hq_core,
                           self.env.cur_vq_core, self.env.cur_vm_core, self.env.cur_t_core]

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

        if self.env.cur_vm_core != vm_core:
            #self.__alloc_vm_core(vm_core)
            t = threading.Thread(target=self.__alloc_vm_core,args=(vm_core,))
            t.start()

        if self.env.cur_t_core != t_core:
            #self.__alloc_t_core(t_core)
            t = threading.Thread(target=self.__alloc_t_core,args=(t_core,))
            t.start()
        end_time = time.time()
        if self.env.debug:
            print('act time: ',(end_time - start_time) * 1000 * 1000, "us")

        self.env.set_cur_core(action)
        return prev_core_alloc, cur_core_alloc
    
    def __init_actor(self):
        self.__alloc_vm_core(self.env.cur_vm_core)
        self.__alloc_vhost_core(self.env.cur_vhost_core)
        self.__alloc_hq_core(self.env.cur_hq_core)
        return

    
    def __alloc_vm_core(self,target):
        """
        for cpu in range(self.env.max_core):
            cmd = "virsh vcpupin " + self.env.vm_name + " " + \
                str(cpu) + " " + str(target['start']) + \
                "-" + str(target['end'])
            subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            #subprocess.Popen(cmd, shell=True)
        """
        self.cset_ctrl_vcpu.cpus = range(target['start'],target['end'] + 1)
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
        
        t = trees.Tree()
        cset_vcpu = None
        try:
            cset_vcpu = cset.create_cgroup('vcpu')
        except:
            cset_vcpu = t.get_node_by_path('/cpuset/vcpu')

        self.cset_ctrl_vcpu = cset_vcpu.controller

        grep_cmd="ps -eLF | grep \"qemu\" |awk '{print $4}'"
        vcpu_tids = subprocess.check_output(grep_cmd,shell=True)
        vcpu_tids = vcpu_tids.decode('utf-8').split()
        print('vcpu_tid',vcpu_tids)
        self.cset_ctrl_vcpu.mems = [0]

        for t in vcpu_tids:
            try:
                self.cset_ctrl_vcpu.tasks = [t]
            except:
                continue

        return
    
    def set_vsock(self,vsock):
        self.vsock = vsock
        self.__alloc_vq_core(self.env.cur_vq_core)
        self.__alloc_t_core(self.env.cur_t_core)

        return None
    
    