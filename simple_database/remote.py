import socket
import threading
import json

from . import local

class client:
    def __init__(self, address):
        self.address = address

    def perform_action(self, action, arg):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(self.address)
        client_socket.sendall(json.dumps({'action': action, 'arg': arg}).encode())
        data = json.loads(client_socket.recv(1024).decode())
        client_socket.shutdown(1)
        client_socket.close()
        return data

    def dump(self):
        return self.perform_action('dump', None)

    def read(self, *keys):
        return self.perform_action('read', keys)

    def write(self, value, *keys):
        return self.perform_action('write', (value, keys))

    def remove(self, *keys):
        return self.perform_action('remove', keys)

class server:
    def __init__(self, address, path):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.database = local.database(path)

    def start(self):
        self.database.start()
        self.socket.bind(self.address)
        self.socket.listen()
        while True:
            client_socket, _ = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def stop(self):
        self.database.stop()
        self.socket.shutdown(1)
        self.socket.close()

    def handle_client(self, client_socket):
        data = json.loads(client_socket.recv(1024).decode())
        match data['action']:
            case 'dump':
                return_data = self.database.perform_action(0, None)
            case 'read':
                return_data = self.database.perform_action(1, data['arg'])
            case 'write':
                return_data = self.database.perform_action(2, data['arg'])
            case 'remove':
                return_data = self.database.perform_action(3, data['arg'])
        client_socket.sendall(json.dumps(return_data).encode())
        client_socket.shutdown(1)
        client_socket.close()