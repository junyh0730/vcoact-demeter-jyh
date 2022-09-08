import sys
import time
sys.path.append("/home/caslab/vcoact")

from env.env import Environment
from in_vm.monitor.monitor_vm import MonitorVM
from in_vm.vsock_vm import VSockVM

env = Environment()

def run():
    global env
    monitor_vm = MonitorVM(env)
    vsock_vm_daemon = VSockVM()

    vsock_vm_daemon.start()

    itr = 0
    # main loop
    while True:
        monitor_vm.start()
        time.sleep(env.period)
        monitor_vm.end()

        #monitor
        rst = monitor_vm.get()
        
        #trans

        #core alloc.
        
        #send info

        itr += 1
        
    return

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)