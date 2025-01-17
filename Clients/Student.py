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
        # Receive the server's public key
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
        # Pad the data (already in bytes) and encrypt
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        payload = cipher.iv + encrypted_data  # Combine IV and ciphertext
        return base64.b64encode(payload).decode('utf-8')  # Encode payload as base64



    def decrypt_response(self, encrypted_data):
        """
        Decrypt the response data using AES and the session key.
        """
        encrypted_data = base64.b64decode(encrypted_data)  # Decode from base64
        iv = encrypted_data[:16]  # Extract IV (first 16 bytes)
        encrypted_message = encrypted_data[16:]  # Extract ciphertext
        cipher = AES.new(self.session_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_message), AES.block_size).decode('utf-8')

    def run(self):
        """
        Connect to the server and perform RSA handshake.
        """
        self.ss.connect((HOST, PORT))
        self.rsa_handshake()
        print("Connected to the server as a student.")

    def register(self, profile):
        """
        Register a new student profile with the server.
        """
        request = Request(action="signup", profile=profile.to_dict())
        serialized_request = RequestSerializer.encode(request)  # This returns bytes
        encrypted_request = self.encrypt_request(serialized_request)  # Encrypt the serialized request
        self.ss.send(encrypted_request.encode('utf-8'))  # Send encrypted data as bytes
        encrypted_response = self.ss.recv(4096).decode('utf-8')  # Receive response
        response = self.decrypt_response(encrypted_response)  # Decrypt the server's response
        print(response)



    def login(self, student_id):
        """
        Log in to the server using the student ID.
        """
        request = Request(action="login", student_id=student_id)
        encrypted_request = self.encrypt_request(RequestSerializer.encode(request))
        self.ss.send(encrypted_request.encode('utf-8'))  # Fix: Ensure the string is sent as bytes
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
        self.ss.send(encrypted_request.encode('utf-8'))  # Fix: Ensure the string is sent as bytes
        response = self.decrypt_response(self.ss.recv(4096).decode('utf-8'))
        print(response)

    def submit_request(self, content, approver_id):
        """
        Submit a request to the student's assigned staff member.
        """
        try:
            request = Request(action="submit_request", content=content, approver_id=approver_id, profile={"session_id": self.session_id})
            encrypted_request = self.encrypt_request(RequestSerializer.encode(request))
            self.ss.send(encrypted_request.encode('utf-8'))  # Fix: Ensure the string is sent as bytes
            response = self.decrypt_response(self.ss.recv(4096).decode('utf-8'))
            print(response)
        except ConnectionResetError:
            print("Error: Connection to server was lost.")
        except Exception as e:
            print(f"Unexpected error: {e}")
