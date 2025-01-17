from socket import *
from threading import Thread, Lock
from Actions.Request import Request, RequestSerializer
from config import *
from Actions.Actions import action_handlers
from Profiles.Profile import Profile
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import sqlite3
import time
import os

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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY,
                serialized_profile TEXT
            )
        """)

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

    def encrypt_response(self, data, session_key):
        """
        Encrypt the response data using AES and the session key.
        """
        cipher = AES.new(session_key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        payload = cipher.iv + encrypted_data
        return base64.b64encode(payload).decode('utf-8')  # Encode entire payload as base64


    def decrypt_request(self, encrypted_data, session_key):
        """
        Decrypt the request data using AES and the session key.
        """
        encrypted_data = base64.b64decode(encrypted_data)  # Decode from base64
        iv = encrypted_data[:AES.block_size]  # Extract IV
        encrypted_message = encrypted_data[AES.block_size:]  # Extract ciphertext
        cipher = AES.new(session_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_message), AES.block_size).decode('utf-8')


    def client_handler(self, conn):
        thread_db_conn = sqlite3.connect('Database/system.db')
        thread_cursor = thread_db_conn.cursor()

        conn.send(PUBLIC_KEY.export_key())
        encrypted_session_key = conn.recv(256)
        cipher_rsa = PKCS1_OAEP.new(PRIVATE_KEY)
        session_key = cipher_rsa.decrypt(encrypted_session_key)

        while True:
            try:
                encrypted_request = conn.recv(4096)
                if not encrypted_request:
                    self.log("Client disconnected.")
                    break

                decrypted_request = self.decrypt_request(encrypted_request.decode('utf-8'), session_key)
                request = RequestSerializer.decode_raw(decrypted_request)  # Adjusted decode method

                self.log(f"Received action '{request.action}' from client.")

                if request.action not in ["signup", "login"]:
                    session_id = request.content.get("session_id")
                    if not session_id or session_id not in self.sessions:
                        self.log("Unauthorized access attempt.")
                        conn.send(self.encrypt_response("Unauthorized access", session_key).encode('utf-8'))
                        continue

                handler_class = action_handlers.get(request.action)
                if handler_class:
                    handler_instance = handler_class(self, conn, thread_cursor, thread_db_conn)
                    handler_instance.handle_action(request)
                else:
                    self.log(f"Unknown action: {request.action}")
                    conn.send(self.encrypt_response("Unknown action", session_key).encode('utf-8'))

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
