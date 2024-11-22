from socket import *
import struct
import json
from threading import Thread
from config import *

class Client(Thread):
    def __init__(self):
        """
        Initialize the client socket and prepare for connection.
        """
        super().__init__()
        self.ss = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket

    def run(self):
        """
        Connect to the server and start a separate thread to listen for incoming messages.
        """
        self.ss.connect((HOST, PORT))  # Connect to the server
        self.id = self.ss.getsockname()[1]  # Use the socket's port number as the client ID
        print(f"Connected as Client {self.id}")
        # Start a background thread to handle incoming messages
        Thread(target=self.receive_messages).start()

    def receive_messages(self):
        """
        Continuously listen for messages from the server.
        """
        while True:
            try:
                message = receive_message_with_length(self.ss)  # Receive and decode a message
                print(f"Received: {message}")  # Print the received message
            except:  # Exit the loop if an error occurs (e.g., disconnection)
                break

    def send_message(self, to_id, message):
        """
        Send a message to another client via the server.
        Includes the target client's ID and the message content.
        """
        send_message_with_length(self.ss, {"to": to_id, "message": message})  # Prepare and send the message
