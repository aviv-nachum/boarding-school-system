from Actions.Request import Request
from Clients.User import User
import json

class Student(User):
    def __init__(self, username, password, profile):
        super().__init__(username, password, "student", profile)

    def register(self, profile):
        request = Request(action="signupStudent", profile=profile.to_dict())
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        print(response)

    def login(self, student_id):
        request = Request(action="login", student_id=student_id)
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        response_data = json.loads(response)
        self.session_id = response_data.get("session_id")
        print(response_data.get("message"))

    def submit_request(self, content, approver_id):
        request = Request(
            action="submit_request",
            content=content,
            approver_id=approver_id,
            profile={"session_id": self.session_id}
        )
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        print(response)