from socket import *
from threading import Thread, Lock
from config import *
from Request import Request, RequestSerializer
import sqlite3
import time
import functools

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

class DBManager:
    def __init__(self, db_name='system.db'):
        self.db_conn = sqlite3.connect(db_name, check_same_thread=False)
        self.db_conn.execute("PRAGMA journal_mode=WAL;")
        self.cursor = self.db_conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute("""
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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exit_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                content TEXT,
                approved BOOLEAN,
                approver_id INTEGER
            )
        """)
        self.db_conn.commit()

    def insert(self, query, params):
        execute_with_retry(self.cursor, query, params)
        self.db_conn.commit()

    def fetch_one(self, query, params):
        execute_with_retry(self.cursor, query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params):
        execute_with_retry(self.cursor, query, params)
        return self.cursor.fetchall()

def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

class Server(Thread):
    def __init__(self):
        super().__init__()
        self.addr = (HOST, PORT)
        self.db_manager = DBManager()

    def run(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind(self.addr)
        self.s.listen(5)
        print("Server is running...")

        while True:
            conn, addr = self.s.accept()
            print(f"Connection from {addr}")
            Thread(target=self.client_handler, args=(conn,)).start()

    @log_action
    def client_handler(self, conn):
        while True:
            try:
                request = RequestSerializer.decode(conn)
                if not request:
                    break
                action = request.action
                if action == "signup":
                    self.process_register(request, conn)
                elif action == "login":
                    self.process_login(request, conn)
                elif action == "submit_request":
                    self.process_request_submission(request, conn)
                elif action == "view_requests":
                    self.process_view_requests(request, conn)
                elif action == "approve_request":
                    self.process_request_approval(request, conn)
            except Exception as e:
                print(f"Error: {e}")
                break
        conn.close()

    def process_register(self, request, conn):
        profile = request.profile
        query = """INSERT INTO profiles (id, name, surname, grade, class_number, head_teacher_id, head_madric_id, role)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        self.db_manager.insert(query, (profile['id'], profile['name'], profile['surname'], profile['grade'],
                                       profile['class_number'], profile['head_teacher_id'], profile['head_madric_id'],
                                       profile['role']))
        conn.sendall("Registration successful.".encode('utf-8'))

    # Similarly update other handlers for login, submission, etc.
