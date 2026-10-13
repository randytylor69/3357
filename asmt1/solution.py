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
    except timeout:
        raise SystemExit("ERROR: DNS query timeout");
    finally:
        clientSocket.close();


     


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        raise SystemExit(1)
    file_path = sys.argv[1]
    dns_ip = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'

    # 1. Parse email
# ==========================================================================================
    sender, recipient, subject, body = parse_email(file_path)
    domain = recipient.split('@')[1]

    mx_query = build_dns_query(18, domain, 15)
    mx_response = send_dns_query(dns_ip, mx_query)
