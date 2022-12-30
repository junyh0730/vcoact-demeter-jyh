import socket
import multiprocessing
import logging

class VSock():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        self.logger = logging.getLogger("vsock_hyp")
        self.user = ""
        
        self.RX_CID = None
        self.RX_PORT = None
        self.TX_CID = None
        self.TX_PORT = None
        
        
        self.RX_BUF_LEN = 1024

        self.l_rx_buf = list()
        self.l_tx_buf = list()

        self.rx_sock = None
        self.tx_sock = None

        return
    
    def start(self):
        
        pass
    
    def send(self, s):
        if self.env.vsock_enable == False:
            return None

        try:
            self.tx_sock.sendall(s)
        except:
            print("tx fail")
        
        return

    
    def _start_rx(self,q):
        try:
            
            #listen
            logging.info("Listening")
            self.rx_sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            print("self.RX_CID~~~~~")
            print(self.RX_CID)
            print(self.RX_PORT)
            self.rx_sock.bind((self.RX_CID, self.RX_PORT))
            self.rx_sock.listen()
            (conn, (remote_cid, remote_port)) = self.rx_sock.accept()

            #connection
            self.logger.info("Got Rx connection")
            print(f"Connection opened by cid={remote_cid} port={remote_port}")
            process = multiprocessing.Process(target=self.__handle_rx, args=(conn,q,))
            process.daemon = True
            process.start()
            self.logger.info("Started process %r", process)
            """
            #listen
            logging.info("Listening")
            self.rx_sock_lc = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            print("self.RX_CID LC~~~~~")
            print(self.RX_CID_LC)
            print(self.RX_PORT_LC)
            self.rx_sock_lc.bind((self.RX_CID_LC, self.RX_PORT_LC))
            self.rx_sock_lc.listen()
            (conn, (remote_cid, remote_port)) = self.rx_sock_lc.accept()

            #connection
            self.logger.info("Got Rx_LC connection")
            print(f"Connection opened by cid={remote_cid} port={remote_port}")
            process = multiprocessing.Process(target=self.__handle_rx, args=(conn,q,))
            process.daemon = True
            process.start()
            self.logger.info("Started LC process %r", process)
            """
            
        except:
            logging.exception("Unexpected exception")
        
        return
    """
    def _start_rx_be(self,q):
        try:
            #listen
            logging.info("Listening")
            self.rx_sock_be = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            print("self.RX_CID BE~~~~~")
            print(self.RX_CID_BE)
            print(self.RX_PORT_BE)
            self.rx_sock_be.bind((self.RX_CID_BE, self.RX_PORT_BE))
            self.rx_sock_be.listen()
            (conn, (remote_cid, remote_port)) = self.rx_sock_be.accept()

            #connection
            self.logger.info("Got Rx_BE connection")
            print(f"Connection opened by cid={remote_cid} port={remote_port}")
            process = multiprocessing.Process(target=self.__handle_rx, args=(conn,q,))
            process.daemon = True
            process.start()
            self.logger.info("Started BE process %r", process)
            
        except:
            logging.exception("Unexpected exception")
        
        return 
    """
    def _start_tx(self):
        try:
            self.tx_sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            print(self.tx_sock)
            print("self.tx_sock.connect((self.TX_CID, self.TX_PORT))")
            print(self.TX_CID, self.TX_PORT)
            self.tx_sock.connect((self.TX_CID, self.TX_PORT))
            print("tx conn succ")
        except:
            print("tx conn fail")

        return 
    """
    
    def _start_tx_lc(self):
        try:
            self.tx_sock_lc = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            print(self.tx_sock_lc)
            print("self.tx_sock_lc.connect((self.TX_CID_LC, self.TX_PORT_LC))")
            print(self.TX_CID_LC, self.TX_PORT_LC)
            self.tx_sock_lc.connect((self.TX_CID_LC, self.TX_PORT_LC))
            print("tx_lc conn succ")
        except:
            print("tx_lc conn fail")

        return
    
    def _start_tx_be(self):
        try:
            self.tx_sock_be = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            print(self.tx_sock_be)
            print("self.tx_sock_be.connect((self.TX_CID_BE, self.TX_PORT_BE))")
            print(self.TX_CID_BE, self.TX_PORT_BE)
            self.tx_sock_be.connect((self.TX_CID_BE, self.TX_PORT_BE))
            print("tx_be conn succ")
        except:
            print("tx_be conn fail")

        return
    """
    def __handle_rx(self,conn,q):
        while True:
            buf = conn.recv(self.RX_BUF_LEN)
            if not buf:
                break

            self._cb_rx(buf,q)
        return
    
    def _cb_rx(self,buf,q):
        pass
    
    def __handle_tx(self):
        pass

    
    def _end_rx(self):
        for process in multiprocessing.active_children():
            process.join()
            logging.info("Shutting down process %r", process)
            process.terminate()

        logging.info("All done")
    
    def _end_tx(self):
        self.tx_sock.close()
        return
    