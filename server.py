from socket import *
from threading import Thread, Lock
from config import *
from Request import Request, RequestSerializer
from Profile import Profile  # Import the Profile class
import sqlite3
import time

lock = Lock()

# Retry mechanism for database operations
def execute_with_retry(cursor, query, params=(), retries=3, delay=0.1):
    """
    Execute a database query with retry logic to handle locked database errors.
    """
    for _ in range(retries):
        try:
            cursor.execute(query, params)
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(delay)
            else:
                raise
    raise sqlite3.OperationalError("Failed to execute query after retries: database is locked.")

# Decorator for client handler functions
def client_action(func):
    """
    Decorator for client handler functions to log actions and handle exceptions gracefully.
    """
    def wrapper(self, request, conn, *args, **kwargs):
        try:
            self.log(f"Executing {func.__name__} for action '{request.action}'")
            return func(self, request, conn, *args, **kwargs)  # Pass correct arguments
        except Exception as e:
            self.log(f"Error in {func.__name__}: {e}")
            error_response = Request(action="error", content=f"Error: {str(e)}")
            conn.sendall(RequestSerializer.encode(error_response))
    return wrapper

class Server(Thread):
    """
    Server class to manage client connections and handle requests.
    """
    def __init__(self):
        reset_database()
        super().__init__()
        self.addr = (HOST, PORT)
        self.init_db()

    def init_db(self):
        """
        Initialize the database and set up the necessary tables.
        """
        self.db_connection = sqlite3.connect('system.db', check_same_thread=False)
        self.db_connection.execute("PRAGMA journal_mode=WAL;")
        cursor = self.db_connection.cursor()

        # Update the profiles table to use a serialized_profile column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY,
                serialized_profile TEXT
            )
        """)

        # Create exit requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exit_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                content TEXT,
                approved BOOLEAN,
                approver_id INTEGER
            )
        """)
        self.db_connection.commit()

    def log(self, message):
        """
        Thread-safe logging to avoid overlapping messages with interactive menus.
        """
        with lock:
            print(message)

    def run(self):
        """
        Start the server, accept new connections, and spawn threads to handle clients.
        """
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind(self.addr)
        self.s.listen(5)
        self.log("Server is running...")

        while True:
            try:
                conn, addr = self.s.accept()
                self.log(f"Connection from {addr}")
                Thread(target=self.client_handler, args=(conn,)).start()
            except Exception as e:
                self.log(f"Server error: {e}")
                break

    def client_handler(self, conn):
        """
        Handle communication with a specific client.
        Each client runs in its own thread with a separate database connection.
        """
        thread_db_conn = sqlite3.connect('system.db')
        thread_cursor = thread_db_conn.cursor()

        # Map actions to their corresponding handler methods
        action_handlers = {
            "signup": self.process_register,
            "login": self.process_login,
            "logout": self.process_logout,
            "submit_request": self.process_request_submission,
            "approve_request": self.process_request_approval,
            "view_requests": self.process_view_requests,
        }

        while True:
            try:
                # Decode the client request
                request = RequestSerializer.decode(conn)
                if not request:
                    self.log("Client disconnected.")
                    break

                self.log(f"Received action '{request.action}' from client.")

                # Find the appropriate handler for the action
                handler = action_handlers.get(request.action)
                if handler:
                    handler(request, conn, thread_cursor, thread_db_conn)
                else:
                    self.log(f"Unknown action: {request.action}")
                    conn.sendall(RequestSerializer.encode(Request(action="error", content="Unknown action.")))

            except ConnectionResetError:
                self.log("Client forcibly disconnected.")
                break
            except Exception as e:
                self.log(f"Error handling client: {e}")
                break

        conn.close()
        thread_db_conn.close()
        self.log("Client handler thread terminated.")

    @client_action
    def process_register(self, request, conn, cursor, db_conn):
        """
        Handle student or staff registration using the Profile class.
        """
        profile = Profile.from_dict(request.profile)
        self.log(f"Processing registration for profile ID: {profile.id}")

        # Check if the ID already exists
        cursor.execute("SELECT id FROM profiles WHERE id = ?", (profile.id,))
        if cursor.fetchone():
            self.log(f"Registration failed: ID {profile.id} already exists.")
            conn.sendall(RequestSerializer.encode(Request(action="signup_response", content="Registration failed: ID already exists.")))
            return

        # Serialize the profile and store it in the database
        serialized_profile = Profile.encode(profile).decode('utf-8')
        cursor.execute("""
            INSERT INTO profiles (id, serialized_profile)
            VALUES (?, ?)
        """, (profile.id, serialized_profile))
        db_conn.commit()

        self.log(f"Registration successful for profile ID: {profile.id}")
        conn.sendall(RequestSerializer.encode(Request(action="signup_response", content="Registration successful.")))

    @client_action
    def process_login(self, request, conn, cursor, db_conn):
        """
        Handle login requests.
        """
        cursor.execute("SELECT serialized_profile FROM profiles WHERE id = ?", (request.student_id,))
        result = cursor.fetchone()
        if result:
            profile = Profile.decode(result[0].encode('utf-8'))
            conn.sendall(RequestSerializer.encode(Request(action="login_response", content="Login successful.", profile=profile.to_dict())))
        else:
            conn.sendall(RequestSerializer.encode(Request(action="login_response", content="Login failed: User not found.")))

    @client_action
    def process_logout(self, request, conn, cursor, db_conn):
        """
        Handle logout requests.
        """
        conn.sendall(RequestSerializer.encode(Request(action="logout_response", content="Logout successful.")))

    @client_action
    def process_request_submission(self, request, conn, cursor, db_conn):
        """
        Handle the submission of an exit request.
        """
        cursor.execute("""
            INSERT INTO exit_requests (student_id, content, approved, approver_id)
            VALUES (?, ?, ?, ?)
        """, (request.student_id, request.content, False, request.approver_id))
        db_conn.commit()
        conn.sendall(RequestSerializer.encode(Request(action="submit_request_response", content="Request submission sent.")))

    @client_action
    def process_request_approval(self, request, conn, cursor, db_conn):
        """
        Handle the approval of an exit request.
        """
        cursor.execute("""
            UPDATE exit_requests SET approved = 1 WHERE id = ?
        """, (request.request_id,))
        db_conn.commit()
        conn.sendall(RequestSerializer.encode(Request(action="approve_request_response", content="Approval request sent.")))

    @client_action
    def process_view_requests(self, request, conn, cursor, db_conn):
        """
        Handle viewing of exit requests by staff.
        """
        cursor.execute("""
            SELECT * FROM exit_requests WHERE approver_id = ?
        """, (request.student_id,))
        requests = cursor.fetchall()
        response = [{"id": r[0], "student_id": r[1], "content": r[2], "approved": bool(r[3])} for r in requests]
        conn.sendall(RequestSerializer.encode(Request(action="view_requests_response", content=response)))

def reset_database():
    """
    Clear the database by deleting all rows in tables.
    """
    db_connection = sqlite3.connect('system.db')
    cursor = db_connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS profiles")
    cursor.execute("DROP TABLE IF EXISTS exit_requests")
    db_connection.commit()
    db_connection.close()
    print("Database reset completed.")
