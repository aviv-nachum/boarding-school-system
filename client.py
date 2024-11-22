from socket import *
from threading import Thread
from config import *
from message import Message


class Client(Thread):
    def __init__(self):
        """
        Initialize the client socket and prepare for connection.
        """
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket

    def run(self):
        """
        Connect to the server and start a separate thread to listen for server responses.
        """
        self.ss.connect((HOST, PORT))  # Connect to the server
        self.id = self.ss.getsockname()[1]  # Use the socket's port number as the client ID
        print(f"Connected as Client {self.id}")
        # Start a background thread to handle server messages (if needed)
        Thread(target=self.receive_messages).start()

    def receive_messages(self):
        """
        Placeholder for receiving messages from the server if necessary.
        """
        while True:
            try:
                message = Message.decode(self.ss)  # Decode a message from the server
                print(f"Server response: {message.content}")  # Print the received message
            except:
                break

    def send_message(self, content):
        """
        Send a message to the server.
        """
        message = Message(content)  # Create a message object
        self.ss.sendall(message.encode())  # Encode and send the message
