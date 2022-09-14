import sys
from env.env import Environment
from monitor.monitor import Monitor
from policy.vcoact import Vcoact
from vsock.vsock_hyp import VSockHYP
import time

sys.path.append("/home/caslab/vcoact")

env = Environment()

def run():
    global env
    agent = Vcoact(env)
    monitor = Monitor(env)
    vsock_hyp = VSockHYP(env)
    vsock_hyp.start()

    itr = 0

    # main loop
    while True:
        monitor.start()
        time.sleep(env.period)
        monitor.end()

        result = monitor.get()
        agent.step(result)

        itr += 1
        
    return


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)