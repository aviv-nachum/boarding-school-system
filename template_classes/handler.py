from typing import Any
from template_classes.encConnection import ServerEncConnection
from template_classes.API import API
from Actions.Actions import action_handlers
import json
import jwt
import datetime

permissions: dict[str, list[str]] = {
    "signupStudent": ["guest", "student", "staff"],
    "signupStaff": ["guest", "student", "staff"],
    "login": ["guest"],
    "remove_user": ["staff"],
    "logout": ["student", "staff"],
    "submit_request": ["student"],
    "approve_request": ["staff"],
    "view_requests": ["staff"],
}

class Handler:
    def __init__(self, conn, host, port):
        self.conn = ServerEncConnection(host, port, conn)
        self.host = host
        self.key = "secret"
        self.api = API()
        self.active_role = "guest"
        self.active_user = None

    def handle_request(self, request: bytes):
#        #print("Handling request...")
        req: dict[str, Any] = json.loads(request)
        if req.get("profile", None) and req.get("profile", None).get("role", None):
            self.active_role = req.get("profile", None).get("role", None)
#        #print(f"Active role: {self.active_role}")
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
        self.active_user = None
        cookie = req.get("cookie", None)
        try:
            if cookie is None:
                return
            cookie = jwt.decode(cookie, self.key, algorithms="HS256", options={"verify_signature": True})
            active_username = cookie["username"]
            self.active_user = self.api.get_user(active_username)
            if self.active_user:
                self.active_role = self.active_user.role
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError, jwt.exceptions.InvalidTokenError, jwt.exceptions.ExpiredSignatureError) as e:
            print(f"Cookie error: {e}")

    def handle_forever(self) -> None:
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
        if action not in permissions:
            print(f"Action '{action}' not found in permissions.")
            return False
#print(f"#Checking permissions of {self.active_role} for action '{action}'...")
        return self.active_role in permissions[action]

    def create_cookie(self, username: str, id: int):
        cookie = {
            "username": username,
            "id": id,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        return jwt.encode(cookie, self.key, algorithm="HS256")
