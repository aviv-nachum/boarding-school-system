import struct
import json


class Message:
    """
    Represents a message exchanged between the client and server.
    Includes encoding and decoding functionality.
    """

    def __init__(self, content):
        self.content = content  # The actual message content

    def encode(self):
        """
        Serialize the message to JSON, prepend its length (4 bytes), and return the byte sequence.
        """
        message_bytes = json.dumps({"content": self.content}).encode('utf-8')
        packed_length = struct.pack('!I', len(message_bytes))
        return packed_length + message_bytes

    @staticmethod
    def decode(sock):
        """
        Decode a message received from the socket.
        Read the length header and the serialized message content.
        """
        packed_length = sock.recv(4)
        if not packed_length:
            return None
        length = struct.unpack('!I', packed_length)[0]
        data = sock.recv(length).decode('utf-8')
        content = json.loads(data)["content"]
        return Message(content)
