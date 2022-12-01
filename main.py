import sys
from env.env import Environment
from monitor.monitor import Monitor
from policy.vcoact import Vcoact
from vsock.vsock_hyp import VSockHYP
from actor.actor_hyp import ActorHyp
from tracer.tracer import Tracer
import time
import logging
from multiprocessing import Queue



numba_logger = logging.getLogger('numba')
numba_logger.setLevel(logging.WARNING)

sys.path.append("/home/caslab/vcoact")

env = Environment()

def run():
    global env
    q = Queue()
    monitor = Monitor(env,q)
    actor_hyp = ActorHyp(env)
    vsock_hyp = VSockHYP(env, monitor, actor_hyp,q)
    agent = Vcoact(env)
    tracer = None
    if env.is_tracer:
        tracer = Tracer(env, monitor)

    #init
    vsock_hyp.start()
    monitor.set_vsock(vsock_hyp)
    actor_hyp.set_vsock(vsock_hyp)

    itr = 0
    action = None

    # main loop
    if env.mode == 'vcoact':
        print('start vcoact mode')
    elif env.mode == 'monitor':
        print('start monitor mode')

    cur_core_alloc = env.get_cur_core()
    start_time = time.time()
    while True:
        #monitor
        monitor.start()
        start_time = time.time()
        time.sleep(env.period)
        end_time = time.time()
        monitor.end()

        if env.debug:
            print('total time: ',(end_time - start_time) * 1000 * 1000, "us")


        #get monitor result
        rst,p99 = monitor.get()

        #tracer
        if env.is_tracer:
            t = tracer.trace(rst, cur_core_alloc, p99)

        if env.mode == 'vcoact':
            #policy
            action = agent.step(rst)

            #act
            prev_core_alloc, cur_core_alloc = actor_hyp.act(action)
            
                
        
        #update th
        vm_th, pkt_th = tracer.get_th()
        agent.set_th(vm_th,pkt_th)

        itr += 1
           
    return None


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)