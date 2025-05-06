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
    server.start()  # Start the server in a separate thread
    sleep(1)  # Allow the server to initialize

    # Start the GUI for user interaction
    gui = GUI()
    gui.main_menu()  # Display the main menu
