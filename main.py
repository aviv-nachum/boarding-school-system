import time
from server import Server
from client import Client

# Initialize and start the server
server = Server()
server.start()

time.sleep(1)  # Allow server time to start

# Initialize two clients
client1 = Client()
client2 = Client()

# Start the client threads
client1.start()
client2.start()

time.sleep(1)  # Allow clients to connect to the server

# Client 1 sends a message
client1.send_message("Hello from Client 1!")

# Client 2 sends a message
client2.send_message("Hello from Client 2!")
