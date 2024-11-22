import time
from server import Server
from client import Client

# Initialize and start the server
server = Server()
server.start()

time.sleep(1)  # Give the server time to start before connecting clients

# Initialize two clients
client1 = Client()
client2 = Client()

# Start the client threads (connect to the server and handle communication)
client1.start()
client2.start()

time.sleep(1)  # Allow clients to establish connection with the server

# Client 1 sends a message to Client 2
client1.send_message(2, "Hello from Client 1!")

# Client 2 sends a response to Client 1
client2.send_message(1, "Hello back from Client 2!")
