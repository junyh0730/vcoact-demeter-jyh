import time
import os, struct
from monitor.hq_monitor import HQMonitor
from monitor.cpu_monitor import CPUMonitor
from monitor.latency_collector import LatCollector

class Monitor():
    def __init__(self,env):
        self.env = env
        self.start_time = -1
        self.end_time = -1
        self.hqm = HQMonitor(env)
        self.cpum = CPUMonitor(env)
        self.latency_collector = LatCollector(env)
        self.vsock = None
        return
    
    
    def start(self):
        self.start_time = time.time()

        #start record
        self.__send_start_sig()
        #self.hqm.start()
        self.cpum.start()
        return

    
    def end(self):
        #end record
        self.__send_end_sig()
        #self.hqm.end()
        self.cpum.end()
        self.end_time = time.time()
        return
    
    def get(self):
        rst = None
        diff_time = (self.end_time - self.start_time) * 1000 * 1000 * 1000  #ns
        #hqm_rst = self.hqm.get(diff_time)
        cpum_rst = self.cpum.get(diff_time)
        p99 = self.latency_collector.getCurLatency()

        #rst = [hqm_rst, cpum_rst]
        
        if self.env.debug:
            print("monitor diff_time: ",diff_time)

        """
        if self.env.mode == 'monitor':
            self.logger.info("info diff_time " + str(diff_time / 1000/ 1000/ 1000) + ' s')
            m_str=["hq", 'pcpu']
            for target, l_r in zip(m_str, rst):
                for i,r in enumerate(l_r): 
                    strings = 'info '+str(target)+ ' ' +str(i) + ' ' +str(r)
                    self.logger.info(strings)
        """

        return cpum_rst,p99
    
    def __get_raw(self):
        cur_time = time.time()
        l_start_idle, l_start_non_idle = self.cpum.get_raw()
        softirq_usage = self.hqm.get_raw()
        cur_engy = self.read_engy()
        rst = [cur_time,l_start_idle,l_start_non_idle,softirq_usage,cur_engy]
        return rst
    
    """
    def start_rec(self):
        self.rec_start_rst = self.__get_raw()
    
    def end_rec(self):
        self.rec_end_rst = self.__get_raw()

    def get_rec(self):
        diff_time = self.rec_end_rst[0] - self.rec_start_rst[0]
        engy = self.rec_end_rst[4] - self.rec_start_rst[4]
        avg_core_num = None

        l_pcpu_util = []
        l_softirq_util = []

        for i in range(len(self.rec_end_rst)):
            #cal pcpu_util
            idle = self.rec_end_rst[1][i] - self.rec_start_rst[1][i]
            non_idle = self.rec_end_rst[2][i] - self.rec_start_rst[2][i]
            total = non_idle + idle
            pcpu_util = round(non_idle * 100.0 / total, 3)
            l_pcpu_util.append(pcpu_util)

            #cal softirq_util
            softirq = round(
                (self.rec_end_rst[3][i] - self.rec_start_rst[3][i]) * 100.0 / diff_time, 3)
            l_softirq_util.append(softirq)
    """
    
    def __send_start_sig(self):
        strings = "".join(["act ", "start ", "-1 ", "-1 "])
        pkt = strings.encode('utf-8')
        print('send_start_sig: ',pkt)
        self.vsock.send(pkt)

    def __send_end_sig(self):
        strings = "".join(["act ", "end ", "-1 ", "-1 "])
        pkt = strings.encode('utf-8')
        print('send_end_sig: ',pkt)
        self.vsock.send(pkt)
    
    
    def set_info(self,target,core_num,util):
        if self.env.debug:
            strings = 'info '+str(target)+ ' ' +str(core_num) + ' ' +str(util)
            self.logger.info(strings)
        strings = 'info '+str(target)+ ' ' +str(core_num) + ' ' +str(util)
        print(strings)
        return

    def set_vsock(self,vsock):
        self.vsock = vsock
    
    def read_engy(self,msr="1553",cpu=0):
        f = os.open('/dev/cpu/%d/msr' % (cpu,), os.O_RDONLY)
        os.lseek(f, int(msr), os.SEEK_SET)
        val = struct.unpack('Q', os.read(f, 8))[0]
        os.close(f)
        return val