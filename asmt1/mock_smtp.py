import socket

SMTP_IP = "127.0.0.1"
SMTP_PORT = 1025

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SMTP_IP, SMTP_PORT))
server.listen(5)

print(f"[SMTP SERVER] Listening on TCP {SMTP_IP}:{SMTP_PORT}...")

while True:
    conn, addr = server.accept()
    print(f"[SMTP SERVER] Client connected from {addr}")

    # Step 1: Initial greeting
    conn.sendall(b"220 SimpleMockSMTP Service Ready\n")

    in_data_mode = False
    received_mail_data = []

    while True:
        data = conn.recv(2048)
        if not data:
            break

        text = data.decode("ascii", errors="replace")

        # Step 6: When in DATA mode, accumulate until a single '.' line
        if in_data_mode:
            received_mail_data.append(text)
            if "\n.\n" in text or text.endswith(".\n") or text == ".\n":
                in_data_mode = False
                print("[SMTP SERVER] Full email body received successfully!")
                conn.sendall(b"250 Message accepted for delivery\n")
            continue

        # Process handshake commands
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines:
            if line.startswith("HELO"):
                print(f"[SMTP SERVER] -> {line}")
                conn.sendall(b"250 Hello\n")
            elif line.startswith("MAIL FROM:"):
                print(f"[SMTP SERVER] -> {line}")
                conn.sendall(b"250 Sender OK\n")
            elif line.startswith("RCPT TO:"):
                print(f"[SMTP SERVER] -> {line}")
                conn.sendall(b"250 Recipient OK\n")
            elif line == "DATA":
                print(f"[SMTP SERVER] -> DATA")
                in_data_mode = True
                conn.sendall(b"354 Start mail input; end with <CRLF>.<CRLF>\n")
            elif line == "QUIT":
                print(f"[SMTP SERVER] -> QUIT")
                conn.sendall(b"221 Service closing transmission channel\n")
                break

    conn.close()
    print(f"[SMTP SERVER] Closed connection with {addr}\n")
