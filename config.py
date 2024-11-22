"""
important info and functions all classes need access to
"""

import struct
import json

HOST = 'localhost'
PORT = 8000

def send_message_with_length(sock, message):
    """
    Serialize the message to JSON, prepend its length (4 bytes), and send it.
    This ensures the receiver knows how much data to read.
    """
    message_bytes = json.dumps(message).encode('utf-8')  # Convert message to JSON bytes
    packed_length = struct.pack('!I', len(message_bytes))  # Pack the length in network byte order
    sock.sendall(packed_length + message_bytes)  # Send the length followed by the message

def receive_message_with_length(sock):
    """
    Receive a message with a prepended 4-byte length header.
    The length specifies how many bytes to read for the actual message.
    """
    packed_length = sock.recv(4)  # Read the 4-byte length header
    if not packed_length:  # Connection closed
        return None
    length = struct.unpack('!I', packed_length)[0]  # Unpack the length from network byte order
    data = sock.recv(length).decode('utf-8')  # Read the message based on the length
    return json.loads(data)  # Deserialize the JSON string back to a Python object