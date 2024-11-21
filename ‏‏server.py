from socket import *
from threading import Thread, Lock
import struct
import json

HOST = 'localhost'
PORT = 8000

clients = {}  # Dictionary to store client ID -> socket
lock = Lock()

def send_message_with_length(sock, message):
    message_bytes = json.dumps(message).encode('utf-8')
    packed_length = struct.pack('!I', len(message_bytes))
    sock.sendall(packed_length + message_bytes)

def receive_message_with_length(sock):
    packed_length = sock.recv(4)
    if not packed_length:
        return None
    length = struct.unpack('!I', packed_length)[0]
    data = sock.recv(length).decode('utf-8')
    return json.loads(data)

class Server(Thread):
    def __init__(self):
        super().__init__()
        self.addr = (HOST, PORT)

    def run(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind(self.addr)
        self.s.listen(5)
        print("Server is running...")

        while True:
            conn, addr = self.s.accept()
            with lock:
                client_id = len(clients) + 1
                clients[client_id] = conn
            print(f"Client {client_id} connected from {addr}.")
            Thread(target=self.client_handler, args=(conn, client_id)).start()

    def client_handler(self, conn, client_id):
        while True:
            try:
                message = receive_message_with_length(conn)
                if not message:
                    break
                to_id = message['to']
                msg_content = message['message']
                print(f"Client {client_id} -> Client {to_id}: {msg_content}")

                with lock:
                    if to_id in clients:
                        send_message_with_length(clients[to_id], {"from": client_id, "message": msg_content})
            except Exception as e:
                print(f"Error: {e}")
                break

        with lock:
            del clients[client_id]
        conn.close()
        print(f"Client {client_id} disconnected.")
