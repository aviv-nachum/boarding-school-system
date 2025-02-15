from socket import socket
from threading import Thread
from template_classes.encConnection import ClientEncConnection
from config import HOST, PORT
import base64
from Actions.Request import Request, RequestSerializer
import json

class User(Thread):
    def __init__(self, username, password, role, profile):
        super().__init__()
        self.username = username
        self.password = password
        self.role = role
        self.profile = profile
        self.conn = ClientEncConnection(HOST, PORT, socket())
        self.session_key = None
        self.session_id = None

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def run(self):
        print(f"Connected to the server as {self.role}.")

    def login(self, user_id):
        session_key_encoded = base64.b64encode(self.session_key).decode('utf-8')
        request = Request(action="login", student_id=user_id, session_key=session_key_encoded)
        serialized_request = RequestSerializer.encode(request)
        encrypted_request = self.conn.encrypt_request(serialized_request)
        self.conn.send(encrypted_request)
        try:
            encrypted_response = self.conn.recv(4096)
            if encrypted_response:
                response = self.conn.decrypt_response(encrypted_response)
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
        encrypted_request = self.conn.encrypt_request(serialized_request)
        self.conn.send(encrypted_request)
        encrypted_response = self.conn.recv(4096)
        response = self.conn.decrypt_response(encrypted_response)
        print(response)