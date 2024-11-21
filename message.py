import time
from server import Server
from client import Client

server = Server()
server.start()

time.sleep(1)

client1 = Client()
client2 = Client()

client1.start()
client2.start()

time.sleep(1)

client1.send_message(2, "Hello from Client 1!")
client2.send_message(1, "Hello back from Client 2!")
