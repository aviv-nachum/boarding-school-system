from template_classes.listener import Listener
from threading import Thread
from db_manager import reset_database
from config import HOST, PORT

class Server(Thread):
    def __init__(self):
        super().__init__()
        #reset_database()
        self.listener = Listener(host=HOST, port=PORT)
        
    def run(self):
        self.listener.start()

if __name__ == "__main__":
    Server().start()