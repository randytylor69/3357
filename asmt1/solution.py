from socket import *
import os
import sys
import time

def parse_email(file_path):
    sender, recipient, subject, body = "", "", "", "";
    lineList = [];
    headerList = [];
    isSeparated = False;

    # append each line into a list
    with open(file_path) as f:
        for li in f: lineList.append(li);

    # separate header and body with blank line
    for l in lineList:
        if (l == '\n' or l == '\r\n') and isSeparated == False: 
            isSeparated = True;
            continue;
        if (isSeparated == False): headerList.append(l);
        else: body+=l;
    if isSeparated == False: raise SystemExit("ERROR: no email content")
    
    # parse header
    if len(headerList) == 0: raise SystemExit(1); # empty header ERROR!

    for li in headerList:
        li = li.strip();
        if ":" not in li: raise SystemExit("ERROR: wrong header format ")
        headerType, headerCont = li.split(':',1); # split between header type and content
        headerType = headerType.strip();
        headerCont = headerCont.strip();
        
        # validate header content 
        if headerType.lower() == "from" or headerType.lower() == "to":
            if '@' not in headerCont: raise SystemExit("ERROR: '@' not in email")
            user, domain = headerCont.split('@',1)
            if not user or not domain: raise SystemExit("ERROR: email length error")

        # validate header type
        if headerType.lower() == "from": sender = headerCont;
        if headerType.lower() == "to": recipient = headerCont;
        if headerType.lower() == "subject": subject = headerCont;
    
    if not sender or not recipient or not subject: raise SystemExit("ERROR: insufficient header")
    
    return sender, recipient, subject, body

# ==========================================================================================
# convert domain to bytes
def build_dns_query(id, domain, qtype):
    # convert id to bytes
    id_byte = bytes([id])

    # convert domain 
    qname=b""
    domainList = domain.split('.');
    for label in domainList:
        label_byte = bytes([len(label)]) + label.encode("ascii") # length_byte + ascii_byte
        qname += label_byte
    qname+=b"\x00"

    return id_byte + qname + bytes([qtype])

# ==========================================================================================
# deliver bytes to the DNS server
def send_dns_query(dns_ip, query):
    # create UDP socket
    clientSocket = socket(AF_INET, SOCK_DGRAM);
    clientSocket.settimeout(5.0);

    try:
        clientSocket.sendto(query, (dns_ip, 1053));
        response, serverAddress = clientSocket.recvfrom(2048);
        return response
    except timeout:
        raise SystemExit("ERROR: DNS query timeout");
    finally:
        clientSocket.close();


# ==========================================================================================
# parse DNS server response
def parse_dns_response(response, expected_id, qtype):

    print(response,'\n')
    # validate response length
    if len(response) < 4: 
        raise SystemExit(f"ERROR: Insufficient response length. Current: {len(response)}")

    # validate ID
    if response[0] != expected_id: raise SystemExit("ERROR: DNS response ID doesn't match")

    # parse QNAME echo (pass through the domain name)
    index = 1;
    while index < len(response) and response[index] !=0 : index += 1
    if index >= len(response): raise SystemExit("ERROR: 0x00 terminator from DNS res not found")
    index += 1; # go past the terminator
    
    # validate QCODE
    if response[index] != 0: 
        raise SystemExit(f"ERROR: Failed QCODE from DNS response. Current: {response[index]}")
    index += 1;
    
    # read ANSWER_LEN
    answer_len = response[index]
    index += 1;

    # read ANSWER
    answer = response[index : index + answer_len]

    # handle type A
    if qtype == 1:
        if answer_len !=4: raise SystemExit("ERROR: Invalid A record response length")
        return '.'.join(str(b) for b in answer) # i.e. "127.0.0.1"

    # handle type MX
    if qtype == 15:
        domainList = []
        answer_index = 2 # start from index 2 of the answer 
        while answer_index < len(answer):
            leng = answer[answer_index]
            if leng == 0: break # found terminator 0x00
            answer_index += 1
            domainSection = answer[answer_index:answer_index + leng].decode("ascii")
            domainList.append(domainSection)
            answer_index += leng
        return '.'.join(domainList)

# ==========================================================================================
# connect TCP
def send_smtp_email(ip, sender, recipient, subject, body):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(5.0)

    try:
        sock.connect((ip, 1025))

        # helper method to send stuff
        def send(cmd, expected_code):
            if cmd: sock.sendall(cmd.encode("ascii"))
            res = sock.recv(1024).decode("ascii")
            if not res.startswith(expected_code): raise SystemExit("ERROR: Response not expected")
        
        # 1. read "220..."
        send(None, "220")
        # 2. send "HELO <send_domain>"
        send(f"HELO {sender.split('@')[1]}\n", "250")
        # 3. mail from
        send(f"MAIL FROM: <{sender}>\n", "250")
        # 4. receipient
        send(f"RCPT TO:<{recipient}>\n", "250")
        # 5. data
        send("DATA\n", "354")
        # 6. body
        send(
            f"FROM: {sender}\n"
            f"TO: {recipient}\n"
            f"Subject: {subject}\n\n"
            f"{body}\n.\n", "250"
        )
        # 7. quit
        send("QUIT\n", "221")
    except (timeout, error): raise SystemExit("ERROR: send_smtp_email timeout/error")
    finally: sock.close()


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        raise SystemExit(1)
    file_path = sys.argv[1]
    dns_ip = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'

    sender, recipient, subject, body = parse_email(file_path)
    domain = recipient.split('@')[1]

    mx_query = build_dns_query(18, domain, 15)
    mx_response = send_dns_query(dns_ip, mx_query)
    mx_host = parse_dns_response(mx_response, 18, 15)

    a_query = build_dns_query(19, mx_host, 1)
    a_response = send_dns_query(dns_ip, a_query)
    ip = parse_dns_response(a_response, 19, 1)

    send_smtp_email(ip, sender, recipient, subject, body)
