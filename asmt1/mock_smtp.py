import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 1025))
server.listen(1)
print("Mock SMTP server listening on 127.0.0.1:1025...")

while True:
    conn, addr = server.accept()
    # 1. Greet on connect
    conn.sendall(b"220 MockSMTP ready\n")
    
    in_data = False
    while True:
        data = conn.recv(1024).decode("ascii")
        if not data:
            break
        
        # When in DATA mode, look for the terminating dot line
        if in_data:
            if ".\n" in data or data == ".\r\n":
                in_data = False
                conn.sendall(b"250 Message accepted\n")
            continue

        if data.startswith("HELO"):
            conn.sendall(b"250 Hello\n")
        elif data.startswith("MAIL FROM:"):
            conn.sendall(b"250 Sender OK\n")
        elif data.startswith("RCPT TO:"):
            conn.sendall(b"250 Recipient OK\n")
        elif data.startswith("DATA"):
            in_data = True
            conn.sendall(b"354 Start mail input; end with <CRLF>.<CRLF>\n")
        elif data.startswith("QUIT"):
            conn.sendall(b"221 Bye\n")
            break
    conn.close()
