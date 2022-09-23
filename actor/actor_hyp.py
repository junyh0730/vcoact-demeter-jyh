from cgroupspy import trees
import subprocess
import os

class ActorHyp():
    def __init__(self,env):
        self.env = env

        x=bin((1<<self.env.max_core) - 1)
        x=format((int(x,2)),'x')
        self.HEX_CPUMASK_ALL = x.rjust(4,'0').encode() 

        self.l_fd_xps = list()
        self.cset_ctrl = None
        self.vsock = None

        self.__open_fd_xps()
        self.__init_cset_ctrl()
        self.__init_actor()


        return

    
    def act(self,action):
        [vhost_core,hq_core,vq_core,vm_core,t_core] = action
        self.__alloc_vhost_core(vhost_core)
        self.__alloc_hq_core(hq_core)
        self.__alloc_vq_core(vq_core)
        self.__alloc_vm_core(vm_core)
        self.__alloc_t_core(t_core)
        return
    
    def __init_actor(self):
        self.__alloc_vm_core(self.env.cur_vm_core)
        self.__alloc_vhost_core(self.env.cur_vhost_core)
        self.__alloc_hq_core(self.env.cur_hq_core)
        return

    
    def __alloc_vm_core(self,target):
        for cpu in range(self.env.max_core):
            cmd = "virsh vcpupin " + self.env.vm_name + " " + \
                str(cpu) + " " + str(target['start']) + \
                "-" + str(target['end'])
            subprocess.Popen(cmd, shell=True)

            print(cmd)
        self.env.cur_vm_core = target
        return
    
    def __alloc_vhost_core(self,target):
        self.cset_ctrl.cpus = range(target['start'],target['end'] + 1)

        self.env.cur_vhost_core = target

        return
    
    def __alloc_vq_core(self,target):
        alloc_str = "act vq " + str(target['start']) + " " + str(target['end'])

        pkt = alloc_str.encode('utf-8')
        self.vsock.send(pkt)

        self.env.cur_vq_core = target
        return
    
    def __alloc_t_core(self,target):
        alloc_str = "act t " + str(target['start']) + " " + str(target['end'])

        pkt = alloc_str.encode('utf-8')
        self.vsock.send(pkt)

        self.env.cur_t_core = target
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
        self.env.cur_hq_core = target
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

        self.cset_ctrl = cset_vhost.controller

        grep_cmd="ps -eLF | grep \"vhost-\"[0-9] |awk '{print $4}'"
        vhost_tids = subprocess.check_output(grep_cmd,shell=True)
        vhost_tids = vhost_tids.decode('utf-8').split()

        for t in vhost_tids:
            try:
                self.cset_ctrl.tasks = [t]
            except:
                continue

        return
    
    def set_vsock(self,vsock):
        self.vsock = vsock
        return None
    
    