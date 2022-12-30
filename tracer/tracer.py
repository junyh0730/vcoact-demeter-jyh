import socket 
import threading
import multiprocessing
import logging
import numpy as np
import pandas as pd
from numba import jit
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from mlxtend.plotting import plot_decision_regions
from bayes_opt import BayesianOptimization, UtilityFunction
from th_finder.th_finder import ThFinder


@jit(nopython=True, cache=True)
def cal_util(cpu_rst, vcpu_rst, cur_lc_vcpu_core, cur_hq_core):
    vm_util = float(-1)
    vm_util_if_dec = float(-1)
    pkt_util = float(-1)
    pkt_util_if_dec = float(-1)

    arr_vm = np.split(vcpu_rst, [cur_lc_vcpu_core])[0]
    arr_pkt = np.split(cpu_rst, [cur_hq_core])[0]

    vm_util = np.average(arr_vm)
    pkt_util = np.average(arr_pkt)

    if len(arr_vm) != 1:
        vm_util_if_dec = np.sum(arr_vm)/(len(arr_vm) - 1)
    if len(arr_pkt) != 1:
        pkt_util_if_dec = np.sum(arr_pkt)/(len(arr_pkt) - 1)

    return vm_util, vm_util_if_dec, pkt_util, pkt_util_if_dec

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

        self.th_weight = 0.7

        self.explorer_th = 50

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

        #dataframe
        self.key = ["prev_lc_vcpu_core", "prev_pkt_core", "prev_vm_util",
                    "prev_pkt_util", "lc_vcpu_core", "pkt_core", "vm_util", "pkt_util", "p99"]
        self.df = pd.DataFrame(columns=self.key)

        #th
        self.vm_th = 90
        self.pkt_th = 90

        #prev
        self.prev_core_alloc = None
        self.prev_util = None

        self.slo_vio_count = 0

        self.optimizer = BayesianOptimization(f=None,
                                         pbounds={"vm_th": [1, 99],
                                                  "pkt_th": [1, 99]},
                                         verbose=2, random_state=1234)
        self.utility = UtilityFunction(kind = "ucb", kappa = 1.96, xi = 0.01)

        #self.th_finder = ThFinder(self.env.slo)


        self.reset()    
        self.run()
    
    def trace(self, rst, cur_core_alloc, p99):
        if self.is_running == False:
            return False

        if p99 <= 0:
            return False

        if p99 > self.env.slo:
            self.slo_vio_count += 1

        self.itr += 1
        self.l_rst.append(rst)
        self.l_action.append(cur_core_alloc)

        [prev_vhost_core, prev_hq_core, prev_vq_core,
            prev_lc_vcpu_core, prev_t_core] = cur_core_alloc
        lc_vcpu_core_num = prev_lc_vcpu_core['start']
        pkt_core_num = prev_hq_core['end'] + 1
        cpu_rst,vcpu_rst = rst
        vm_util, temp, pkt_util, temp = cal_util(cpu_rst,vcpu_rst, lc_vcpu_core_num, pkt_core_num)


        if self.prev_util != None:
            self.df.loc[len(self.df)] = [*self.prev_core_alloc, *self.prev_util,
                                         lc_vcpu_core_num, pkt_core_num, vm_util, pkt_util, p99]

        self.prev_core_alloc = [lc_vcpu_core_num,pkt_core_num]
        self.prev_util = [vm_util,pkt_util]

        if len(self.df) > self.explorer_th:
            thread = threading.Thread(target=self.__th_finder_thread)
            thread.daemon = True
            thread.start()
            

        
        return True
    
    def __th_finder_thread(self):
        self.vm_th, self.pkt_th = self.th_finder.cal_th(self.df, self.vm_th,self.pkt_th,self.th_weight)
        #self.vm_th = self.th_weight * self.vm_th + (1-self.th_weight) * vm_th
        #self.pkt_th = self.th_weight * self.pkt_th + (1-self.th_weight) * pkt_th


        print("weighted vm th: ", self.vm_th, "weighted pkt th: ", self.pkt_th)

        self.df = pd.DataFrame(columns=self.key)
        return 

    
    def reset(self):
        self.is_running = False
        self.itr = 0
        self.l_rst = list()
        self.l_action = list()
        self.start_engy = -1
        self.end_engy = -1
        self.slo_vio_count = 0
        self.__clear_logfile()

        #self.df = pd.DataFrame(columns=self.key)


    def run(self):
        thread = threading.Thread(target=self.__run_tracer_deamon)
        thread.daemon = True
        thread.start()
    
    def get_th(self):
        return self.vm_th, self.pkt_th

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

                #self.df.to_csv("df.csv")
                            

    def __write_log(self, stat):
        l_str = ["avg_vm_num", "avg_pkt_num",
                 "avg_vm_util", "avg_pkt_util", "engy"]
        for string, s in zip(l_str, stat):  
            self.logger.info((string +": " + str(s)).format())
        
        return None
    
    """
    def __cal_th(self,stat):
        
        target = self.__obj_func(stat)
        cur_th = {'vm_th': self.vm_th, 'pkt_th': self.pkt_th}
        try:
            self.optimizer.register(params = cur_th, target = target)
        except KeyError:
            print("same point")
            pass
        #update
        next_th = self.optimizer.suggest(self.utility)
        next_th['vm_th'] = int(next_th['vm_th'])
        next_th['pkt_th'] = int(next_th['pkt_th'])
        self.vm_th = next_th['vm_th']
        self.pkt_th = next_th['pkt_th']
        print("vm th: ", self.vm_th, "pkt th: ", self.pkt_th)
    
    def __obj_func(self,stat):
        alpha = 0.5
        target = 0
        total_guart_pctg = 1 - (self.slo_vio_count * 1.0 / self.itr)
        print("slo guart. pctg: ", total_guart_pctg)
        [avg_vm_num, avg_pkt_num, avg_vm_util, avg_pkt_util, engy] = stat
        target = alpha * total_guart_pctg + \
            (1-alpha) * (avg_vm_util + avg_pkt_util) / 200
        print("obj score: ", target)
        return target
    """

    

    def __cal_stat(self):
        accu = [0,0,0,0]
        for action, rst in zip(self.l_action, self.l_rst):
            #accu core_num
            [vhost_core,hq_core,vq_core,lc_vcpu_core,t_core] = action
            lc_vcpu_core_num = lc_vcpu_core['end'] - lc_vcpu_core['start'] + 1
            pkt_core_num = hq_core['end'] - hq_core['start'] + 1

            accu[0] += lc_vcpu_core_num
            accu[1] += pkt_core_num

            #accu util
            #[hqm_rst, cpum_rst] = rst
            cur_lc_vcpu_core = lc_vcpu_core_num
            cur_hq_core = self.env.cur_hq_core['end'] + 1

            cpu_util, vcpu_util = rst
            arr_vm = np.split(vcpu_util, [cur_lc_vcpu_core])[0]
            arr_pkt = np.split(cpu_util, [cur_hq_core])[0]

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

        #logger 
        if self.env.mode == 'monitor':
            itr = 0
            l_acc_cpu = self.env.max_core * [0]
            l_acc_vcpu = self.env.max_core * [0]
            for rst in self.l_rst: 
                cpu, vcpu = rst
                for i in range(self.env.max_core):
                    l_acc_vcpu[i] += vcpu[i]
                    l_acc_cpu[i] += cpu[i]
                itr += 1

            for i in range(self.env.max_core):
                avg_vcpu_util = l_acc_vcpu[i] / itr
                strings = 'info vcpu '+str(i) + ' ' +str(avg_vcpu_util)
                self.logger.info(strings)


            for i in range(self.env.max_core):
                avg_cpu_util = l_acc_cpu[i] / itr
                strings = 'info pcpu '+str(i) + ' ' +str(avg_cpu_util)
                self.logger.info(strings)

        return stat
    
    
   
    
    def __clear_logfile(self):
        f = open("./monitor.log", "a") # Create a blank file
        f.seek(0)  # sets  point at the beginning of the file
        f.truncate()  # Clear previous content
        f.close()  # Close file
    
    def __plot(self,pearson_corr):
        #plot 
        """
        plot = sns.heatmap(pearson_corr,
                            xticklabels=pearson_corr.columns,
                            yticklabels=pearson_corr.columns,
                            cmap='RdBu_r',
                            annot=True,
                            linewidth=0.5)
        plot.figure.savefig("pearson_corr.png")
        plt.clf()
        """

        sns.set(style = "darkgrid")

        fig = plt.figure()
        ax = fig.add_subplot(111,projection = '3d')

        x = self.df['vm_util']
        y = self.df['pkt_util']
        z = self.df['p99']

        ax.set_xlabel("VM Util.")
        ax.set_ylabel("Packet Processing Util.")
        ax.set_zlabel("99th Percentile Latency (ms)")

        ax.scatter(x,y,z, c=z, marker='o')
        
        plt.savefig("util.png")

        
        


