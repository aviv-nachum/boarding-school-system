from socket import *
from threading import Thread, Lock
from config import *
import sqlite3  # Database for storing messages
from message import Message

clients = {}  # Dictionary to store client ID -> socket mapping
lock = Lock()  # Lock to ensure thread-safe access to the `clients` dictionary

# Initialize SQLite database
db_connection = sqlite3.connect('messages.db', check_same_thread=False)
cursor = db_connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    content TEXT
)
""")
db_connection.commit()


class Server(Thread):
    def __init__(self):
        super().__init__()
        self.addr = (HOST, PORT)  # Server address tuple (host, port)

    def run(self):
        """
        Start the server, accept new connections, and spawn threads to handle clients.
        """
        self.s = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket
        self.s.bind(self.addr)  # Bind the socket to the specified address
        self.s.listen(5)  # Start listening for incoming connections (max queue size = 5)
        print("Server is running...")

        while True:
            conn, addr = self.s.accept()  # Accept a new client connection
            with lock:  # Ensure thread-safe modification of `clients`
                client_id = len(clients) + 1  # Assign a new client ID
                clients[client_id] = conn  # Map the client ID to the connection socket
            print(f"Client {client_id} connected from {addr}.")
            # Start a new thread to handle the client
            Thread(target=self.client_handler, args=(conn, client_id)).start()

    def client_handler(self, conn, client_id):
        """
        Handle communication with a specific client. Store all messages in a database.
        """
        # Create a thread-local database connection and cursor
        thread_db_conn = sqlite3.connect('messages.db')  # New connection for this thread
        thread_cursor = thread_db_conn.cursor()

        while True:
            try:
                # Receive the message object
                message = Message.decode(conn)
                if not message:  # If no message, the client likely disconnected
                    break

                # Log the message in the database using the thread-local cursor
                thread_cursor.execute(
                    "INSERT INTO messages (sender_id, content) VALUES (?, ?)",
                    (client_id, message.content)
                )
                thread_db_conn.commit()

                print(f"Stored message from Client {client_id}: {message.content}")
            except Exception as e:
                print(f"Error: {e}")  # Log any errors during communication
                break

        # Cleanup: Remove the client and close the connection
        with lock:
            del clients[client_id]  # Remove client from the `clients` dictionary
        conn.close()  # Close the socket
        thread_db_conn.close()  # Close the thread-local database connection
        print(f"Client {client_id} disconnected.")
