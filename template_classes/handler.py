import json
import socket
from typing import Any
from template_classes.encConnection import ServerEncConnection
import jwt
from template_classes.API import API
import datetime


permissions: dict[str, list[str]] = {
    "signup": ["guest", "student", "staff"],
    "login": ["guest"],
    "remove_user": ["staff"],
    "logout": ["student", "staff"],
    "submit_request": ["student"],
    "approve_request": ["staff"],
    "view_requests": ["staff"],
}


class Handler:
    def __init__(self, conn : socket, host, port):
        self.conn = ServerEncConnection(host, port, conn)
        self.host = host
        self.key="secret"
        self.api:API = API()


    def handle_request(self, request: bytes):
        """
        Handle a client request by parsing JSON and invoking the appropriate action.

        Args:
            request (bytes): The raw request data from the client.
        """
        req: dict[str, Any] = json.loads(request)
        action: str = req.get("action", None)
        self.active_user = None
        self.set_active_user_name(req)

        if not action:
            #self.send_error("no action specified")
            return
        if not self.permit_action(action):
            #self.send_error(f"not permitted to perform action {action}")
            return
        elif action == "login":
            self.handle_login(req)

        elif action == "signup":
            self.handle_signup(req)

        elif action == "remove_user":
            self.handle_remove_user(req)
        
        elif action == "logout":
            self.handle_logout(req)

        elif action == "submit_request":
            self.handle_submit_request(req)

        elif action == "approve_request":
            self.handle_approve_request(req)

        elif action == "view_requests":
            self.handle_view_requests(req)

    def handle_signup(self, req: dict[str, Any]):
        """
        Handle user signup requests.

        Args:
            req (dict[str, Any]): The request data containing "username" and "password".
        """
        username = req.get("username", None)
        email = req.get("email", None)
        password = req.get("password", None)
        if (not username) or (not password):
            #self.send_error("must give username and password for login")
            return
        self.api.sign_up(username, email, password)
        #self.send_sucsess(f"user {username} added")

    def set_active_user_name(self, req: dict[str, Any]) -> str | None:
        """
        Validate and set the active user based on a login cookie.

        Args:
            req (dict[str, Any]): The request data containing "login_cookie".

        Returns:
            str | None: The username of the active user, or None if validation fails.
        """
        self.active_user = None
        self.active_role = "guest"
        login_cookie = req.get("login_cookie", None)
        try:
            if login_cookie == None:
                return
            cookie=jwt.decode(login_cookie, self.key, algorithms="HS256", options={"verify_signature": True})
            active_email = cookie["email"]
            self.active_user = self.api.get_user(active_email) #API REF
            if self.active_user:
                self.active_role = self.active_user.role
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError, jwt.exceptions.InvalidTokenError, jwt.exceptions.ExpiredSignatureError) as e:
            print(f"Cookie error: {e}")

    def handle_forever(self) -> None:
        """
        Continuously handle incoming client requests.
        """
        self.conn.start()
        print("server up and running")
        while True:
            try:
                request =self.conn.recv_msg().decode("utf-8")
                self.handle_request(request)
            except IOError as error:
                print(f"IOError: {error}")
                return
            
    def permit_action(self, action: str) -> bool:
        """
        Check if the active user has permission to perform the specified action.

        Args:
            action (str): The action to check.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if action not in permissions:
            return False
        return self.active_role in permissions[action]
    
    def create_cookie(self, username:str, email:str):
        """
        Creates a cookie for the client when when he logs in
        
        Args:
            username (str): Name of user
            email (str): Email of the user

        Return:
            JSON Web Token
        """
        cookie = {}
        cookie["name"] = "login"
        cookie["username"] = username
        cookie["email"] = email
        cookie["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
        ans=jwt.encode(cookie, self.key , algorithm="HS256")
        # assert self.check_cookie(ans)
        return ans
    
    def handle_login(self, req: dict[str, Any]):
        """
        Handle user login requests.

        Args:
            req (dict[str, Any]): The request data containing "email" and "password".
        """
        email = req.get("email", None)
        password = req.get("password", None)
        if (not email) or (not password):
            print("problem")
            #self.send_error("must give username and password for login")
            return
        user = self.api.get_user(email) #  API REF
        if not user:
            print("no user exist")
            #self.send_error("username doesn't exist")
            return
        if not self.api.check_password(user,password):
            print("another problem")
            #self.send_error("Invalid password")
            return
        cookie = self.create_cookie(self.api.check_name(user), email)
        self.conn.send_msg(cookie.encode("utf-8"))

    def handle_remove_user(self, req: dict[str, Any]):
        """
        Handle requests to remove a user.

        Args:
            req (dict[str, Any]): The request data containing "user_to_remove".
        """
        if not "user_to_remove" in req:
            print("No user to delete")
        user = self.api.get_user(req["user_to_remove"])
        self.api.delete_user(user)

    def handle_logout(self, req: dict[str, Any]):
        """
        Handle user logout requests.
        Sends the client a wrong cookie to hopefully deny them accses to the user.

        Args:
            req (dict[str, Any]): The request data containing "login_cookie".
        """
        encCookie = req.get("login_cookie", None)
        cookie=jwt.decode(encCookie, self.key, algorithms="HS256", options={"verify_signature": True})
        cookie["exp"] = datetime.datetime.now(tz=datetime.timezone.utc)
        encCookie=jwt.encode(cookie, self.key , algorithm="HS256")
        self.conn.send_msg(encCookie.encode("utf-8"))

    def handle_submit_request(self, req: dict[str, Any]):
        try:
            self.cursor.execute("""
                INSERT INTO exit_requests (student_id, content, approved, approver_id)
                VALUES (?, ?, ?, ?)
            """, (req["student_id"], req["content"], False, req["approver_id"]))
            self.db_conn.commit()
            self.conn.send_msg(json.dumps({"status": "success"}).encode())
        except Exception as e:
            self.conn.send_msg(json.dumps({"status": "error", "desc": str(e)}).encode())

    def handle_approve_request(self, req: dict[str, Any]):
        try:
            self.cursor.execute("""
                UPDATE exit_requests SET approved = 1 WHERE id = ?
            """, (req["request_id"],))
            self.db_conn.commit()
            self.conn.send_msg(json.dumps({"status": "success"}).encode())
        except Exception as e:
            self.conn.send_msg(json.dumps({"status": "error", "desc": str(e)}).encode())

    def handle_view_requests(self, req: dict[str, Any]):
        try:
            self.cursor.execute("""
                SELECT * FROM exit_requests WHERE approver_id = ?
            """, (req["approver_id"],))
            requests = self.cursor.fetchall()
            response = [{"id": r[0], "student_id": r[1], "content": r[2], "approved": bool(r[3])} 
                       for r in requests]
            self.conn.send_msg(json.dumps(response).encode())
        except Exception as e:
            self.conn.send_msg(json.dumps({"status": "error", "desc": str(e)}).encode())
