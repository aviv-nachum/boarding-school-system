from socket import *
from threading import Thread
from config import *
from Request import Request, RequestSerializer

class Staff(Thread):
    def __init__(self):
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.ss.connect((HOST, PORT))
        print("Connected to the server as staff.")

    def register(self, profile):
        request = Request(action="signup", profile=profile)
        self.ss.sendall(RequestSerializer.encode(request))
        print("Registration request sent.")

    def login(self, staff_id):
        request = Request(action="login", student_id=staff_id)
        self.ss.sendall(RequestSerializer.encode(request))
        print("Login request sent.")

    def logout(self):
        request = Request(action="logout")
        self.ss.sendall(RequestSerializer.encode(request))
        print("Logout request sent.")

    def view_requests(self):
        request = Request(action="view_requests")
        self.ss.sendall(RequestSerializer.encode(request))
        print("Request to view submissions sent.")

    def approve_request(self, request_id):
        request = Request(action="approve_request", request_id=request_id)
        self.ss.sendall(RequestSerializer.encode(request))
        print("Approval request sent.")
