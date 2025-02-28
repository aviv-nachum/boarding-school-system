import struct
import json
import logging
import base64

# filepath: c:\Users\Kids\Documents\GitHub\boarding-school-system\Actions\Request.py

class Request:
    """
    Represents a request sent between the client and server.
    """
    def __init__(self, action, student_id=None, content=None, approver_id=None, request_id=None, profile=None, session_key=None):
        self.action = action
        self.student_id = student_id
        self.content = content
        self.approver_id = approver_id
        self.request_id = request_id
        self.profile = profile
        self.session_key = session_key

    def to_json(self):
        return json.dumps({
            "action": self.action,
            "student_id": self.student_id,
            "content": self.content,
            "approver_id": self.approver_id,
            "request_id": self.request_id,
            "profile": self.profile,
            "session_key": self.session_key,
        })

class RequestSerializer:
    """
    Handles serialization and deserialization of Request objects.
    """

    @staticmethod
    def encode(request):
        """
        Serialize a request object to JSON and prepend its length.
        """
        return json.dumps(request.__dict__).encode('utf-8')

    @staticmethod
    def decode_raw(data):
        """
        Deserialize a raw JSON string and convert it into a Request object.
        """
        return Request(**json.loads(data.decode('utf-8')))

    @staticmethod
    def decode(data):
        """
        Decode a message from the socket and return a Request object.
        """
        return Request(**json.loads(data.decode('utf-8')))
