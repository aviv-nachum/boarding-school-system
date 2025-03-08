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
        self.conn.start()  # Ensure the connection is properly started
        self.session_key = None
        self.old_session_key = None
        self.session_id = None

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def run(self):
        pass #print(f"Connected to the server as {self.role}.")

    def login(self, student_id):
        request = Request(action="login", user_id=student_id, role=self.role, username=self.username, password=self.password)
        self.conn.send_msg(request.to_json().encode('utf-8'))
        #response = self.conn.recv_msg().decode('utf-8')
        #response_data = json.loads(response)
        #self.session_id = response_data.get("session_id")
        #print(response_data.get("message"))

    def logout(self):
        request = Request(action="logout", profile=self.profile.to_dict(), role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))

        #session_key_encoded = base64.b64encode(self.session_key).decode('utf-8')
        #request = Request(action="logout", content={"session_id": self.session_id}, session_key=session_key_encoded, role=self.role)
        #serialized_request = RequestSerializer.encode(request)
        #self.conn.send_msg(serialized_request)
        
        #encrypted_response = self.conn.recv_msg()
        #response = json.loads(encrypted_response.decode('utf-8'))
        #print(response)