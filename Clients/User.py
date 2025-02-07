from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from config import HOST, PORT
from Actions.Request import Request, RequestSerializer
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from template_classes.encConnection import ClientEncConnection
import base64
import json

class User(Thread):
    def __init__(self, username, password, role, profile):
        super().__init__()
        self.connection = ClientEncConnection(HOST, PORT, socket())
        self.username = username
        self.password = password
        self.role = role
        self.profile = profile
        self.ss = socket(AF_INET, SOCK_STREAM)
        self.session_key = None
        self.session_id = None

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password
    
    def send_request(self, request):
        self.connection.send_msg(RequestSerializer.encode(request))
        
    def receive_response(self):
        return RequestSerializer.decode(self.connection.recv_msg())

    def rsa_handshake(self):
        """
        Perform RSA handshake to exchange AES session keys with the server.
        """
        public_key = RSA.import_key(self.ss.recv(4096))
        cipher_rsa = PKCS1_OAEP.new(public_key)
        self.session_key = get_random_bytes(16)
        encrypted_session_key = cipher_rsa.encrypt(self.session_key)
        self.ss.send(encrypted_session_key)

    def encrypt_request(self, data):
        """
        Encrypt the request data using AES and the session key.
        """
        cipher = AES.new(self.session_key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        payload = base64.b64encode(cipher.iv + encrypted_data)
        return payload

    def decrypt_response(self, encrypted_data):
        """
        Decrypt the response data using AES and the session key.
        """
        encrypted_data = base64.b64decode(encrypted_data)
        iv = encrypted_data[:AES.block_size]
        encrypted_message = encrypted_data[AES.block_size:]
        cipher = AES.new(self.session_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_message), AES.block_size).decode('utf-8')

    def run(self):
        self.connection.connect()
        self.connection.start()
        self.ss.connect((HOST, PORT))
        self.rsa_handshake()
        print(f"Connected to the server as {self.role}.")

    def login(self, user_id):
        session_key_encoded = base64.b64encode(self.session_key).decode('utf-8')
        request = Request(action="login", student_id=user_id, session_key=session_key_encoded)
        serialized_request = RequestSerializer.encode(request)
        encrypted_request = self.encrypt_request(serialized_request)
        self.ss.send(encrypted_request)
        try:
            encrypted_response = self.ss.recv(4096)
            if encrypted_response:
                response = self.decrypt_response(encrypted_response)
                response_data = json.loads(response)
                self.session_id = response_data.get("session_id")
                print(response_data.get("message"))
            else:
                print("No response received from server")
        except ConnectionAbortedError as e:
            print(f"Connection aborted: {e}")

    def logout(self):
        session_key_encoded = base64.b64encode(self.session_key).decode('utf-8')
        request = Request(action="logout", content={"session_id": self.session_id}, session_key=session_key_encoded)
        serialized_request = RequestSerializer.encode(request)
        encrypted_request = self.encrypt_request(serialized_request)
        self.ss.send(encrypted_request)
        encrypted_response = self.ss.recv(4096)
        response = self.decrypt_response(encrypted_response)
        print(response)