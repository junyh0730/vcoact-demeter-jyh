import sys
import multiprocessing
import time
sys.path.append("/home/vm/vcoact-demeter/vcoact")

from env.env import Environment
from monitor.vm.monitor_vm import MonitorVM
#from vsock.vsock_vm import VSockVM
from vsock.vsock_vm_be import VSockVM
from vsock.parser import Parser
from actor.actor_vm import ActorVM

env = Environment()
start_e = multiprocessing.Event()
end_e = multiprocessing.Event()

def run():
    global env,start_e,end_e
    print("start vsock_vm_daemon = VSockVM(actor,env,start_e,end_e)!!!")

    actor = ActorVM(env)
    print("start vsock_vm_daemon = VSockVM(actor,env,start_e,end_e)!!!")
    vsock_vm_daemon = VSockVM(actor,env,start_e,end_e)
    print("start vsock_vm_daemon.start()!!!")
    vsock_vm_daemon.start()
    
    print("start main loop!!!")
        
    main_loop(vsock_vm_daemon, actor)
        
    return


def main_loop(vsock_vm_daemon, actor):
    global env,start_e,end_e
    monitor_vm = MonitorVM(env,start_e,end_e)

    if env.mode == 'vcoact':
        while True:
            #None
            #monitor_vm.start()
            time.sleep(env.period)
            #monitor_vm.end()

            #monitor
            #rst = monitor_vm.get()
            
            #send info
            #sendInfo(vsock_vm_daemon, rst)

            #alloc core 
            #t_core, vq_core = alloc_policy(actor,rst)

    elif env.mode == 'demeter':
        start_e.clear()
        end_e.clear()
        while True:
            
            start_e.wait()
            start_e.clear()

            #start 
            monitor_vm.start()

            time.sleep(env.period)
            #wait end signal from hyp
            #print("wait end event")
            end_e.wait()
            end_e.clear()

            #end
            monitor_vm.end()
            
            #send info
            # rst, traffic, wait_time = monitor_vm.get()
            rst, traffic = monitor_vm.get()
            #sendInfo(vsock_vm_daemon, rst)
            #sendInfo_traffic(vsock_vm_daemon, traffic)
            #sendInfo_traffic(vsock_vm_daemon, wait_time)
            #print("send info")
            #sendInfo(vsock_vm_daemon, rst)
            #sendInfo_traffic(vsock_vm_daemon, traffic)
    
    elif env.mode == 'monitor':
        #init
        #start_e, end_e = monitor_vm.get_e()
        #vsock_vm_daemon.set_e(start_e,end_e)

        start_e.clear()
        end_e.clear()

        while True:
            #wait start signal from hyp
            #print("wait start event")
            start_e.wait()
            start_e.clear()

            #start 
            monitor_vm.start()

            #wait end signal from hyp
            #print("wait end event")
            end_e.wait()
            end_e.clear()

            #end
            monitor_vm.end()
            
            #send info
            # rst, traffic, wait_time = monitor_vm.get()
            rst, traffic = monitor_vm.get()
            sendInfo(vsock_vm_daemon, rst)
            sendInfo_traffic(vsock_vm_daemon, traffic)
            print("send info")


    return


def sendInfo(vsock_vm_daemon, rst):
    rst_target = "task"
    #trans
    pkt = Parser.transInfoToPkt(rst_target, rst.tolist())
    #print(pkt)
    
    #send
    vsock_vm_daemon.send(pkt)
    
    return

def sendInfo_traffic(vsock_vm_daemon, rst):
    rst_target = "task"
    #trans
    pkt = Parser.transTrafficToPkt(rst_target, rst)
    #print(pkt)
    
    #send
    vsock_vm_daemon.send(pkt)
    
    return
    
    

if __name__ == "__main__":
    try:
        print("start run!!!")
        run()
    except KeyboardInterrupt:
        sys.exit(0)
