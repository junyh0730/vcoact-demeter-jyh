import subprocess
import os
from cgroupspy import trees

class CPUMonitor():
    def __init__(self):
        t = trees.Tree()
        cpuacct = t.get_node_by_path('/cpuacct')
        self.ctrl = cpuacct.controller
        self.start_usage_percpu = None
        self.env_usage_percpu = None
        return
    
    def start(self):
        #start record
        self.start_usage_percpu = self.ctrl.usage_percpu
        return
    
    def end(self):
        #end record
        self.end_usage_percpu = self.ctrl.usage_percpu
        return
    
    def get(self,diff_time):
        result = []        
        for start, end in zip(self.start_usage_percpu,self.end_usage_percpu):
            diff = end - start
            pctg = round(diff * 100 / diff_time, 3)
            result.append(pctg)

        return result