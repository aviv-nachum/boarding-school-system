from Actions.Request import Request
from Clients.User import User

class Staff(User):
    def __init__(self, username, password, profile):
        super().__init__(username, password, "staff", profile)

    def view_requests(self):
        request = Request(action="view_requests")
        self.send_request(request)
        response = self.receive_response()
        print(response.content)

    def approve_request(self, request_id):
        request = Request(action="approve_request", request_id=request_id)
        self.send_request(request)
        response = self.receive_response()
        print(response.content)