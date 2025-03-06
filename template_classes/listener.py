from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from config import HOST, PORT
import threading
from threading import Thread
from template_classes.handler import Handler


class Listener:
    def __init__(self, host=HOST, port=PORT, backlog=1000):
        """
        Initialize the listener with a host and port.
        """
        self.host = host
        self.port = port
        self.backlog = backlog
        self.server_socket: socket | None = None
        self.active_connection: list[Thread] = []

    def start(self):
        """
        Start the listener to accept incoming client connections.
        """
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.backlog)
        print(f"Listening on {self.host}:{self.port}")

        while True:
            conn, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
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