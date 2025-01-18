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
        if session_key and isinstance(session_key, bytes):
            self.session_key = base64.b64encode(session_key).decode('utf-8')
        else:
            self.session_key = session_key

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
    def decode_raw(data):
        """
        Deserialize a raw JSON string and convert it into a Request object.
        """
        try:
            # Remove the length prefix (first 4 bytes)
            json_data = data[4:]
            request_data = json.loads(json_data.decode('utf-8'))
            if 'session_key' in request_data and request_data['session_key']:
                session_key = request_data['session_key']
                # Ensure proper padding for base64 decoding
                missing_padding = len(session_key) % 4
                if missing_padding:
                    session_key += '=' * (4 - missing_padding)
                request_data['session_key'] = base64.b64decode(session_key)
            return Request(**request_data)
        except UnicodeDecodeError as e:
            logging.error(f"UnicodeDecodeError: {e}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e}")
            raise

    @staticmethod
    def decode(sock):
        """
        Decode a message from the socket and return a Request object.
        """
        packed_length = sock.recv(4)
        if not packed_length:
            return None
        length = struct.unpack('!I', packed_length)[0]
        data = b""
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        request_data = json.loads(data.decode('utf-8'))
        return Request(**request_data)
