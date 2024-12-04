from socket import *
from threading import Thread
from config import *
from Request import Request, RequestSerializer

class Student(Thread):
    def __init__(self):
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.ss.connect((HOST, PORT))
        print("Connected to the server as a student.")

    def register(self, profile):
        request = Request(action="signup", profile=profile)
        self.ss.sendall(RequestSerializer.encode(request))
        print("Registration request sent.")

    def login(self, student_id):
        request = Request(action="login", student_id=student_id)
        self.ss.sendall(RequestSerializer.encode(request))
        print("Login request sent.")

    def logout(self):
        try:
            request = Request(action="logout")
            self.ss.sendall(RequestSerializer.encode(request))
            print("Logout request sent.")
        except ConnectionResetError:
            print("Connection lost during logout.")

    def submit_request(self, content, approver_id):
        try:
            request = Request(action="submit_request", content=content, approver_id=approver_id)
            self.ss.sendall(RequestSerializer.encode(request))
            print("Request submission sent.")
        except ConnectionResetError:
            print("Error: Connection to server was lost.")
