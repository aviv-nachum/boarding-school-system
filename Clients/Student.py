from config import HOST, PORT
from Actions.Request import Request
from Clients.User import User

class Student(User):
    def __init__(self, username, password, profile):
        super().__init__(username, password, "student", profile)

    def register(self, profile):
        request = Request(action="signupStudent", profile=profile.to_dict())
        self.send_request(request)
        response = self.receive_response()
        print(response.content)

    def login(self, student_id):
        request = Request(action="login", student_id=student_id)
        self.send_request(request)
        response = self.receive_response()
        self.session_id = response.content.get("session_id")
        print(response.content.get("message"))

    def submit_request(self, content, approver_id):
        request = Request(
            action="submit_request",
            content=content,
            approver_id=approver_id,
            profile={"session_id": self.session_id}
        )
        self.send_request(request)
        response = self.receive_response()
        print(response.content)