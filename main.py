import sys
from env.env import Environment
from monitor.monitor import Monitor
from policy.vcoact import Vcoact
from vsock.vsock_hyp import VSockHYP
from actor.actor_hyp import ActorHyp
import time

sys.path.append("/home/caslab/vcoact")

env = Environment()

def run():
    global env
    monitor = Monitor(env)
    actor_hyp = ActorHyp(env)
    vsock_hyp = VSockHYP(env,monitor,actor_hyp)
    agent = Vcoact(env)

    vsock_hyp.start()

    itr = 0

    # main loop
    while True:
        monitor.start()
        time.sleep(env.period)
        monitor.end()

        result = monitor.get()

        if env.mode == "vcoact":
            action = agent.step(result)
            actor_hyp.act(action)

        elif env.mode == "monitor":
            pass

        itr += 1
    
    return


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)