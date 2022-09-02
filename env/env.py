import multiprocessing

class Environment():
    def __init__(self):
        self.max_core = multiprocessing.cpu_count()
        self.netinf_name = "enp101s0f0"
        self.server_ip = "10.150.21.215"

        self.debug = True
        self.period = 0.1 #s