from Actions.Request import Request, RequestSerializer
from Clients.User import User
from Profiles.Staff_Profile import Staff_Profile
from Profiles.Student_Profile import Student_Profile
from db_manager import store_in_DB, get_user

# Dictionary to map actions to their corresponding handler methods
action_handlers = {}

# Decorator for client handler functions
def client_action(cls):
    """
    Register the class's handle_action method to the action_handlers dictionary.
    """
    action_name = cls.action_name
    if action_name:
        action_handlers[action_name] = cls
    return cls

@client_action
class ProcessRegisterStudent:
    action_name = "signupStudent"

    def __init__(self, server, conn, cursor, db_conn):
        self.server = server
        self.conn = conn
        self.cursor = cursor
        self.db_conn = db_conn

    def handle_action(self, request):
        profile = Student_Profile.from_dict(request.profile)
        self.server.log(f"Processing registration for profile ID: {profile.id}")

        # Check if the ID already exists
        if get_user(profile.id):
            self.server.log(f"Registration failed: ID {profile.id} already exists.")
            response = Request(action="signup_response", content="Registration failed: ID already exists.")
        else:
            # Store the profile in the database
            user = User(username=profile.id, password=request.profile['password'], role="student", profile=profile)
            store_in_DB(user)
            self.server.log(f"Registration successful for profile ID: {profile.id}")
            response = Request(action="signup_response", content="Registration successful.")

        # Encrypt and send response
        try:
            encrypted_response = self.server.encrypt_response(
                RequestSerializer.encode(response),
                request.session_key
            )
            self.server.log(f"Encrypted response to be sent: {encrypted_response}")
            self.conn.sendall(encrypted_response)  # No .encode('utf-8') needed here since it's already bytes
        except Exception as e:
            self.server.log(f"Error encrypting or sending response: {e}")

@client_action
class ProcessRegisterStaff:
    action_name = "signupStaff"

    def __init__(self, server, conn, cursor, db_conn):
        self.server = server
        self.conn = conn
        self.cursor = cursor
        self.db_conn = db_conn

    def handle_action(self, request):
        profile = Staff_Profile.from_dict(request.profile)
        self.server.log(f"Processing registration for profile ID: {profile.id}")

        # Check if the ID already exists
        if get_user(profile.id):
            self.server.log(f"Registration failed: ID {profile.id} already exists.")
            response = Request(action="signup_response", content="Registration failed: ID already exists.")
        else:
            # Store the profile in the database
            user = User(username=profile.id, password=request.profile['password'], role="staff", profile=profile)
            store_in_DB(user)
            self.server.log(f"Registration successful for profile ID: {profile.id}")
            response = Request(action="signup_response", content="Registration successful.")

        # Encrypt and send response
        try:
            encrypted_response = self.server.encrypt_response(
                RequestSerializer.encode(response),
                request.session_key
            )
            self.server.log(f"Encrypted response to be sent: {encrypted_response}")
            self.conn.sendall(encrypted_response)  # No .encode('utf-8') needed here since it's already bytes
        except Exception as e:
            self.server.log(f"Error encrypting or sending response: {e}")

@client_action
class ProcessLogin:
    action_name = "login"

    def __init__(self, server, conn, cursor, db_conn):
        self.server = server
        self.conn = conn
        self.cursor = cursor
        self.db_conn = db_conn

    def handle_action(self, request):
        user = get_user(request.student_id)
        if user:
            self.conn.sendall(RequestSerializer.encode(Request(action="login_response", content="Login successful.", profile=user.profile.to_dict())))
        else:
            self.conn.sendall(RequestSerializer.encode(Request(action="login_response", content="Login failed: User not found.")))

@client_action
class ProcessLogout:
    action_name = "logout"

    def __init__(self, server, conn, cursor, db_conn):
        self.server = server
        self.conn = conn
        self.cursor = cursor
        self.db_conn = db_conn

    def handle_action(self, request):
        self.conn.sendall(RequestSerializer.encode(Request(action="logout_response", content="Logout successful.")))

@client_action
class ProcessSubmitRequest:
    action_name = "submit_request"

    def __init__(self, server, conn, cursor, db_conn):
        self.server = server
        self.conn = conn
        self.cursor = cursor
        self.db_conn = db_conn

    def handle_action(self, request):
        self.cursor.execute("""
            INSERT INTO exit_requests (student_id, content, approved, approver_id)
            VALUES (?, ?, ?, ?)
        """, (request.student_id, request.content, False, request.approver_id))
        self.db_conn.commit()
        self.conn.sendall(RequestSerializer.encode(Request(action="submit_request_response", content="Request submission sent.")))

@client_action
class ProcessApproveRequest:
    action_name = "approve_request"

    def __init__(self, server, conn, cursor, db_conn):
        self.server = server
        self.conn = conn
        self.cursor = cursor
        self.db_conn = db_conn

    def handle_action(self, request):
        self.cursor.execute("""
            UPDATE exit_requests SET approved = 1 WHERE id = ?
        """, (request.request_id,))
        self.db_conn.commit()
        self.conn.sendall(RequestSerializer.encode(Request(action="approve_request_response", content="Approval request sent.")))

@client_action
class ProcessViewRequests:
    action_name = "view_requests"

    def __init__(self, server, conn, cursor, db_conn):
        self.server = server
        self.conn = conn
        self.cursor = cursor
        self.db_conn = db_conn

    def handle_action(self, request):
        self.cursor.execute("""
            SELECT * FROM exit_requests WHERE approver_id = ?
        """, (request.student_id,))
        requests = self.cursor.fetchall()
        response = [{"id": r[0], "student_id": r[1], "content": r[2], "approved": bool(r[3])} for r in requests]
        self.conn.sendall(RequestSerializer.encode(Request(action="view_requests_response", content=response)))
