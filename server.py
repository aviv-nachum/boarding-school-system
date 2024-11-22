from socket import *
from threading import Thread, Lock
from config import *
from Request import Request, RequestSerializer
import sqlite3
import time

clients = {}  # Connected clients (ID -> socket)
lock = Lock()

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
        super().__init__()
        self.addr = (HOST, PORT)

    def run(self):
        """
        Start the server, accept new connections, and spawn threads to handle clients.
        """
        # Initialize database and set WAL mode
        db_connection = sqlite3.connect('system.db', check_same_thread=False)
        db_connection.execute("PRAGMA journal_mode=WAL;")
        db_connection.commit()
        self.db_connection = db_connection

        # Start listening for connections
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind(self.addr)
        self.s.listen(5)
        print("Server is running...")

        while True:
            conn, addr = self.s.accept()
            with lock:
                client_id = len(clients) + 1
                clients[client_id] = conn
            print(f"Client {client_id} connected from {addr}.")
            Thread(target=self.client_handler, args=(conn, client_id)).start()

    def client_handler(self, conn, client_id):
        """
        Handle communication with a specific client.
        Each thread uses its own SQLite connection and cursor.
        """
        thread_db_conn = sqlite3.connect('system.db')
        thread_cursor = thread_db_conn.cursor()

        while True:
            try:
                request = RequestSerializer.decode(conn)
                if not request:
                    print(f"Client {client_id} disconnected.")
                    break

                print(f"Received action '{request.action}' from Client {client_id}")

                # Route the request based on its action
                if request.action == "signup":
                    self.process_register(request, conn, thread_cursor, thread_db_conn)
                elif request.action == "login":
                    self.process_login(request, conn, thread_cursor)
                elif request.action == "logout":
                    self.process_logout(request, conn)
                elif request.action == "submit_request":
                    self.process_request_submission(request, conn, thread_cursor, thread_db_conn)
                elif request.action == "approve_request":
                    self.process_request_approval(request, conn, thread_cursor, thread_db_conn)
                elif request.action == "view_requests":
                    self.process_view_requests(request, conn, thread_cursor)

            except Exception as e:
                print(f"Error handling client {client_id}: {e}")
                break

        with lock:
            del clients[client_id]
        conn.close()
        thread_db_conn.close()
        print(f"Client {client_id} disconnected.")

    def process_register(self, request, conn, cursor, db_conn):
        profile = request.profile
        try:
            # Check if the ID already exists
            cursor.execute("SELECT id FROM profiles WHERE id = ?", (profile['id'],))
            if cursor.fetchone():
                conn.sendall("Registration failed: ID already exists.".encode('utf-8'))
                return

            execute_with_retry(cursor, """
                INSERT INTO profiles (id, name, surname, grade, class_number, head_teacher_id, head_madric_id, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (profile['id'], profile['name'], profile['surname'], profile.get('grade', None),
                  profile.get('class_number', None), profile.get('head_teacher_id', None),
                  profile.get('head_madric_id', None), profile['role']))
            db_conn.commit()
            conn.sendall("Registration successful.".encode('utf-8'))
        except sqlite3.IntegrityError as e:
            print(f"Error during registration: {e}")
            conn.sendall("Registration failed: Database error.".encode('utf-8'))

    def process_login(self, request, conn, cursor):
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (request.student_id,))
        profile = cursor.fetchone()
        if profile:
            conn.sendall("Login successful.".encode('utf-8'))
        else:
            conn.sendall("Login failed: User not found.".encode('utf-8'))

    def process_logout(self, request, conn):
        conn.sendall("Logout successful.".encode('utf-8'))

    def process_request_submission(self, request, conn, cursor, db_conn):
        execute_with_retry(cursor, """
            INSERT INTO exit_requests (student_id, content, approved, approver_id)
            VALUES (?, ?, ?, ?)
        """, (request.student_id, request.content, False, request.approver_id))
        db_conn.commit()
        conn.sendall("Request submission sent.".encode('utf-8'))

    def process_request_approval(self, request, conn, cursor, db_conn):
        execute_with_retry(cursor, """
            UPDATE exit_requests SET approved = 1 WHERE id = ?
        """, (request.request_id,))
        db_conn.commit()
        conn.sendall("Approval request sent.".encode('utf-8'))

    def process_view_requests(self, request, conn, cursor):
        cursor.execute("""
            SELECT * FROM exit_requests WHERE approver_id = ?
        """, (request.student_id,))
        requests = cursor.fetchall()
        response = [{"id": r[0], "student_id": r[1], "content": r[2], "approved": bool(r[3])} for r in requests]
        conn.sendall(RequestSerializer.encode(Request(action="view_requests_response", content=response)))
