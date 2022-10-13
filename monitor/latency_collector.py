from multiprocessing import Process, Queue
import socket


class LatCollector():
    def __init__(self, env):
        self.env = env
        self.slo = env.slo
        self.server_port = 9999 
        window_size = 100
        self.latency_queue = Queue(maxsize=window_size)
        self.latency_collector = Process(target=self.__latency_collect_daemon,
                                        args=(self.latency_queue,))
        self.latency_collector.deamon = True
        self.latency_collector.start()
    
    
    def getCurLatency(self):
        count = 0
        latency = 0
        while self.latency_queue.qsize():
            latency += self.latency_queue.get()
            count += 1

        if count > 0:
            latency = latency / count
            norm_latency = latency / self.slo
        else:
            norm_latency = -1
        
        return norm_latency

    def __latency_collect_daemon(self, latency_queue):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("ip: " + str(self.env.server_ip) + " port: " + str(self.server_port))
        server_socket.bind((self.env.server_ip, self.server_port))
        server_socket.listen()
        client_socket, addr = server_socket.accept()
        print('Connected by', addr,'for latency collection')

        while True:
            latency = 0.0
            # try:
            data = client_socket.recv(1024)
            data = str(data.decode())
            data = data.split(':')
            data = ' '.join(data).split()
            for latency in data:
                latency_queue.put(float(latency))

            # except:
            #    print('latnecy exception')
            #    latency = self.slo
            # print(float(data.decode()))
            # time.sleep(self.periode)

        client_socket.close()
        server_socket.close()
        sys.exit(0)