from cgroupspy import trees
import subprocess
import os

class ActorVM():
    def __init__(self,env):
        self.env = env

        x=(1<<self.env.max_core) - 1
        self.HEX_CPUMASK_ALL = f'{x:x}'.encode('utf-8') 

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
            grep_cmd = "cat /proc/interrupts | grep " + str(name) + " | awk -F: '{print $1}'"
            irqs = subprocess.check_output(grep_cmd,shell=True)
            l_irq = irqs.decode('utf-8').split()

            l_fd_irq_aff = list()
            l_fd_irq_aff_list = list()

            for irq in l_irq:
                fd_irq_aff = os.open("/proc/irq/"+str(irq)+"/smp_affinity", os.O_RDWR)
                fd_irq_aff_list = os.open("/proc/irq/"+str(irq)+"/smp_affinity_list", os.O_RDWR)

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
                                 "/queues/tx-" + str(core) + "/xps_cpus", os.O_RDWR)
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
        self.alloc_t_core(self.env.cur_t_core)
        self.alloc_vq_core(self.env.cur_vq_core)
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

            for cpu_id, [fd_irq_aff,fd_irq_aff_list] in enumerate(zip(l_fd_irq_aff,l_fd_irq_aff_list)):
                os.write(fd_irq_aff_list, str(core).encode('utf-8'))
                os.write(fd_irq_aff, f'{aff:x}'.encode('utf-8'))
                os.write(fd_irq_aff_list, str(core).encode('utf-8')) 
                
                aff = (aff << 1) 
                core += 1

                if aff == max_aff:
                    aff = 1
                    core = 0

                if self.env.debug:
                    try:
                        print("IRQ ","cpuid: ", cpu_id," aff_list: ",os.read(fd_irq_aff_list,100).decode('utf-8'))
                        print("IRQ ","cpuid: ", cpu_id," aff: ",os.read(fd_irq_aff,100).decode('utf-8'))
                    except:
                        pass

        #xps
        for i, fd in enumerate(self.l_fd_xps):
            if i < target_num:
                os.write(fd, self.HEX_CPUMASK_ALL)
            else:
                os.write(fd, '00'.encode())

            if self.env.debug:
                try:
                    print("XPS ", "cpuid: ", i ," aff: " ,os.read(fd,100).decode('utf-8'))
                except:
                    pass

        return
    
