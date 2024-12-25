from socket import *
from threading import Thread
from config import *
from Actions.Request import *

class Staff(Thread):
    def __init__(self):
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.ss.connect((HOST, PORT))
        print("Connected to the server as staff.")

    def register(self, profile):
        """
        Register a new staff profile with the server.
        """
        request = Request(action="signup", profile=profile)
        self.ss.sendall(RequestSerializer.encode(request))
        response = RequestSerializer.decode(self.ss)
        if response:
            print(response.content)

    def login(self, staff_id):
        """
        Log in to the server using the staff ID.
        """
        request = Request(action="login", student_id=staff_id)
        self.ss.sendall(RequestSerializer.encode(request))
        response = RequestSerializer.decode(self.ss)
        if response:
            print(response.content)

    def logout(self):
        """
        Log out from the server.
        """
        request = Request(action="logout")
        self.ss.sendall(RequestSerializer.encode(request))
        response = RequestSerializer.decode(self.ss)
        if response:
            print(response.content)

    def view_requests(self):
        """
        View requests assigned to this staff member.
        """
        request = Request(action="view_requests")
        self.ss.sendall(RequestSerializer.encode(request))
        response = RequestSerializer.decode(self.ss)
        if response:
            print(response.content)

    def approve_request(self, request_id):
        """
        Approve a specific request by ID.
        """
        request = Request(action="approve_request", request_id=request_id)
        self.ss.sendall(RequestSerializer.encode(request))
        response = RequestSerializer.decode(self.ss)
        if response:
            print(response.content)
