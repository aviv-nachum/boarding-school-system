"""
Manages incoming client connections and delegates them to handlers.
"""

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from config import HOST, PORT
from threading import Thread
from Encryption_handeling.handler import Handler


class Listener:
    """
    Listens for incoming client connections and manages them.
    """

    def __init__(self, host=HOST, port=PORT, backlog=1000):
        """
        Initializes the Listener with server details.

        Args:
            host (str): The host address to bind the server.
            port (int): The port number to bind the server.
            backlog (int): The maximum number of queued connections.
        """
        self.host = host
        self.port = port
        self.backlog = backlog
        self.server_socket: socket | None = None  # The server's main socket
        self.active_connection: list[Thread] = []  # List of active client threads

    def start(self):
        """
        Starts the listener to accept incoming client connections.
        """
        self.server_socket = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Allow address reuse
        self.server_socket.bind((self.host, self.port))  # Bind the socket to the host and port
        self.server_socket.listen(self.backlog)  # Start listening for connections
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            conn, addr = self.server_socket.accept()
            #print(f"Accepted connection from {addr}")
            handler = Handler(conn, self.host, self.port)
            thread = Thread(target=handler.handle_forever)
            self.active_connection.append(thread)
            thread.start()

    def stop(self):
        """
        Stop the listener and close the server socket.
        """
        self.server_socket.close()


if __name__ == "__main__":
    listener = Listener()
    listener.start()