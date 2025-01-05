from socket import *
from threading import Thread, Lock
from Actions.Request import Request, RequestSerializer
from config import *
from Actions.Actions import action_handlers
from Profiles.Profile import Profile
import sqlite3
import time

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
    """
    Server class to manage client connections and handle requests.
    """
    def __init__(self):
        reset_database()  # For testing, will be removed later
        super().__init__()
        self.addr = (HOST, PORT)
        self.init_db()

    def init_db(self):
        self.db_connection = sqlite3.connect('Database/system.db', check_same_thread=False)
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
        with lock:
            print(message)

    def run(self):
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
        thread_db_conn = sqlite3.connect('Database/system.db')
        thread_cursor = thread_db_conn.cursor()

        while True:
            try:
                # Decode the client request
                request = RequestSerializer.decode(conn)
                if not request:
                    self.log("Client disconnected.")
                    break

                self.log(f"Received action '{request.action}' from client.")

                # Find the appropriate handler for the action
                handler_class = action_handlers.get(request.action)
                if handler_class:
                    handler_instance = handler_class(self, conn, thread_cursor, thread_db_conn)
                    handler_instance.handle_action(request)
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

def reset_database():
    db_connection = sqlite3.connect('Database/system.db')
    cursor = db_connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS profiles")
    cursor.execute("DROP TABLE IF EXISTS exit_requests")
    db_connection.commit()
    db_connection.close()
    print("Database reset completed.")
