import struct
import json

class Request:
    """
    Represents a request sent between the client and server.
    """

    def __init__(self, action, student_id=None, content=None, approver_id=None, request_id=None, profile=None):
        self.action = action
        self.student_id = student_id
        self.content = content
        self.approver_id = approver_id
        self.request_id = request_id
        self.profile = profile

class RequestSerializer:
    """
    Handles serialization and deserialization of Request objects.
    """

    @staticmethod
    def encode(request):
        """
        Serialize a request object to JSON and prepend its length.
        """
        message_bytes = json.dumps(request.__dict__).encode('utf-8')
        packed_length = struct.pack('!I', len(message_bytes))
        return packed_length + message_bytes

    @staticmethod
    def decode(sock): # TODO: be the opposite of encode, fix in server.py
        """
        Decode a message from the socket and return a Request object.
        """
        packed_length = sock.recv(4)
        if not packed_length:
            return None
        length = struct.unpack('!I', packed_length)[0]
        data = sock.recv(length).decode('utf-8')
        request_data = json.loads(data)
        return Request(**request_data)

