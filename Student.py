from socket import *
from threading import Thread
from config import *
from Request import *

class Student(Thread): # 
    def __init__(self):
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.ss.connect((HOST, PORT))
        print("Connected to the server as a student.")

    def register(self, profile):
        """
        Register a new student profile with the server.
        """
        request = Request(action="signup", profile=profile)
        self.ss.sendall(RequestSerializer.encode(request))
        response = RequestSerializer.decode(self.ss)
        if response:
            print(response.content)

    def login(self, student_id):
        """
        Log in to the server using the student ID.
        """
        request = Request(action="login", student_id=student_id)
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

    def submit_request(self, content, approver_id = self.profile["head_teacher_id"]): # approver_id = self.profile["head_teacher_id"]
        """
        Submit a request to the student's assigned staff member.
        """
        try:
            request = Request(action="submit_request", content=content, approver_id=approver_id)
            self.ss.sendall(RequestSerializer.encode(request))
            response = RequestSerializer.decode(self.ss)
            if response:
                print(response.content)
        except ConnectionResetError:
            print("Error: Connection to server was lost.")
        except Exception as e:
            print(f"Unexpected error: {e}")
