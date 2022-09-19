import time
import logging
from monitor.hq_monitor import HQMonitor
from monitor.cpu_monitor import CPUMonitor

class Monitor():
    def __init__(self,env):
        self.env = env
        self.start_time = -1
        self.end_time = -1
        self.hqm = HQMonitor(env)
        self.cpum = CPUMonitor(env)

        logging.basicConfig(filename='./monitor.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        return
    
    
    def start(self):
        self.start_time = time.time()
        #start record
        self.hqm.start()
        self.cpum.start()
        return
    
    def end(self):
        #end record
        self.hqm.end()
        self.cpum.end()
        self.end_time = time.time()
        return
    
    def get(self):
        rst = None
        diff_time = (self.end_time - self.start_time) * 1000 * 1000 * 1000  #ns
        hqm_rst = self.hqm.get(diff_time)
        cpum_rst = self.cpum.get(diff_time)
        
        rst = [hqm_rst, cpum_rst]

        if self.env.debug:
            #self.logger.info("diff_time : " + str(diff_time))
            m_str=["hq", 'pcpu']
            for target, l_r in zip(m_str, rst):
                for i,r in enumerate(l_r): 
                    strings = 'info '+str(target)+ ' ' +str(i) + ' ' +str(r)
                    self.logger.info(strings)

        return rst
    
    def set_info(self,target,core_num,util):
        if self.env.debug:
            strings = 'info '+str(target)+ ' ' +str(core_num) + ' ' +str(util)
            self.logger.info(strings)
        
        return