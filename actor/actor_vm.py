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

        self.__open_fd_xps()

        self.__init_actor()
        return
    
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
    
    def __init_actor(self):
        self.alloc_t_core(self.cur_t_core)
        self.alloc_vq_core(self.cur_vq_core)
        return
    
    def alloc_t_core(self,target):
        return
    
    def alloc_vq_core(self,target):
        num = target['end'] - target['start'] + 1

        #TODO: irq remmap

        #xps
        for i, fd in enumerate(self.l_fd_xps):
            if i < num:
                os.write(fd, self.HEX_CPUMASK_ALL)
            else:
                os.write(fd, '00'.encode())

        return
    