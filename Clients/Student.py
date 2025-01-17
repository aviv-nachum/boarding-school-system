from socket import *
from threading import Thread
from config import *
from Actions.Request import Request, RequestSerializer
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64


class Student(Thread):
    def __init__(self):
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)
        self.session_key = None
        self.session_id = None

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
        encrypted_data = base64.b64decode(encrypted_data)  # Decode from base64
    
        # print the encrypted data
        print(f"Encrypted response data: {encrypted_data[:50]}...")
    
        iv = encrypted_data[:AES.block_size]  # Extract IV
        encrypted_message = encrypted_data[AES.block_size:]  # Extract ciphertext
        cipher = AES.new(self.session_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_message), AES.block_size).decode('utf-8')  # Return decrypted plaintext




    def run(self):
        self.ss.connect((HOST, PORT))
        self.rsa_handshake()
        print("Connected to the server as a student.")

    def register(self, profile):
        request = Request(action="signup", profile=profile.to_dict())
        serialized_request = RequestSerializer.encode(request)
        encrypted_request = self.encrypt_request(serialized_request)
        self.ss.send(encrypted_request)
        encrypted_response = self.ss.recv(4096)
        if encrypted_response:
            print(f"Encrypted response received: {encrypted_response}")
            response = self.decrypt_response(encrypted_response)
            print(response)
        else:
            print("No response received from server")

    def login(self, student_id):
        request = Request(action="login", student_id=student_id)
        encrypted_request = self.encrypt_request(RequestSerializer.encode(request).decode('utf-8'))
        self.ss.send(encrypted_request)
        encrypted_response = self.ss.recv(4096)
        response = self.decrypt_response(encrypted_response)
        print(response)

    def logout(self):
        request = Request(action="logout", content={"session_id": self.session_id})
        encrypted_request = self.encrypt_request(RequestSerializer.encode(request).decode('utf-8'))
        self.ss.send(encrypted_request)
        encrypted_response = self.ss.recv(4096)
        response = self.decrypt_response(encrypted_response)
        print(response)

    def submit_request(self, content, approver_id):
        request = Request(action="submit_request", content=content, approver_id=approver_id, profile={"session_id": self.session_id})
        encrypted_request = self.encrypt_request(RequestSerializer.encode(request).decode('utf-8'))
        self.ss.send(encrypted_request)
        encrypted_response = self.ss.recv(4096)
        response = self.decrypt_response(encrypted_response)
        print(response)
