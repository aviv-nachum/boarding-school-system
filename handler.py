from socket import socket
import json
from typing import Any
from AuthDB import User, store_in_DB, remove_from_DB, get_user
from encConnection import ServerEncConnection
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import base64
from icecream import ic

import jwt

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

    """
    A class to handle client-server communication, including user authentication and role-based actions.
    """

    def __init__(self, conn: socket) -> None:
        """
        Initialize the Handler instance.

        Args:
            conn (socket): A socket connection to the client.
        """
        self.conn = conn
        self.active_user: User | None = None
        self.active_user_name: str | None = None
        self.active_role: list[str] = ["guest"]
        with open("Templates_Ex/sign_rsa_privatekey", "rb") as key_file:
            self.sign_rsa_key = RSA.import_key(key_file.read())

    def recvall(self, length: int) -> bytes:
        """
        Receive exactly the specified number of bytes from the client.

        Args:
            length (int): The number of bytes to receive.

        Returns:
            bytes: The received data.
        """
        ans = b""
        while len(ans) < length:
            chunk = self.conn.recv(length - len(ans))
            if not chunk:
                raise IOError("Connection closed before receiving expected data.")
            ans += chunk
        return ans

    def sendall(self, data: bytes) -> None:
        """
        Send all data to the client.

        Args:
            data (bytes): The data to send.
        """
        self.conn.sendall(data)

    def send_msg(self, request: bytes):
        """
        Send a message to the client with length prefix.

        Args:
            request (bytes): The message to send.
        """
        req_len = int.to_bytes(len(request), 4, "big")
        self.sendall(req_len)
        self.sendall(request)

    def recv_msg(self):
        """
        Receive a message from the client with length prefix.

        Returns:
            bytes: The received message.
        """
        req_len = int.from_bytes(self.recvall(4), "big")
        return self.recvall(req_len)

    def start(self):
        pass

    def handle_forever(self) -> None:
        """
        Continuously handle incoming client requests.
        """
        while True:
            try:
                request = self.recv_msg()
                self.handle_request(request)
            except IOError as error:
                print(f"IOError: {error}")
                return

    def handle_request(self, request: bytes):
        """
        Handle a client request by parsing JSON and invoking the appropriate action.

        Args:
            request (bytes): The raw request data from the client.
        """
        req: dict[str, Any] = json.loads(request)
        action: str = req.get("action", None)
        self.active_user = None
        self.set_active_user(req)

        if not action:
            self.send_error("no action specified")
            return
        if not self.permit_action(action):
            self.send_error(f"not permitted to perform action {action}")
            return
        elif action == "login":
            self.handle_login(req)

        elif action == "signup":
            self.handle_signup(req)

        elif action == "remove_user":
            self.handle_remove_user(req)

    def handle_signup(self, req: dict[str, Any]):
        """
        Handle user signup requests.

        Args:
            req (dict[str, Any]): The request data containing "username" and "password".
        """
        username = req.get("username", None)
        password = req.get("password", None)

        if (not username) or (not password):
            self.send_error("must give username and password for login")
            return
        if not self._sanitize_input(username) or not self._sanitize_input(password):
            self.send_error("invalid characters in username or password")
            return
        if get_user(username):
            self.send_error("there already exist a user with that username")
            return
        user = User(username=username)
        user.set_password(password)
        store_in_DB(user)

        self.send_sucsess(f"user {username} added")

    def handle_login(self, req: dict[str, Any]):
        """
        Handle user login requests.

        Args:
            req (dict[str, Any]): The request data containing "username" and "password".
        """
        username = req.get("username", None)
        password = req.get("password", None)
        if (not username) or (not password):
            self.send_error("must give username and password for login")
            return
        if not self._sanitize_input(username) or not self._sanitize_input(password):
            self.send_error("invalid characters in username or password")
            return
        user = get_user(username)
        if not user:
            self.send_error("username doesn't exist")
            return
        if not user.check_password(password):
            self.send_error("Invalid password")
            return
        cookie = self.generate_login_cookie(user.username)
        self.send_msg(cookie.encode())

    def handle_remove_user(self, req: dict[str, Any]):
        """
        Handle requests to remove a user.

        Args:
            req (dict[str, Any]): The request data containing "user_to_remove".
        """
        if (not self.active_user) or (not self.active_user.is_admin()):
            self.send_error("must be login as admin to remove user")
            return
        if not "user_to_remove" in req:
            self.send_error("request must contain user_to_remove field")
        user = get_user(req["user_to_remove"])
        remove_from_DB(user)
        self.send_sucsess(f"user {req['user_to_remove']} was removed")

    def set_active_user(self, req: dict[str, Any]) -> str | None:
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
        if login_cookie == None:
            return
        elif not self.check_cookie(json.dumps(login_cookie)):
            self.send_error("Invalid Signature, Cyber detected 🐮🤥😡")
            return
        else:
            active_user_name = login_cookie["cookie"]["username"]
            self.active_user = get_user(active_user_name)
            if self.active_user:
                self.active_role = self.active_user.role

    def send_error(self, error_msg: str):
        """
        Send an error message to the client.

        Args:
            error_msg (str): The error message to send.
        """
        self.send_msg(
            json.dumps({"status": "error", "descryption": error_msg}).encode()
        )

    def send_sucsess(self, succsess_msg: str):
        """
        Send a success message to the client.

        Args:
            succsess_msg (str): The success message to send.
        """
        self.send_msg(
            json.dumps({"status": "sucsess", "descryption": succsess_msg}).encode()
        )

    def generate_login_cookie(self, username: str) -> str:
        """
        Generate a login cookie for the user.

        Args:
            username (str): The username for which to generate the cookie.

        Returns:
            str: The generated cookie as a JSON string.
        """
        cookie = {}
        cookie["name"] = "login"
        cookie["username"] = username
        signature = base64.b64encode(self.sign(json.dumps(cookie).encode())).decode()
        ans = json.dumps({"signature": signature, "cookie": cookie})
        assert self.check_cookie(ans)
        return ans

    def check_cookie(self, cookie_json: str) -> bool:
        """
        Verify the validity of a login cookie.

        Args:
            cookie_json (str): The JSON representation of the cookie.

        Returns:
            bool: True if the cookie is valid, False otherwise.
        """
        try:
            cookie = json.loads(cookie_json)
            cookie_data = json.dumps(cookie["cookie"]).encode()
            cookie_signature = base64.b64decode(cookie["signature"].encode())
            return self.verify(cookie_data, cookie_signature)
        except (json.JSONDecodeError, ValueError, KeyError, TypeError):
            return False

    def sign(self, data: bytes) -> bytes:
        """
        Create a digital signature for the given data.

        Args:
            data (bytes): The data to sign.

        Returns:
            bytes: The generated digital signature.
        """
        sign_hash = SHA256.new(data)
        signature = pkcs1_15.new(self.sign_rsa_key).sign(sign_hash)
        return signature

    def verify(self, data: bytes, signature: bytes):
        """
        Verify a digital signature.

        Args:
            data (bytes): The original data.
            signature (bytes): The digital signature to verify.

        Returns:
            bool: True if the signature is valid, False otherwise.
        """
        try:
            hashed_msg = SHA256.new(data)
            signature = pkcs1_15.new(self.sign_rsa_key).verify(hashed_msg, signature)
            return True
        except (ValueError, TypeError):
            return False

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

    def _sanitize_input(self, value: str) -> bool:
        """
        Sanitize user input to prevent potential security issues.

        Args:
            value (str): The input value to sanitize.

        Returns:
            bool: True if the input is valid, False otherwise.
        """
        return value.isalnum()
