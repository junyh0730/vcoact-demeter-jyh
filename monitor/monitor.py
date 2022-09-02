import time
from monitor.task_monitor import TaskMonitor
from monitor.hq_monitor import HQMonitor
from monitor.vq_monitor import VQMonitor
from monitor.cpu_monitor import CPUMonitor

class Monitor():
    def __init__(self,env):
        self.env = env

        self.start_time = -1
        self.end_time = -1
        self.taskm = TaskMonitor(env)
        self.hqm = HQMonitor(env)
        self.vqm = VQMonitor(env)
        self.cpum = CPUMonitor(env)
        return
    
    
    def start(self):
        self.start_time = time.time()
        #start record
        self.taskm.start()
        self.hqm.start()
        self.vqm.start()
        self.cpum.start()
        return
    
    def end(self):
        #end record
        self.taskm.end()
        self.hqm.end()
        self.vqm.end()
        self.cpum.end()
        self.end_time = time.time()
        return
    
    def get(self):
        rst = None
        diff_time = (self.end_time - self.start_time) * 1000 * 1000 * 1000  #ns
        taskm_rst = self.taskm.get()
        hqm_rst = self.hqm.get(diff_time)
        vqm_rst = self.vqm.get()
        cpum_rst = self.cpum.get(diff_time)
        
        rst = [taskm_rst, hqm_rst, vqm_rst, cpum_rst]

        if self.env.debug:
            print("monitor")
            print("diff_time : ", diff_time)
            m_str=["taskm", "hqm", "vqm", 'cpum']
            for s, r in zip(m_str,rst):
                print(s)
                print(r)

        return rst