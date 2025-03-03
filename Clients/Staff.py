from Actions.Request import Request
from Clients.User import User

class Staff(User):
    def __init__(self, username, password, profile):
        super().__init__(username, password, "staff", profile)

    def view_requests(self):
        request = Request(action="view_requests", role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        #print(response)

    def approve_request(self, request_id):
        request = Request(action="approve_request", request_id=request_id, role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        #print(response)