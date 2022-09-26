import sys
from env.env import Environment
from monitor.monitor import Monitor
from policy.vcoact import Vcoact
from vsock.vsock_hyp import VSockHYP
from actor.actor_hyp import ActorHyp
import time
import socket

sys.path.append("/home/caslab/vcoact")

env = Environment()

def run():
    global env
    monitor = Monitor(env)
    actor_hyp = ActorHyp(env)
    vsock_hyp = VSockHYP(env,monitor,actor_hyp)
    agent = Vcoact(env)

    vsock_hyp.start()
    monitor.set_vsock(vsock_hyp)
    actor_hyp.set_vsock(vsock_hyp)

    itr = 0

    # main loop
    if env.mode == 'vcoact':
        while True:
            #monitor
            monitor.start()
            time.sleep(env.period)
            monitor.end()

            #get monitor result
            result = monitor.get()

            #policy
            action = agent.step(result)

            #act
            actor_hyp.act(action)

            itr += 1
    
    elif env.mode == 'monitor':
        print('start monitor mode')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((env.server_ip, 9995))
        s.listen()
        while True:
            conn, addr = s.accept()

            try:
                data = conn.recv(2048)
            except socket.error:
                break

            e = data.decode('utf-8')

            if e == 'start':
                #start monitor
                if env.debug:
                    print("start monitor")
                monitor.start()
                continue

            elif e == 'end':
                #end monitor
                if env.debug:
                    print("end monitor")
                monitor.end()
                monitor.get()
        
    return


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)