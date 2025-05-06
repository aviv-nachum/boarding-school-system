"""
Server module for the boarding school system.
Handles the initialization and running of the server.
"""

from Encryption_handeling.listener import Listener
from threading import Thread
from db_manager import reset_database
from config import HOST, PORT

class Server(Thread):
    """
    Represents the server for the boarding school system.
    Manages incoming connections and starts the listener.
    """
    def __init__(self):
        super().__init__()
        # Uncomment the line below to reset the database on server initialization
        # reset_database()
        self.listener = Listener(host=HOST, port=PORT)
        
    def run(self):
        """
        Starts the listener to handle incoming client connections.
        """
        self.listener.start()

if __name__ == "__main__":
    # Start the server
    Server().start()