"""
Main entry point for the boarding school system.
Starts the server and initializes the GUI for user interaction.
"""

from time import sleep
from server import Server
from gui import GUI

if __name__ == "__main__":
    # Initialize and start the server
    server = Server()
    server.start()
    sleep(1)

    # Start the GUI
    gui = GUI()
    gui.main_menu()
