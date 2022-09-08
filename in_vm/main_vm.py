import sys
import time
sys.path.append("/home/caslab/vcoact")

from env.env import Environment
from in_vm.monitor.monitor_vm import MonitorVM
from in_vm.vsock_vm import VSockVM
from vsock.parser import Parser
from in_vm.actor_vm import ActorVM

env = Environment()

def run():
    global env
    actor = ActorVM(env)
    vsock_vm_daemon = VSockVM(actor)
    vsock_vm_daemon.start()
        
    main_loop(vsock_vm_daemon, actor)
        
    return


def main_loop(vsock_vm_daemon, actor):
    global env
    monitor_vm = MonitorVM(env)

    while True:
        monitor_vm.start()
        time.sleep(env.period)
        monitor_vm.end()

        #monitor
        rst = monitor_vm.get()
        
        #send info
        sendInfo(vsock_vm_daemon, rst)

        #alloc core 
        t_core, vq_core = alloc_policy(actor,rst)

    return

def alloc_policy(actor, rst):
    t_core, vq_core = actor.cur_t_core, actor.cur_vq_core

    #TODO: impl core allocation policy


    return t_core, vq_core

def sendInfo(vsock_vm_daemon, rst):
    l_rst_target = ["task", "vq"]
    for target, util in zip(l_rst_target,rst):
        #trans
        l_pkt = Parser.transInfoToPkt(target, util)

        #send
        for pkt in l_pkt:
            vsock_vm_daemon.send(pkt)
    
    return
    

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)