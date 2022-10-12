from multiprocessing import Process, Queue
import socket


class LatCollector():
    def __init__(self, env):
        self.server_port = 9999 
        self.latency_queue = Queue(maxsize=self.window_size)
        self.latency_collector = Process(target=self.__latency_collect_daemon,
                                        args=(self.latency_queue,))
        self.latency_collector.deamon = True
        self.latency_collector.start()
    
    
    def getCurLatency(self):
        latency = 0.0
        if len(self.latency_lst) > 0:
            latency = self.latency_lst[-1]
        return float(latency)

    def updateLatency(self, latency):
        self.latency_lst.append(latency)
        if len(self.latency_lst) > self.window_size:
            self.latency_lst.pop(0)
        return

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