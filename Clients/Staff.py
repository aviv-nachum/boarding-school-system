from Actions.Request import Request
from Clients.User import User
import json

class Staff(User):
    def __init__(self, username, password, profile):
        super().__init__(username, password, "staff", profile)
        self.cookie = None  # Store the cookie received during login

    def login(self, staff_id):
        request = Request(action="login", user_id=staff_id, role=self.role, username=self.username, password=self.password)
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        response_data = json.loads(response)
        self.cookie = response_data.get("cookie")  # Save the cookie for future requests
        #print(response_data.get("message"))

    def register(self, profile):
        request = Request(action="signupStaff", profile=profile.to_dict(), role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))

    def view_requests(self):
        request = Request(action="view_requests", role=self.role, profile=self.profile.to_dict(), cookie=self.cookie)
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        response_data = json.loads(response)

        if response_data.get("status") == "success":
            requests = response_data.get("requests", [])
            if requests:
                print("\n--- Exit Requests ---")
                for req in requests:
                    print(f"Request ID: {req['id']}, Student ID: {req['student_id']}, Content: {req['content']}, Approved: {req['approved']}")
            else:
                print("No exit requests found.")
        else:
            print(f"Error: {response_data.get('message')}")

    def approve_request(self, request_id):
        request = Request(action="approve_request", request_id=request_id, role=self.role)
        request.cookie = self.cookie  # Include the cookie in the request
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        #print(response)