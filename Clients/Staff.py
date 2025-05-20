"""
Defines the Staff client class for interacting with the server.
"""

from Actions.Request import Request
from Clients.User import User
import json

class Staff(User):
    """
    Represents a staff client in the boarding school system.
    """
    def __init__(self, username, password, profile):
        """
        Initializes a Staff object.

        Args:
            username (str): The username of the staff member.
            password (str): The password of the staff member.
            profile (Profile): The profile object associated with the staff member.
        """
        super().__init__(username, password, "staff", profile)
        self.cookie = None  # Store the cookie received during login

    def login(self, staff_id):
        """
        Sends a login request to the server.

        Args:
            staff_id (str): The ID of the staff member.
        """
        # Create a login request with the staff ID, username, and password
        request = Request(
            action="login",
            user_id=staff_id,
            role=self.role,
            username=self.username,
            password=self.password
        )
        # Send the login request to the server
        self.conn.send_msg(request.to_json().encode('utf-8'))
        response = self.conn.recv_msg().decode('utf-8')
        response_data = json.loads(response)
        self.cookie = response_data.get("cookie")  # Save the cookie for future requests
        #print(response_data.get("message"))

    def register(self, profile):
        """
        Sends a registration request to the server.

        Args:
            profile (Profile): The profile data to register.
        """
        # Create a registration request with the staff profile
        request = Request(action="signupStaff", profile=profile.to_dict(), role=self.role)
        # Send the registration request to the server
        self.conn.send_msg(request.to_json().encode('utf-8'))
        
    def view_requests(self):
        """
        Fetches the list of pending exit requests from the server.

        Returns:
            list[dict]: A list of pending requests, where each request is a dictionary.
        """
        # Send a request to the server to fetch pending requests
        request = Request(action="view_requests", role=self.role, profile=self.profile.to_dict(), cookie=self.cookie)
        self.conn.send_msg(request.to_json().encode('utf-8'))

        # Receive the response from the server
        response = self.conn.recv_msg().decode('utf-8')
        response_data = json.loads(response)

        if response_data.get("status") == "success":
            return response_data.get("requests", [])
        else:
            print(f"Error: {response_data.get('message')}")
            return []

    def approve_request(self, request_id):
        """
        Sends a request to the server to approve a specific exit request.

        Args:
            request_id (int): The ID of the request to approve.
        """
        # Send an approval request to the server
        request = Request(action="approve_request", request_id=request_id, role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))

        # Receive the response from the server
        response = self.conn.recv_msg().decode('utf-8')
        if response == "success":
            print(f"Request ID {request_id} approved successfully.")
        else:
            print(f"Failed to approve Request ID {request_id}.")

    def view_approved_requests(self):
        """
        Fetches the list of approved exit requests from the server.

        Returns:
            list[dict]: A list of approved requests, where each request is a dictionary.
        """
        # Send a request to the server to fetch approved requests
        request = Request(action="view_approved_requests", role=self.role, profile=self.profile.to_dict(), cookie=self.cookie)
        self.conn.send_msg(request.to_json().encode('utf-8'))

        # Receive the response from the server
        response = self.conn.recv_msg().decode('utf-8')
        response_data = json.loads(response)

        if response_data.get("status") == "success":
            return response_data.get("requests", [])
        else:
            print(f"Error: {response_data.get('message')}")
            return []