import socket
import multiprocessing
import logging

class VSock():
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

        self.logger = logging.getLogger("vsock_hyp")
        self.user = ""
        self.CID = None
        self.PORT = None

        self.RX_BUF_LEN = 256

        self.l_rx_buf = list()
        self.l_tx_buf = list()

        self.rx_sock = None
        self.tx_sock = None

        return
    
    def start(self):
        pass
    
    def send(self, s):
        try:
            self.tx_sock.sendall(s)
        except:
            print("tx fail")
        
        return

    
    def _start_rx(self):
        try:
            #listen
            logging.info("Listening")
            self.rx_sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            self.rx_sock.bind((self.CID, self.PORT))
            self.rx_sock.listen()
            (conn, (remote_cid, remote_port)) = self.rx_sock.accept()

            #connection
            self.logger.debug("Got connection")
            print(f"Connection opened by cid={remote_cid} port={remote_port}")
            process = multiprocessing.Process(target=self.__handle_rx, args=(conn))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)

        except:
            logging.exception("Unexpected exception")

        finally:
            logging.info("Shutting down")
            for process in multiprocessing.active_children():
                logging.info("Shutting down process %r", process)
                process.terminate()
                process.join()

        logging.info("All done")
        return
    
    def _start_tx(self):
        try:
            self.tx_sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            self.tx_sock.connect((self.CID, self.PORT))
        except:
            print("connection fail")

        return 
    
    def __handle_rx(self,conn):
        while True:
            buf = conn.recv(self.RX_BUF_LEN)
            if not buf:
                break

            self._cb_rx(buf)
        return
    
    def _cb_rx(self,buf):
        pass
    
    def __handle_tx(self):
        pass

    
    def _end_rx(self):
        pass
    
    def _end_tx(self):
        self.tx_sock.close()
        return
    