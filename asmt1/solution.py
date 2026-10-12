import socket
import os
import sys
import time

def parse_email(file_path):
    sender, recipient, subject, body = "", "", "", "";
    lineList = [];
    lineCount = -1;
    
    # append each line into a list
    with open(file_path) as f:
        for line in f:
            lineList.append(line);
    
    # populate return tuple elements
    for li in lineList:
        lineCount += 1;

        if (li == '\n'): continue;

        if (li[:5] == "From:" and lineCount == 0): 
            if '@' in li[6:-1]:
                sender  = li[6:-1]; continue 
            else: raise SystemExit(1);

        if (li[:3] == "To:" and lineCount == 1):  
            if '@' in li[4:-1]:
                recipient = li[4:-1]; continue
            else:  raise SystemExit(1);
        
        if (li[:8] == "Subject:" and lineCount == 2):                  
            subject = li[9:-1]; continue

        body+= (li + '\n')
    
    # format body
    if len(body) > 2: body = body [0: -2] # remove trailing \n

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


