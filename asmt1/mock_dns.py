# mock_dns.py
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 1053))
print("Mock DNS server listening on 127.0.0.1:1053...")

while True:
    data, addr = sock.recvfrom(512)
    req_id = data[0]

    # Find the end of QNAME in the query (starts at index 1, ends at 0x00)
    qname_end = 1
    while qname_end < len(data) and data[qname_end] != 0:
        qname_end += 1
    qname = data[1 : qname_end + 1]  # includes 0x00 terminator
    qtype = data[qname_end + 1]

    qcode = 0  # 0 = success

    if qtype == 15:  # MX query -> return hostname mail.uwo.ca
        answer_payload = b"\x04mail\x03uwo\x02ca\x00"
    elif qtype == 1:  # A query -> return IPv4 127.0.0.1 (4 bytes)
        answer_payload = bytes([127, 0, 0, 1])
    else:
        qcode = 1
        answer_payload = b""

    answer_len = len(answer_payload)

    # Wire layout: [ID] [Echoed QNAME] [QCODE] [ANSWER_LEN] [ANSWER]
    response = bytes([req_id]) + qname + bytes([qcode, answer_len]) + answer_payload
    sock.sendto(response, addr)
