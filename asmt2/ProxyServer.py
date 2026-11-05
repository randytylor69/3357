import glob
import os
import sys
from socket import *
from urllib.parse import urlparse

bind_host = sys.argv[1]
proxy_port = 8888

# Create cache directory if needed, and clean leftover files at startup
if not os.path.exists("cache"):
    os.makedirs("cache")
else:
    for f in glob.glob("cache/*"):
        try:
            os.remove(f)
        except OSError:
            pass

# TCP socket
proxy_socket = socket(AF_INET, SOCK_STREAM)
proxy_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
proxy_socket.bind((bind_host, proxy_port))
proxy_socket.listen(1)

print("Proxy server running...")

while True:
    print("Ready to serve...")

    client_socket, client_address = proxy_socket.accept()
    print(f"Received a connection from: {client_address}")

    # Read request headers until CRLF CRLF
    raw = b""
    while b"\r\n\r\n" not in raw:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        raw += chunk

    req_txt = raw.decode("iso-8859-1")
    print(f"Raw request: \n {req_txt}")

    lines = req_txt.split("\r\n")
    if not lines or not lines[0]:
        client_socket.close()
        continue

    parts = lines[0].split(" ")
    if len(parts) < 2:
        client_socket.close()
        continue

    method, url = parts[0], parts[1]

    # Reject non-GET requests
    if method != "GET":
        body = "405 Method Not Allowed"
        reply = (
            "HTTP/1.0 405 Method Not Allowed\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 22\r\n"
            "\r\n" + body
        )
        client_socket.sendall(reply.encode())
        client_socket.close()
        continue

    # Parse URL
    parsed_url = urlparse(url if "//" in url else "//" + url)
    host = parsed_url.hostname
    port = parsed_url.port or 80
    path = parsed_url.path if parsed_url.path else "/"
    if not path.startswith("/"):
        path = "/" + path

    print(f"Extracted:\nHost: {host}, Port: {port}, Path: {path}")

    # Format cache filename: port 80 uses host, other ports use host_port
    if port != 80:
        cache_host = f"{host}_{port}"
    else:
        cache_host = host

    cache_filename = "cache/" + cache_host + path.replace("/", "_")

    # Cache Hit
    if os.path.isfile(cache_filename):
        print(">>> CACHE HIT <<<")
        with open(cache_filename, "rb") as f:
            cached = f.read()
        client_socket.sendall(cached)
        print(f"Served from Local Cache: {cache_filename}")
        client_socket.close()
        continue

    # Cache Miss
    print("<<< CACHE MISS >>>\nConnecting to Server...")

    try:
        origin_socket = socket(AF_INET, SOCK_STREAM)
        origin_socket.connect((host, port))
    except OSError:
        body = "502 Bad Gateway"
        reply = (
            "HTTP/1.0 502 Bad Gateway\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 15\r\n"
            "\r\n" + body
        )
        client_socket.sendall(reply.encode())
        client_socket.close()
        continue

    print(f"Connection successful to {host}:{port}")

    # Forward GET request
    forward_host = f"{host}:{port}" if port != 80 else host
    forward = (
        f"GET {path} HTTP/1.0\r\n"
        f"Host: {forward_host}\r\n"
        f"Connection: close\r\n"
        f"User-Agent: SimpleProxy/1.0\r\n"
        f"\r\n"
    )
    origin_socket.sendall(forward.encode())

    # Read until origin closes connection
    res = b""
    while True:
        chunk = origin_socket.recv(4096)
        if not chunk:
            break
        res += chunk
    origin_socket.close()

    # Save to cache and return to client
    with open(cache_filename, "wb") as f:
        f.write(res)
    client_socket.sendall(res)
    print(f"Saved {len(res)} bytes to cache")
    client_socket.close()