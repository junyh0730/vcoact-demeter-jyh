import socket
import sys

IP = "10.150.21.215"
PORT = 9995

if len(sys.argv) != 2:
    print("Insufficient arguments")
    sys.exit()

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect((IP,PORT))
strings = sys.argv[1]
print(strings)
sock.sendall(strings.encode('utf-8'))