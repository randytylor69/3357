import sys
import time
from socket import *

# read hostname and port from cmd

server_name = sys.argv[1]
server_port = int(sys.argv[2])

# open UDP socket

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(1)

# send 10 pins: [Ping <sequence_number> <timestamp>] 

for sequence in range(1,11):
    msg = f"Ping {str(sequence)} {time.ctime()}"
    try:
        start = time.time()
        client_socket.sendto(msg.encode(), (server_name, server_port))
        reply, server_address = client_socket.recvfrom(1024)
        RTT = time.time() - start

        print(f"Reply from {server_address[0]}: {reply.decode()}")
        print(f"RTT: {str(RTT)}")
    
    except timeout:
        print("Request timed out.")

client_socket.close()



