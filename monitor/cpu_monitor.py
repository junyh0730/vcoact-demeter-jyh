import subprocess
import os,re
from cgroupspy import trees

class CPUMonitor():
    def __init__(self,env):
        t = trees.Tree()
        cpuacct = t.get_node_by_path('/cpuacct')
        self.ctrl = cpuacct.controller
        self.start_usage_percpu = None
        self.env_usage_percpu = None

        self.fd_stat = os.open('/proc/stat', os.O_RDONLY)

        self.l_start_idle = None
        self.l_end_idle = None
        self.l_start_non_idle = None
        self.l_end_non_idle = None
        return
    
    def start(self):
        #start record
        #self.start_usage_percpu = self.ctrl.usage_percpu
        self.l_start_idle, self.l_start_non_idle = self.__read_stat()
        return
    
    def end(self):
        #end record
        #self.end_usage_percpu = self.ctrl.usage_percpu
        self.l_end_idle, self.l_end_non_idle = self.__read_stat()
        return
    
    def get(self,diff_time):
        result = []        
        """
        for start, end in zip(self.start_usage_percpu,self.end_usage_percpu):
            diff = end - start
            pctg = round(diff * 100 / diff_time, 3)
            result.append(pctg)
        """
    
        for start_idle, end_idle, start_non_idle, end_non_idle \
            in zip(self.l_start_idle, self.l_end_idle, \
                self.l_start_non_idle, self.l_end_non_idle):

            non_idle_time = end_non_idle - start_non_idle
            idle_time = end_idle - start_idle
            total = non_idle_time + idle_time
            pctg = round(non_idle_time * 100 / total, 3)
            result.append(pctg)

        return result
    
    def __read_stat(self):
        l_idle = list()
        l_non_idle = list()
        """
        cpu : user nice system idle iowait irq softirq steal guest guest_nice
        cpu0 : ...
        idle_time = idle + iowait
        non_idle_time = user + nice + system + irq + softirq + steal
        total = idle_time + non_idle_time
        previous_total = previous_idle + previous_non_idle
        current_total = current_idle + current_non_idle
        diff_total = current_total - previous_total
        diff_idle = current_idle - previous_idle
        cpu_usage_percentage = ( diff_total - diff_idle )/ diff_total * 100
        """
        os.lseek(self.fd_stat, 0, 0)
        lines = os.read(self.fd_stat, 2000)
        lines = str(lines.decode())
        lines = lines.split("\n")
        

        for line in lines:
            if line.startswith("cpu"):
                stat = re.split("\s+", line.strip())[:11]
                cpu = stat[0]
                user, nice, sys, idle, iowait, irq, softirq, steal, guest, guest_nice = map(
                    int, stat[1:])

                if cpu == 'cpu':
                    continue

                idle_time = idle + iowait
                non_idle_time = user + nice + sys + irq + softirq + steal
                l_idle.append(idle_time)
                l_non_idle.append(non_idle_time)

        return l_idle, l_non_idle


       