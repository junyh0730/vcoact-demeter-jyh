from cgroupspy import trees
import subprocess
import os

class ActorVM():
    def __init__(self,env):
        self.env = env

        x=bin((1<<self.env.max_core) - 1)
        x=format((int(x,2)),'x')
        self.HEX_CPUMASK_ALL = x.rjust(4,'0').encode() 

        self.cur_t_core = {'start':0, 'end':int(env.max_core - 1)}
        self.cur_vq_core = {'start':0, 'end':int(env.max_core/2 - 1)}

        self.l_fd_xps = list()
        self.ll_fd_irq_aff = list()
        self.ll_fd_irq_aff_list = list()

        self.__open_fd_xps()
        self.__open_fd_irq()
        self.__init_cset_ctrl()
        self.__init_actor()
        return
    
    def act(self,action):
        return
    
    def __open_fd_irq(self):
        for name in ["input", "output"]:
            grep_cmd = "IRQ_NUM_LIST=`cat /proc/interrupts | grep " + str(name) + " | awk -F: '{print $1}'`"
            irqs = subprocess.check_output(grep_cmd,shell=True)
            l_irq = irqs.decode('utf-8').split()

            l_fd_irq_aff = list()
            l_fd_irq_aff_list = list()

            for irq in l_irq:
                fd_irq_aff = os.open("/proc/irq/"+str(irq)+"/smp_affinity")
                fd_irq_aff_list = os.open("/proc/irq/"+str(irq)+"/smp_affinity_list")

                l_fd_irq_aff.append(fd_irq_aff)
                l_fd_irq_aff_list.append(fd_irq_aff_list)
            
            self.ll_fd_irq_aff.append(l_fd_irq_aff)
            self.ll_fd_irq_aff_list.append(l_fd_irq_aff_list)
        
        return
    
    def __close_fd_irq(self):
        for l_fd_irq_aff, l_fd_irq_aff_list in zip(self.ll_fd_irq_aff, self.ll_fd_irq_aff_list):
            for fd_irq_aff, fd_irq_aff_list in zip(l_fd_irq_aff, l_fd_irq_aff_list):
                os.close(fd_irq_aff)
                os.close(fd_irq_aff_list)
    
    def __open_fd_xps(self):
        for core in range(self.env.max_core):
            fd = os.open("/sys/class/net/" + str(self.env.vnetinf_name) +
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
        cset_tasks = None
        try:
            cset_tasks = cset.create_cgroup('all_thread')
        except:
            cset_tasks = t.get_node_by_path('/cpuset/all_thread')

        self.cset_ctrl = cset_tasks.controller

        grep_cmd = "ps -eLF |awk '{print $4}' | awk '{if (NR!=1) {print}}'"
        tids = subprocess.check_output(grep_cmd,shell=True).decode('utf-8').split()

        for t in tids:
            try:
                self.cset_ctrl.tasks = [t]
            except:
                continue
        
        return

    
    def __init_actor(self):
        self.alloc_t_core(self.cur_t_core)
        self.alloc_vq_core(self.cur_vq_core)
        return
    
    def alloc_t_core(self,target):
        self.cset_ctrl.cpus = range(target['start'], target['end'] + 1)
        return
    
    def alloc_vq_core(self,target):
        target_num = target['end'] - target['start'] + 1

        for l_fd_irq_aff, l_fd_irq_aff_list in zip(self.ll_fd_irq_aff, self.ll_fd_irq_aff_list):

            #init param
            core = 0
            aff = 1
            max_aff = 1 << target_num 

            for fd_irq_aff,fd_irq_aff_list in zip(l_fd_irq_aff,l_fd_irq_aff_list):
                os.write(fd_irq_aff_list, core) 
                os.write(fd_irq_aff, f'{aff:x}')
                os.write(fd_irq_aff_list, core) 
                
                aff = (aff << 1) 
                core += 1

                if aff == max_aff:
                    aff = 1
                    core = 0

        #xps
        for i, fd in enumerate(self.l_fd_xps):
            if i < target_num:
                os.write(fd, self.HEX_CPUMASK_ALL)
            else:
                os.write(fd, '00'.encode())

        return
    