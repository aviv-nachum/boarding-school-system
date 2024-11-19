from socket import *
from threading import Thread
import threading
import time
from random import randint

clients = []
HOST = 'localhost'
PORT = 8000

def read_from_socket(conn):
    buf = bytearray(0)
    while True:
        b = conn.recv(1)
        buf.extend(b)
        if b == b'\n':
                return bytes(buf)

class Server(threading.Thread):
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


class Client(threading.Thread):
    """client class built to send a message to another """
    def sendMessage(self):
        if len(clients)>1:
                to = randint(0, len(clients) - 1)
                message = ('%s:hello from %s\n' % (to, self.name)).encode('utf-8')
                print(message)
                self.ss.send(message)
    
    def sendMessage(self, message):
        if len(clients)>1:
                to = randint(0, len(clients) - 1)
                message = (message + '\nto:%s \nfrom:%s\n' % (to, self.name))
                print(message)
                self.ss.send(message.encode('utf-8'))

    def receiveMessage(self):
        while 1:
            reply=self.ss.recv(1024)
            if reply != '':
                print("%r received %r" % (self.name, reply))
                break

    def run(self):
        self.ss = socket(AF_INET, SOCK_STREAM)
        self.ss.connect((HOST, PORT)) # client-side, connects to a host
        self.name=self.ss.getsockname()[1]

        while True:
            self.receiveMessage()

server=Server()
client1=Client()
client2=Client()
client3=Client()

client1.start()
client2.start()
client3.start()

time.sleep(1)
client1.sendMessage("hi")