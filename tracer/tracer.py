import socket 
import threading
import multiprocessing
import logging
import numpy as np

class Tracer():
    def __init__(self,env,monitor):
        self.env = env
        self.monitor = monitor
        self.is_running = False
        self.itr = 0
        self.l_rst = list()
        self.l_action = list()
        self.start_engy = -1
        self.end_engy = -1

        #init logger
        #create logger instance
        self.logger = logging.getLogger(__name__)

        #create handler
        streamHandler = logging.StreamHandler()
        fileHandler = logging.FileHandler('./monitor.log')

        #add handler to logger
        self.logger.addHandler(streamHandler)
        self.logger.addHandler(fileHandler)
        self.logger.setLevel(level=logging.INFO)

        self.reset()    
        self.run()
    
    def trace(self, rst, action):
        if self.is_running == False:
            return
        
        if action == None:
            action = self.env.get_cur_core()

        self.itr += 1
        self.l_rst.append(rst)
        self.l_action.append(action)
    
    def reset(self):
        self.is_running = False
        self.itr = 0
        self.l_rst = list()
        self.l_action = list()
        self.start_engy = -1
        self.end_engy = -1
        self.__clear_logfile()

    def run(self):
        thread = threading.Thread(target=self.__run_tracer_deamon)
        thread.daemon = True
        thread.start()

    def __run_tracer_deamon(self):
        #connect socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.env.server_ip, 9995))
        s.listen()

        while True:
            conn, addr = s.accept()

            try:
                data = conn.recv(2048)
            except socket.error:
                break

            e = data.decode('utf-8')

            #start monitor
            if e == 'start':
                self.reset()
                self.is_running = True
                self.start_engy = self.monitor.read_engy()
                if self.env.debug:
                    print("start monitor")

            #end monitor
            elif e == 'end':
                self.is_running = False
                self.end_engy = self.monitor.read_engy()
                if self.env.debug:
                    print("end monitor")
                
                stat = self.__cal_stat()
                self.__write_log(stat)
    
    def __write_log(self, stat):
        l_str = ["avg_vm_num", "avg_pkt_num",
                 "avg_vm_util", "avg_pkt_util", "engy"]
        for string, s in zip(l_str, stat):  
            self.logger.info((string +": " + str(s)).format())
        
        return None

    
    def __cal_stat(self):
        accu = [0,0,0,0]
        for action, rst in zip(self.l_action, self.l_rst):
            #accu core_num
            [vhost_core,hq_core,vq_core,vm_core,t_core] = action
            vm_core_num = vm_core['end'] - vm_core['start'] + 1
            pkt_core_num = hq_core['end'] - hq_core['start'] + 1

            accu[0] += vm_core_num
            accu[1] += pkt_core_num

            #accu util
            #[hqm_rst, cpum_rst] = rst
            cur_vm_core = self.env.cur_vm_core['start']
            cur_hq_core = self.env.cur_hq_core['end'] + 1

            arr_vm = np.split(rst, [cur_vm_core])[1]
            arr_pkt = np.split(rst, [cur_hq_core])[0]

            vm_util = np.average(arr_vm)
            pkt_util = np.average(arr_pkt)

            accu[2] += vm_util
            accu[3] += pkt_util

        # cal avg_core_num and avg_util
        avg_vm_num = round(accu[0] / self.itr,1)
        avg_pkt_num = round(accu[1] / self.itr,1)
        avg_vm_util = round(accu[2] / self.itr,2)
        avg_pkt_util = round(accu[3] / self.itr,2)

        #cal engy
        MAX_LIMIT_ENGY_VAL = 4294967296
        engy = self.end_engy - self.start_engy
        engy = (engy + MAX_LIMIT_ENGY_VAL) % MAX_LIMIT_ENGY_VAL

        stat = [avg_vm_num, avg_pkt_num, avg_vm_util, avg_pkt_util, engy]

        return stat
    
    def __clear_logfile(self):
        f = open("./monitor.log", "a") # Create a blank file
        f.seek(0)  # sets  point at the beginning of the file
        f.truncate()  # Clear previous content
        f.close()  # Close file

        


