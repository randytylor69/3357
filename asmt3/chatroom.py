import socket

class ServerTCP:
    def __init__(self, server_port):
        self.server_port = server_port;
        self.client = {} 
        self.run_event = threading.Event()
        self.handle_event = threading.Event()

        # Create TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get own IP
        addr = socket.gethostbyname(socket.gethostname())

        # Bind the socket
        self.server_socket.bind((addr, self.server_port))

        # Start socket
        self.server_socket.listen(5) # OS will queue up to 5 pending connections
        
        print(f"Server started on {addr}:{self.server_port}")

    def accept_client(self):
        # Uses `select` to check for available new clients. If yes, reads their name and either welcomes/rejects them.
        ready, _, _ = select.select([self.server_socket], [], [], 1) # waits up to 1 sec for a new connection
    
        if ready:
            client_socket, client_addr = self.server_socket.accept() # Valid connetion & accept connection
            name = client_socket.recv(1024).decode()

            # Check if name already taken
            if name in self.client.values():
                client_socket.send("Name already taken".encode())
                client_socket.close()
                return False
            
            # ELSE, welcome the unique name, store the client, and annouce the new connection
            client_socket.send("Welcome".encode())
            self.clients[client_socket] = name
            self.broadcast(client_socket, "join")
            return True

        return False

    def close_client(self, client_socket):
        if client_socket in self.clients:
            del self.clients[client_socket]
            client_socket.close()
            return True
        return False

    def broadcast(self, client_socket_sent, message):
        # sends message to everyone except the sender
        name = self.clients.get(client_socket_sent, "Unknown")

        # builds broadcast based on msg type
        if message = "join": broadcast_msg = f"User {name} joined"
        if message = "exit": broadcast_msg = f"User {name} left"
        else: broadcast_msg = f"{name}: {message}"

        # send msg
        for client_sock in list(self.clients.keys()):
            if client_sock != client_socket_sent:
                try: client_sock.send(broadcast_msg.encode())
                except: pass # if nothing happens just skip

    def shutdown(self):
        # Announce every client that the server is shutting down
        for c in list(self.clients.keys()):
            try:
                c.send("server-shutdown".encode())
                c.close()
            except: pass
        
        self.clients.clear()

        # Stops all loops
        self.run_event.set()
        self.handle_event.set()

        # CLose the main listning socket
        self.server_socket.close()
        print("Server shut down.")

    def get_clients_number(self):
        return len(self.clients)

    def handle_client(self, client_socket):
        pass
    def run(self):
        pass

class ClientTCP:
    def __init__(self, client_name, server_port):
        pass
    def connect_server(self):
        pass
    def send(self, text):
        pass
    def receive(self):
        pass
    def run(self):
        pass

class ServerUDP:
    def __init__(self, server_port):
        pass
    def accept_client(self, client_addr, message):
        pass
    def close_client(self, client_addr):
        pass
    def broadcast(self):
        pass
    def shutdown(self):
        pass
    def get_clients_number(self):
        pass
    def run(self):
        pass

class ClientUDP:
    def __init__(self, client_name, server_port):
        pass
    def connect_server(self):
        pass
    def send(self, text):
        pass
    def receive(self):
        pass
    def run(self):
        pass
