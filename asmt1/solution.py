import socket
import os
import sys
import time

def parse_email(file_path):
    sender, recipient, subject, body = "", "", "", "";
    lineList = [];
    lineCount = 0;
    
    # append each line into a list
    with open(file_path) as f:
        for line in f:
            lineList.append(line);
    
    # populate return tuple elements
    for li in lineList:
        if (li[:5] == "From:" and '@' in li[6:-1] and lineCount == 0): sender  = li[6:-1]
        elif (li[:3] == "To:" and '@' in li[4:-1] and lineCount == 1):  recipient = li[4:-1]
        elif (li[:8] == "Subject:" and lineCount == 2):                  subject = li[9:-1]
        else: body+= (li + '\n')
        lineCount += 1;

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


