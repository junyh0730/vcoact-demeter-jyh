import time
from monitor.task_monitor import TaskMonitor
from monitor.hq_monitor import HQMonitor
from monitor.vq_monitor import VQMonitor
from monitor.vcpu_monitor import VCPUMonitor

class Monitor():
    def __init__(self,env):
        self.start_time = -1
        self.end_time = -1
        self.taskm = TaskMonitor()
        self.hqm = HQMonitor()
        self.vqm = VQMonitor()
        self.vcpum = VCPUMonitor()
        return
    
    
    def start(self):
        self.start_time = time.time()
        #start record
        self.taskm.start()
        self.hqm.start()
        self.vqm.start()
        self.vcpum.start()
        return
    
    def end(self):
        self.end_time = time.time()
        #end record
        self.taskm.end()
        self.hqm.end()
        self.vqm.end()
        self.vcpum.end()
        return
    
    def get(self):
        rst = None
        diff_time = self.end_time - self.start_time #s
        taskm_rst = self.taskm.get()
        hqm_rst = self.hqm.get()
        vqm_rst = self.vqm.get()
        vcpum_rst = self.vcpum.get()
        
        rst = [taskm_rst, hqm_rst, vqm_rst, vcpum_rst]

        return rst