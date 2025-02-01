from socket import *
from threading import Thread
from config import *
from Actions.Request import Request, RequestSerializer
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from Clients.User import User
import json

class Staff(User):
    def __init__(self, username, password, profile):
        super().__init__(username, password, role="staff", profile=profile)

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
        """
        Connect to the server and perform RSA handshake.
        """
        self.ss.connect((HOST, PORT))
        self.rsa_handshake()
        print("Connected to the server as staff.")

    def register(self, profile):
        """
        Register a new staff profile with the server.
        """
        session_key_encoded = base64.b64encode(self.session_key).decode('utf-8')
        request = Request(action="signupStaff", profile=profile.to_dict(), session_key=session_key_encoded)
        serialized_request = RequestSerializer.encode(request)
        encrypted_request = self.encrypt_request(serialized_request)
        self.ss.send(encrypted_request)
        try:
            encrypted_response = self.ss.recv(4096)
            if (encrypted_response):
                response = self.decrypt_response(encrypted_response)
                print(response)
            else:
                print("No response received from server")
        except ConnectionAbortedError as e:
            print(f"Connection aborted: {e}")

    def login(self, staff_id):
        """
        Log in to the server using the staff ID.
        """
        request = Request(action="login", student_id=staff_id)
        encrypted_request = self.encrypt_request(RequestSerializer.encode(request))
        self.ss.send(encrypted_request)
        response = self.decrypt_response(self.ss.recv(4096).decode('utf-8'))
        print(response)
        if "Session ID" in response:
            self.session_id = response.split(": ")[1]

    def logout(self):
        """
        Log out from the server.
        """
        request = Request(action="logout", content={"session_id": self.session_id})
        encrypted_request = self.encrypt_request(RequestSerializer.encode(request))
        self.ss.send(encrypted_request)
        response = self.decrypt_response(self.ss.recv(4096).decode('utf-8'))
        print(response)

    def view_requests(self):
        """
        View requests assigned to this staff member.
        """
        session_key_encoded = base64.b64encode(self.session_key).decode('utf-8')
        request = Request(action="view_requests", content={"session_id": self.session_id}, session_key=session_key_encoded)
        serialized_request = RequestSerializer.encode(request)
        encrypted_request = self.encrypt_request(serialized_request)
        self.ss.send(encrypted_request)
        encrypted_response = self.ss.recv(4096)
        response = self.decrypt_response(encrypted_response)
        print(response)

    def approve_request(self, request_id):
        """
        Approve a specific request by ID.
        """
        session_key_encoded = base64.b64encode(self.session_key).decode('utf-8')
        request = Request(action="approve_request", request_id=request_id, content={"session_id": self.session_id}, session_key=session_key_encoded)
        serialized_request = RequestSerializer.encode(request)
        encrypted_request = self.encrypt_request(serialized_request)
        self.ss.send(encrypted_request)
        encrypted_response = self.ss.recv(4096)
        response = self.decrypt_response(encrypted_response)
        print(response)
