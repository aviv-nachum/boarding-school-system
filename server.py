from socket import *
from threading import Thread, Lock
from config import *
from Request import Request, RequestSerializer
import sqlite3
import time

lock = Lock()

# TODO: add class db_mannager that knows to save automaticly all of the info like profiles
# TODO: in the init crate the db add function that saves info to db, put it server.run
# TODO: make a list of all of the functions that need to go through the api

# Retry mechanism for database operations
def execute_with_retry(cursor, query, params=(), retries=3, delay=0.1):
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

class Server(Thread):
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

        # Create profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                grade TEXT,
                class_number INTEGER,
                head_teacher_id INTEGER,
                head_madric_id INTEGER,
                role TEXT
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
        """
        thread_db_conn = sqlite3.connect('system.db')
        thread_cursor = thread_db_conn.cursor()

        while True:
            try:
                request = RequestSerializer.decode(conn)
                if not request:
                    self.log("Client disconnected.")
                    break

                self.log(f"Received action '{request.action}' from client.")

                # Route the request to appropriate methods
                action = request.action
                if action == "signup":
                    self.process_register(request, conn, thread_cursor, thread_db_conn)
                elif action == "login":
                    self.process_login(request, conn, thread_cursor)
                elif action == "logout":
                    self.process_logout(request, conn)
                elif action == "submit_request":
                    self.process_request_submission(request, conn, thread_cursor, thread_db_conn)
                elif action == "approve_request":
                    self.process_request_approval(request, conn, thread_cursor, thread_db_conn)
                elif action == "view_requests":
                    self.process_view_requests(request, conn, thread_cursor)
                else:
                    self.log(f"Unknown action: {action}")
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

    def process_register(self, request, conn, cursor, db_conn):
        """
        Handle student or staff registration.
        """
        profile = request.profile
        try:
            self.log(f"Processing registration for profile ID: {profile['id']}")

            # Check if the ID already exists
            cursor.execute("SELECT id FROM profiles WHERE id = ?", (profile['id'],))
            if cursor.fetchone():
                self.log(f"Registration failed: ID {profile['id']} already exists.")
                conn.sendall(RequestSerializer.encode(Request(action="signup_response", content="Registration failed: ID already exists.")))
                return

            # Insert the profile into the database
            cursor.execute("""
                INSERT INTO profiles (id, name, surname, grade, class_number, head_teacher_id, head_madric_id, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (profile['id'], profile['name'], profile['surname'], profile.get('grade', None),
                profile.get('class_number', None), profile.get('head_teacher_id', None),
                profile.get('head_madric_id', None), profile['role']))
            db_conn.commit()

            self.log(f"Registration successful for profile ID: {profile['id']}")
            conn.sendall(RequestSerializer.encode(Request(action="signup_response", content="Registration successful.")))
        except sqlite3.IntegrityError as e:
            self.log(f"Error during registration for profile ID {profile['id']}: {e}")
            conn.sendall(RequestSerializer.encode(Request(action="signup_response", content="Registration failed: Database error.")))
        except Exception as e:
            self.log(f"Unexpected error during registration: {e}")
            conn.sendall(RequestSerializer.encode(Request(action="signup_response", content="Registration failed: Unexpected error.")))

    def process_login(self, request, conn, cursor):
        """
        Handle login requests.
        """
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (request.student_id,))
        profile = cursor.fetchone()
        if profile:
            conn.sendall(RequestSerializer.encode(Request(action="login_response", content="Login successful.")))
        else:
            conn.sendall(RequestSerializer.encode(Request(action="login_response", content="Login failed: User not found.")))


    def process_logout(self, request, conn):
        """
        Handle logout requests.
        """
        conn.sendall("Logout successful.".encode('utf-8'))

    def process_request_submission(self, request, conn, cursor, db_conn):
        """
        Handle the submission of an exit request.
        """
        cursor.execute("""
            INSERT INTO exit_requests (student_id, content, approved, approver_id)
            VALUES (?, ?, ?, ?)
        """, (request.student_id, request.content, False, request.approver_id))
        db_conn.commit()
        conn.sendall("Request submission sent.".encode('utf-8'))

    def process_request_approval(self, request, conn, cursor, db_conn):
        """
        Handle the approval of an exit request.
        """
        cursor.execute("""
            UPDATE exit_requests SET approved = 1 WHERE id = ?
        """, (request.request_id,))
        db_conn.commit()
        conn.sendall("Approval request sent.".encode('utf-8'))

    def process_view_requests(self, request, conn, cursor):
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
    cursor.execute("DELETE FROM profiles")
    cursor.execute("DELETE FROM exit_requests")
    db_connection.commit()
    db_connection.close()
    print("Database reset completed.")

