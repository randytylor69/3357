class ServerTCP:
    def __init__(self, server_port):
        pass
    def accept_client(self):
        pass
    def close_client(self, client_socket):
        pass
    def broadcast(self, client_socket_sent, message):
        pass
    def shutdown(self):
        pass
    def get_clients_number(self):
        pass
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