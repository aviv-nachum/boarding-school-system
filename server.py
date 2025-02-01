from socket import *
from threading import Thread, Lock
from Actions.Request import Request, RequestSerializer
from Actions.Actions import action_handlers
from config import *
from Crypto.PublicKey import RSA
from db_manager import reset_database
from handler import Handler
import os
import sqlite3
import time
import logging
import json

logging.basicConfig(level=logging.DEBUG)

lock = Lock()

# Generate RSA keys for the server
if not os.path.exists("private.pem") or not os.path.exists("public.pem"):
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    with open("private.pem", "wb") as priv_file:
        priv_file.write(private_key)
    with open("public.pem", "wb") as pub_file:
        pub_file.write(public_key)

# Load RSA keys
with open("private.pem", "rb") as priv_file:
    PRIVATE_KEY = RSA.import_key(priv_file.read())
with open("public.pem", "rb") as pub_file:
    PUBLIC_KEY = RSA.import_key(pub_file.read())

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
        self.sessions = {}

    def init_db(self):
        self.db_connection = sqlite3.connect('Database/system.db', check_same_thread=False)
        self.db_connection.execute("PRAGMA journal_mode=WAL;")
        cursor = self.db_connection.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                profile TEXT NOT NULL
            )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS exit_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                content TEXT,
                approved BOOLEAN,
                approver_id TEXT,
                FOREIGN KEY (student_id) REFERENCES users (username),
                FOREIGN KEY (approver_id) REFERENCES users (username)
            )""")
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
                handler = Handler(conn)
                Thread(target=handler.handle_forever).start()
            except Exception as e:
                self.log(f"Server error: {e}")
                break