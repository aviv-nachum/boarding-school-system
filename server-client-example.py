from socket import *
from threading import Thread
import threading
import time
from random import randint
import struct # TODO: read about this

# TODO: the client needs to send the message to the server and not other clients
# TODO: replace list with dictionery where the key is the id and the value is the socket (maybe socket dosent need to save socket)
# TODO: crate .py to server, client and for message
# TODO: learn sirialization

clients = []
HOST = 'localhost'
PORT = 8000

def read_from_socket(conn): # TODO: not one at a time, insted send the message length too
    """gets a port and tries to recive from it untill the message end with a '\n'"""
    buf = bytearray(0)
    while True:
        b = conn.recv(1)
        buf.extend(b)
        if b == b'\n':
                return bytes(buf)

class Server(threading.Thread): # TODO: check out "threading.Lock"
    """server class, built to recive messages from client and transfer them to a diffrent client"""
    def __init__(self):
        super(Server, self).__init__()
        self.addr = (HOST,PORT)
        self.start()

    def run(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen(5)
        print("Server is running......")

        while True:
            conn, addr = self.s.accept()
            threading.Thread(target=self.clientHandler, args=(conn, addr)).start()

    def clientHandler(self, conn, addr):
        clients.append(conn)
        while True:
             msg = read_from_socket(conn)
             id_str, _, msg = msg.partition(b':')
             clients[int(id_str)].sendall(msg)
 
class Client(threading.Thread): # dosent need to inherit from thread
    """client class built to send a message to another client"""
    def sendMessage(self, message, to):
        if len(clients)>1:
                to = randint(0, len(clients) - 1) # TODO: not random, sends to server only
                message = ('%s:sent to %s\n' % (to, self.name)) + message
                print(message)
                self.ss.send(message.encode('utf-8'))

    def receiveMessage(self): # TODO: fix this to work with struct.pack
        while 1:
            reply=self.ss.recv(1024)
            if reply != '':
                print("%r received %r" % (self.name, reply))
                break

    def run(self):
        self.ss = socket(AF_INET, SOCK_STREAM)
        self.ss.connect((HOST, PORT)) # client-side, connects to a host
        self.name=self.ss.getsockname()[1] # call this id, ids need to be diffrent 

        while True:
            self.receiveMessage()

### initing servers and clients ###
server=Server()
client1=Client()
client2=Client()
client3=Client()

client1.start()
client2.start()
client3.start()

### testing comunication ###
time.sleep(1)
client1.sendMessage("hi")