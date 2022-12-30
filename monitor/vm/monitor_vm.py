import time
from monitor.vm.task_monitor_vm import TaskMonitorVM
from monitor.vm.traffic_monitor_vm import TrafficMonitor
from monitor.vm.wait_monitor_vm import WaitMonitor
#from monitor.vm.vq_monitor_vm import VQMonitorVM 
import threading

class MonitorVM():
    def __init__(self,env,start_e=None,end_e=None):
        self.env = env

        self.start_time = -1
        self.end_time = -1

        self.tm_vm = TaskMonitorVM(env)
        self.traffic_vm = TrafficMonitor(env)
        #self.wait_vm = WaitMonitor(env)
        #self.vqm_vm = VQMonitorVM(env)

        self.start_e = start_e
        self.end_e = end_e

        return
    
    def start(self):
        self.start_time = time.time()
        self.tm_vm.start()
        self.traffic_vm.start()
        #self.wait_vm.start()
        #self.vqm_vm.start()
        return
    
    def end(self):
        self.tm_vm.end()
        self.traffic_vm.end()
        #self.wait_vm.end()
        #self.vqm_vm.end()
        self.end_time = time.time()
        return
    
    def get(self):
        rst = None
        diff_time = (self.end_time - self.start_time) * 1000 * 1000 * 1000  #ns

        tm_vm_rst = self.tm_vm.get(diff_time)
        traffic_vm = self.traffic_vm.get(diff_time)
        # wait_time = self.wait_vm.get(diff_time)
        #vqm_vm_rst = self.vqm_vm.get(diff_time)

        #rst = [tm_vm_rst, vqm_vm_rst]
        return tm_vm_rst, traffic_vm # , wait_time
    
    def get_e(self):
        return self.start_e, self.end_e
    
