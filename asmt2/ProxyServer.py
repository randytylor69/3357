import os
import sys
from socket import *
from urllib.parse import urlparse

bind_host = sys.argv[1]
proxy_port = 8888

# creates cache folder if not already exists

if not os.path.exists("cache"):
    os.makedirs("cache")

# TCP socket

proxy_socket = socket(AF_INET, SOCK_STREAM)
proxy_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
proxy_socket.bind((bind_host, proxy_port))  # claims port 8888
proxy_socket.listen(1) # set socket to wait for incoming calls

print("Proxy server running...")

while True:
    print("Ready to serve...")

    # completes one call and gets client information
    client_socket, client_address = proxy_socket.accept()
    print(f"Received a connection from: {client_address}")

    # read request information
    raw = b""
    while b"\r\n\r\n" not in raw:
        chunk = client_socket.recv(4096)
        if chunk: raw += chunk
   
    # print request
    req_txt = raw.decode("iso-8859-1")
    print(f"Raw request: \n {req_txt}")

    # reject non-GET requests
    req_line = req_txt.split("\r\n")[0]
    method, url, _version = req_line.split(" ")

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
    
    # parse the url -> host, port, path
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or 80
    path = parsed_url.path if parsed_url.path else "/"

    print(f"Extracted:\nHost: {host}, Port: {port}, Path: {path}")

    # modify cache name
    cache_filename = "cache/" + host + path.replace("/","_")

    # IF file already cached then we just send it
    if os.path.isfile(cache_filename):
        print(">>> CACHE HIT <<<")
        with open(cache_filename, "rb") as f:
            cached = f.read()
        client_socket.sendall(cached)
        print(f"Served from local cache: {cache_filename}")
        client_socket.close()
        continue

    # ELSE call the origin
    print(">>> CACHE MISS <<<\nConnecting to Server...")

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
    
    # FINALLY
    print(f"Connection succesful to {host}:{port}")

    # Send the 4 line request and read until origin closes:
    forward = (
            f"GET {path} HTTP/1.0\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n"
            f"User-Agent: SimpleProxy/1.0\r\n"
            f"\r\n"
            )
    origin_socket.sendall(forward.encode())

    res = b""
    while True:
        chunk = origin_socket.recv(4096)
        if not chunk: break
        res += chunk
    origin_socket.close()

    with open(cache_filename, "wb") as f: f.write(res)
    client_socket.sendall(res)
    print(f"Saved {len(res)} bytes to cache")
    client_socket.close()

