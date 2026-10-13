# mock_dns.py
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 1053))
print("Mock DNS server listening on 127.0.0.1:1053...")

while True:
    data, addr = sock.recvfrom(512)
    # Echo back: [ID (1B)] [STATUS 0 (1B)] [dummy answer payload]
    req_id = data[0]
    # For MX query, respond with status 0 and a sample encoded domain: e.g. b'\x04mail\x03uwo\x02ca\x00'
    response = bytes([req_id, 0]) + b"\x04mail\x03uwo\x02ca\x00"
    sock.sendto(response, addr)
