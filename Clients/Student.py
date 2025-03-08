from Actions.Request import Request
from Clients.User import User
import json

class Student(User):
    def __init__(self, username, password, profile):
        super().__init__(username, password, "student", profile)

    def register(self, profile):
        request = Request(action="signupStudent", profile=profile.to_dict(), role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))
#        response = self.conn.recv_msg().decode('utf-8')
#        print(response)

    def submit_request(self, content, approver_id):
        request = Request(
            action="submit_request",
            content=content,
            approver_id=approver_id,
            profile=self.profile.to_dict(),
            role=self.role
        )
        self.conn.send_msg(request.to_json().encode('utf-8'))
#        response = self.conn.recv_msg().decode('utf-8')
#        print(response)