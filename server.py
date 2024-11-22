from socket import *
from threading import Thread, Lock
from config import *

clients = {}  # Dictionary to store client ID -> socket mapping
lock = Lock()  # Lock to ensure thread-safe access to the `clients` dictionary

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
        Handle communication with a specific client. Relay messages to other clients.
        """
        while True:
            try:
                message = receive_message_with_length(conn)  # Receive a message from the client
                if not message:  # If no message, the client likely disconnected
                    break
                to_id = message['to']  # Target client ID
                msg_content = message['message']  # Message content
                print(f"Client {client_id} -> Client {to_id}: {msg_content}")

                with lock:  # Ensure thread-safe access to `clients`
                    if to_id in clients:  # If the target client is connected
                        # Forward the message to the target client
                        send_message_with_length(clients[to_id], {"from": client_id, "message": msg_content})
            except Exception as e:
                print(f"Error: {e}")  # Log any errors during communication
                break

        # Cleanup: Remove the client and close the connection
        with lock:
            del clients[client_id]  # Remove client from the `clients` dictionary
        conn.close()  # Close the socket
        print(f"Client {client_id} disconnected.")
