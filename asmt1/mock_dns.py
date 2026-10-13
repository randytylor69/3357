import socket

DNS_IP = "127.0.0.1"
DNS_PORT = 1053

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((DNS_IP, DNS_PORT))

print(f"[DNS SERVER] Listening on UDP {DNS_IP}:{DNS_PORT}...")

while True:
    data, addr = sock.recvfrom(2048)
    if len(data) < 3:
        continue

    req_id = data[0]

    # Advance until null terminator 0x00 to extract echoed QNAME
    qname_end = 1
    while qname_end < len(data) and data[qname_end] != 0:
        qname_end += 1

    qname = data[1 : qname_end + 1]  # Includes trailing 0x00
    qtype = data[qname_end + 1]

    # Handle records
    qcode = 0
    if qtype == 15:  # MX query -> mail.uwo.ca
        answer_payload = b"\x04mail\x03uwo\x02ca\x00"
    elif qtype == 1:   # A query -> 127.0.0.1 (4 bytes)
        answer_payload = bytes([127, 0, 0, 1])
    else:
        qcode = 1
        answer_payload = b""

    answer_len = len(answer_payload)

    # Packet layout: [ID (1B)] [Echoed QNAME ... 0x00] [QCODE (1B)] [ANSWER_LEN (1B)] [ANSWER]
    response = bytes([req_id]) + qname + bytes([qcode, answer_len]) + answer_payload
    sock.sendto(response, addr)
    print(f"[DNS SERVER] Served query ID {req_id} (QTYPE {qtype}) to {addr}")
