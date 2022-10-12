import sys
import multiprocessing
import time
sys.path.append("/home/vm/vcoact")

from env.env import Environment
from monitor.vm.monitor_vm import MonitorVM
from vsock.vsock_vm import VSockVM
from vsock.parser import Parser
from actor.actor_vm import ActorVM

env = Environment()
start_e = multiprocessing.Event()
end_e = multiprocessing.Event()

def run():
    global env,start_e,end_e
    actor = ActorVM(env)
    vsock_vm_daemon = VSockVM(actor,env,start_e,end_e)
    vsock_vm_daemon.start()
        
    main_loop(vsock_vm_daemon, actor)
        
    return


def main_loop(vsock_vm_daemon, actor):
    global env,start_e,end_e
    monitor_vm = MonitorVM(env,start_e,end_e)

    if env.mode == 'vcoact':
        while True:
            None
            #monitor_vm.start()
            #time.sleep(env.period)
            #monitor_vm.end()

            #monitor
            #rst = monitor_vm.get()
            
            #send info
            #sendInfo(vsock_vm_daemon, rst)

            #alloc core 
            #t_core, vq_core = alloc_policy(actor,rst)

    elif env.mode == 'monitor':
        #init
        #start_e, end_e = monitor_vm.get_e()
        #vsock_vm_daemon.set_e(start_e,end_e)

        while True:
            #wait start signal from hyp
            print("wait start event")
            start_e.wait()

            #start 
            monitor_vm.start()

            #wait end signal from hyp
            print("wait end event")
            end_e.wait()

            #end
            monitor_vm.end()
            
            #send info
            rst = monitor_vm.get()
            sendInfo(vsock_vm_daemon, rst)
            print("send info")

            start_e.clear()
            end_e.clear()

    return

def alloc_policy(actor, rst):
    t_core, vq_core = actor.cur_t_core, actor.cur_vq_core

    #TODO: impl core allocation policy


    return t_core, vq_core

def sendInfo(vsock_vm_daemon, rst):
    l_rst_target = ["task", "vq"]
    for target, util in zip(l_rst_target,rst):
        #trans
        pkt = Parser.transInfoToPkt(target, util)

        #send
        vsock_vm_daemon.send(pkt)
    
    return
    

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
