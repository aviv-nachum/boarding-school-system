"""
Main entry point for the boarding school system.
Starts the server and initializes the GUI for user interaction.
"""

from time import sleep
from server import Server
from gui_tkinter import GUIApp
import tkinter as tk

if __name__ == "__main__":
    # Initialize and start the server
    server = Server()
    server.start()  # Start the server in a separate thread
    sleep(1)  # Allow the server to initialize

    # Start the tkinter GUI for user interaction
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
