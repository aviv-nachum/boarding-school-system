from socket import *
import struct
import json
from threading import Thread
from config import HOST, PORT

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

class Client(Thread):
    def __init__(self):
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.ss.connect((HOST, PORT))
        self.id = self.ss.getsockname()[1]
        print(f"Connected as Client {self.id}")
        Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            try:
                message = receive_message_with_length(self.ss)
                print(f"Received: {message}")
            except:
                break

    def send_message(self, to_id, message):
        send_message_with_length(self.ss, {"to": to_id, "message": message})
