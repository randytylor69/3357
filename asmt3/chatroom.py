import socket
import threading
import select


class ServerTCP:
    def __init__(self, server_port):
        self.server_port = server_port
        self.clients = {}
        self.run_event = threading.Event()
        self.handle_event = threading.Event()

        # Create TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get own IP
        addr = socket.gethostbyname(socket.gethostname())

        # Bind the socket
        self.server_socket.bind((addr, self.server_port))

        # Start socket
        self.server_socket.listen(5)  # OS will queue up to 5 pending connections

        print(f"Server started on {addr}:{self.server_port}")

    def accept_client(self):
        # Uses `select` to check for available new clients. If yes, reads their name and either welcomes/rejects them.
        ready, _, _ = select.select(
            [self.server_socket], [], [], 1
        )  # waits up to 1 sec for a new connection

        if ready:
            client_socket, client_addr = (
                self.server_socket.accept()
            )  # Valid connetion & accept connection
            name = client_socket.recv(1024).decode()

            # Check if name already taken
            if name in self.clients.values():
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
        if message == "join":
            broadcast_msg = f"User {name} joined"
        elif message == "exit":
            broadcast_msg = f"User {name} left"
        else:
            broadcast_msg = f"{name}: {message}"

        # send msg
        for client_sock in list(self.clients.keys()):
            if client_sock != client_socket_sent:
                try:
                    client_sock.send(broadcast_msg.encode())
                except:
                    pass  # if nothing happens just skip

    def shutdown(self):
        # Announce every client that the server is shutting down
        for c in list(self.clients.keys()):
            try:
                c.send("server-shutdown".encode())
                c.close()
            except:
                pass

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
        while not self.handle_event.is_set():
            try:
                # Wait up to 1 second for data from this client
                ready, _, _ = select.select([client_socket], [], [], 1)

                if ready:
                    message = client_socket.recv(1024).decode()

                    if not message:
                        break  # client disconnected unexpectedly

                    if message == "exit":
                        self.broadcast(client_socket, "exit")
                        self.close_client(client_socket)
                        break
                    else:
                        self.broadcast(client_socket, message)

            except:
                break

    def run(self):
        print("Server is running...")
        try:
            while not self.run_event.is_set():
                # Try to accept a new client (waits up to 1s inside)
                result = self.accept_client()
                if result:
                    # Get the most recently added client socket
                    # (the last key added to the dict)
                    client_socket = list(self.clients.keys())[-1]
                    # Start a thread to handle this client's messages
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,),
                        daemon=True,
                    )
                    thread.start()
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()


class ClientTCP:

    def __init__(self, client_name, server_port):
        self.server_port = server_port
        self.client_name = client_name
        self.exit_run = threading.Event()
        self.exit_receive = threading.Event()

        # create TCP socket and get server address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = socket.gethostbyname(socket.gethostname())

    def connect_server(self):
        try:
            # establish TCP connection, send name, wait for response
            self.client_socket.connect((self.server_addr, self.server_port))
            self.client_socket.send(self.client_name.encode())
            response = self.client_socket.recv(1024).decode()
            if "Welcome" in response:
                print(response)
                return True
            else:
                print(response)
                return False
        except:
            return False

    def send(self, text):
        self.client_socket.send(text.encode())

    def receive(self):
        while not self.exit_receive.is_set():
            try:
                ready, _, _ = select.select([self.client_socket], [], [], 1)
                if ready:
                    message = self.client_socket.recv(1024).decode()
                    if not message:
                        break
                    if message == "server-shutdown":
                        print("Server is shutting down.")
                        self.exit_run.set()
                        self.exit_receive.set()
                        break
                    else:
                        print(message)
            except:
                break

    def run(self):
        if not self.connect_server():
            return

        # receive loop in background thread
        recv_thread = threading.Thread(target=self.receive, daemon=True)
        recv_thread.start()

        try:
            while not self.exit_run.is_set():
                text = input("")
                if text.lower() == "exit":
                    self.send("exit")
                    self.exit_receive.set()
                    break
                self.send(text)
        except KeyboardInterrupt:
            self.send("exit")
            self.exit_receive.set()
        finally:
            self.client_socket.close()


class ServerUDP:
    def __init__(self, server_port):
        self.server_port = server_port
        self.clients = {}
        self.messages = []

        # create UDP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = socket.gethostbyname(socket.gethostname())
        self.server_socket.bind((addr, self.server_port))
        print(f"UDP Server started on {addr}:{self.server_port}")

    def accept_client(self, client_addr, message):
        # extract name from client message
        name = message.split(":")[0].strip()

        # check if name already taken
        if name in self.clients.values():
            self.server_socket.sendto("Name already taken".encode(), client_addr)
            return False

        # welcome new client, track, and queue up join announcement. broadacst.
        self.server_socket.sendto("Welcome".encode(), client_addr)
        self.clients[client_addr] = name
        self.messages.append((client_addr, f"User {name} joined"))
        self.broadcast()
        return True

    def close_client(self, client_addr):
        if client_addr in self.clients:
            name = self.clients[client_addr]
            del self.clients[client_addr]
            self.messages.append((client_addr, f"User {name} left"))
            self.broadcast()
            return True
        return False

    def broadcast(self):
        if not self.messages:
            return
        sender_addr, msg = self.messages[-1]
        for client_addr in list(self.clients.keys()):
            if client_addr != sender_addr:
                try:
                    self.server_socket.sendto(msg.encode(), client_addr)
                except:
                    pass

    def shutdown(self):
        for client_addr in list(self.clients.keys()):
            try:
                self.server_socket.sendto("server-shutdown".encode(), client_addr)
            except:
                pass
        self.clients.clear()
        self.server_socket.close()
        print("UDP Server shut down.")

    def get_clients_number(self):
        return len(self.clients)

    def run(self):
        print("UDP Server is running...")
        try:
            while True:
                try:
                    ready, _, _ = select.select([self.server_socket], [], [], 1)
                    if ready:
                        data, client_addr = self.server_socket.recvfrom(1024)
                        message = data.decode()
                        parts = message.split(": ", 1)
                        text = parts[1] if len(parts) > 1 else message

                        if text == "join":
                            self.accept_client(client_addr, message)
                        elif text == "exit":
                            self.close_client(client_addr)
                        else:
                            if client_addr in self.clients:
                                self.messages.append((client_addr, message))
                                self.broadcast()
                except:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()


class ClientUDP:
    def __init__(self, client_name, server_port):
        self.server_port = server_port
        self.client_name = client_name
        self.exit_run = threading.Event()
        self.exit_receive = threading.Event()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = socket.gethostbyname(socket.gethostname())

    def connect_server(self):
        try:
            self.send("join")
            ready, _, _ = select.select([self.client_socket], [], [], 5)
            if ready:
                data, _ = self.client_socket.recvfrom(1024)
                response = data.decode()
                if "Welcome" in response:
                    print(response)
                    return True
                else:
                    print(response)
                    return False
            return False
        except:
            return False

    def send(self, text):
        message = f"{self.client_name}: {text}"
        self.client_socket.sendto(
            message.encode(), (self.server_addr, self.server_port)
        )

    def receive(self):
        while not self.exit_receive.is_set():
            try:
                ready, _, _ = select.select([self.client_socket], [], [], 1)
                if ready:
                    data, _ = self.client_socket.recvfrom(1024)
                    message = data.decode()
                    if message == "server-shutdown":
                        print("Server is shutting down.")
                        self.exit_run.set()
                        self.exit_receive.set()
                        break
                    else:
                        print(message)
            except:
                break

    def run(self):
        if not self.connect_server():
            return

        recv_thread = threading.Thread(target=self.receive, daemon=True)
        recv_thread.start()

        try:
            while not self.exit_run.is_set():
                text = input("")
                if text.lower() == "exit":
                    self.send("exit")
                    self.exit_receive.set()
                    break
                self.send(text)
        except KeyboardInterrupt:
            self.send("exit")
            self.exit_receive.set()
        finally:
            self.client_socket.close()
