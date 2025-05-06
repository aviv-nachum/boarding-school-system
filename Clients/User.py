"""
Defines the base User class for clients in the boarding school system.
"""

from socket import socket
from threading import Thread
from Encryption_handeling.encConnection import ClientEncConnection
from config import HOST, PORT
from Actions.Request import Request, RequestSerializer

class User(Thread):
    """
    Represents a base user in the boarding school system.
    """
    def __init__(self, username, password, role, profile):
        """
        Initializes a User object.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
            role (str): The role of the user (e.g., "student", "staff").
            profile (Profile): The profile object associated with the user.
        """
        super().__init__()
        self.username = username
        self.password = password
        self.role = role
        self.profile = profile
        self.conn = ClientEncConnection(HOST, PORT, socket())
        self.conn.start()  # Ensure the connection is properly started
        self.session_key = None
        self.old_session_key = None
        self.session_id = None

    def set_password(self, password):
        """
        Sets a new password for the user.

        Args:
            password (str): The new password to set.
        """
        self.password = password

    def check_password(self, password):
        """
        Checks if the provided password matches the user's password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.password == password

    def run(self):
        pass # Placeholder for the thread's run method

    def login(self, student_id):
        """
        Sends a login request to the server.

        Args:
            student_id (str): The ID of the student logging in.
        """
        request = Request(
            action="login",
            user_id=student_id,
            role=self.role,
            username=self.username,
            password=self.password
        )
        self.conn.send_msg(request.to_json().encode('utf-8'))

    def logout(self):
        """
        Sends a logout request to the server.
        """
        request = Request(action="logout", profile=self.profile.to_dict(), role=self.role)
        self.conn.send_msg(request.to_json().encode('utf-8'))