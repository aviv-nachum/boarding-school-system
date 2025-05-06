"""
Defines the Student client class for interacting with the server.
"""

from Actions.Request import Request
from Clients.User import User

class Student(User):
    """
    Represents a student client in the boarding school system.
    """
    def __init__(self, username, password, profile):
        """
        Initializes a Student object.

        Args:
            username (str): The username of the student.
            password (str): The password of the student.
            profile (Profile): The profile object associated with the student.
        """
        super().__init__(username, password, "student", profile)

    def register(self, profile):
        """
        Sends a registration request to the server.

        Args:
            profile (Profile): The profile data to register.
        """
        request = Request(action="signupStudent", profile=profile.to_dict(), role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))

    def submit_request(self, content, approver_id):
        """
        Sends a request submission to the server.

        Args:
            content (str): The content of the request.
            approver_id (str): The ID of the approver.
        """
        request = Request(
            action="submit_request",
            content=content,
            approver_id=approver_id,
            profile=self.profile.to_dict(),
            role=self.role
        )
        self.conn.send_msg(request.to_json().encode('utf-8'))