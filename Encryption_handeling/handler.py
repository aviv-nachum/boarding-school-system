"""
Handles incoming requests and manages user permissions for the boarding school system.
"""

from typing import Any
from Encryption_handeling.encConnection import ServerEncConnection
from Encryption_handeling.API import API
from Actions.Actions import action_handlers
import json
import jwt
import datetime

# Define permissions for each action based on user roles
permissions: dict[str, list[str]] = {
    "signupStudent": ["guest", "student", "staff"],
    "signupStaff": ["guest", "student", "staff"],
    "login": ["guest"],
    "remove_user": ["staff"],
    "logout": ["student", "staff"],
    "submit_request": ["student"],
    "approve_request": ["staff"],
    "view_requests": ["staff"],
    "view_approved_requests": ["staff"],
}

class Handler:
    """
    Handles client requests and manages user sessions.
    """
    def __init__(self, conn, host, port):
        """
        Initializes the Handler with a connection and server details.

        Args:
            conn (ServerEncConnection): The encrypted server connection.
            host (str): The host address of the server.
            port (int): The port number of the server.
        """
        self.conn = ServerEncConnection(host, port, conn)
        self.host = host
        self.key = "secret"
        self.api = API()
        self.active_role = "guest"
        self.active_user = None  # Tracks the currently active user

    def handle_request(self, request: bytes):
        """
        Processes an incoming request from the client.

        Args:
            request (bytes): The raw request data received from the client.
        """
        #print("Handling request...")
        req: dict[str, Any] = json.loads(request)
        #print(f"Request: {req}")
        if req.get("profile", None) and req.get("profile", None).get("role", None):
            self.active_role = req.get("profile", None).get("role", None)
        #print(f"Active role: {self.active_role}")
        action: str = req.get("action", None)
        self.active_user = None
        self.set_active_user_name(req)

        if not action:
            print("No action specified in the request.")
            return
        if not self.permit_action(action):
            print(f"Action '{action}' is not permitted.")
            return
        elif action in action_handlers:
#            #print(f"Executing action handler for '{action}'...")
            action_handlers[action](self, req)

    def set_active_user_name(self, req: dict[str, Any]) -> str | None:
        """
        Sets the active user's name based on the request.

        Args:
            req (dict[str, Any]): The request data.

        Returns:
            str | None: The username of the active user, or None if not set.
        """
        self.active_user = None
        cookie = req.get("cookie", None)
        try:
            if cookie is None:
                #print("No cookie found in the request.")
                return
            decoded_cookie = jwt.decode(cookie, self.key, algorithms="HS256", options={"verify_signature": True})
            active_username = decoded_cookie["username"]
            self.active_user = self.api.get_user(active_username)
            if self.active_user:
                self.active_role = self.active_user.role
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError, jwt.exceptions.InvalidTokenError, jwt.exceptions.ExpiredSignatureError) as e:
            print(f"Cookie error: {e}")

    def handle_forever(self) -> None:
        """
        Continuously handles incoming requests from the client.
        """
        self.conn.start()
#        #print("Server up and running")
        while True:
            try:
                request = self.conn.recv_msg()
#                #print(f"Received request: {request}")
                self.handle_request(request)
            except IOError as error:
                print(f"Connection error: {error}")
                break  # Exit the loop if there's a connection error

    def permit_action(self, action: str) -> bool:
        """
        Checks if the active user has permission to perform the specified action.

        Args:
            action (str): The action to check permissions for.

        Returns:
            bool: True if the action is permitted, False otherwise.
        """
        if action not in permissions:
            print(f"Action '{action}' not found in permissions.")
            return False
#print(f"#Checking permissions of {self.active_role} for action '{action}'...")
        return self.active_role in permissions[action]

    def create_cookie(self, username: str, id: int):
        """
        Creates a JWT cookie for the user.

        Args:
            username (str): The username of the user.
            id (int): The user ID.

        Returns:
            str: The encoded JWT cookie.
        """
        cookie = {
            "username": username,
            "id": id,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        return jwt.encode(cookie, self.key, algorithm="HS256")
