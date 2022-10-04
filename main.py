import sys
from env.env import Environment
from monitor.monitor import Monitor
from policy.vcoact import Vcoact
from vsock.vsock_hyp import VSockHYP
from actor.actor_hyp import ActorHyp
from tracer.tracer import Tracer
import time

sys.path.append("/home/caslab/vcoact")

env = Environment()

def run():
    global env
    monitor = Monitor(env)
    actor_hyp = ActorHyp(env)
    vsock_hyp = VSockHYP(env, monitor, actor_hyp)
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


    while True:
        #monitor
        monitor.start()
        time.sleep(env.period)
        monitor.end()

        #get monitor result
        result = monitor.get()

        if env.mode == 'vcoact':
            #policy
            action = agent.step(result)

            #act
            actor_hyp.act(action)

        #tracer
        if env.is_tracer:
            tracer.trace(result, action)

        itr += 1
           
    return


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)