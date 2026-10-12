import socket
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
        if l == '\n': 
            isSeparated = True;
            continue;
        if (isSeparated == False): headerList.append(l);
        else: body+=l;

    for li in headerList:
        if (li[:5] == "From:"): 
            if '@' in li[6:-1]:
                sender  = li[6:-1]; continue 
            else: raise SystemExit(1);

        if (li[:3] == "To:"):  
            if '@' in li[4:-1]:
                recipient = li[4:-1]; continue
            else:  raise SystemExit(1);

        if (li[:8] == "Subject:"):                  
            subject = li[9:-1]; continue


    return sender, recipient, subject, body

if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        raise SystemExit(1)
    file_path = sys.argv[1]
    dns_ip = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'

    # 1. Parse email
    sender, recipient, subject, body = parse_email(file_path)
    print("sender: ", sender, "\nrecipient: ", recipient, "\nsubject: ", subject, "\nbody: ", body)
    # domain = recipient.split('@')[1]


