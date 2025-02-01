from socket import socket, AF_INET, SOCK_STREAM
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
import base64

# examples for using keys
rsakey = RSA.generate(2048)
rsakey_data = rsakey.export_key()
rsakey_pub_data = rsakey.public_key().export_key()
with open("enc_rsa_privatekey", "wb") as key_file:
    key_file.write(rsakey_data)

with open("enc_rsa_pubkey.pem", "wb") as key_file:
    key_file.write(rsakey_pub_data)

rsakey = RSA.generate(2048)
rsakey_data = rsakey.export_key()
rsakey_pub_data = rsakey.public_key().export_key()
with open("Templates_Ex/sign_rsa_privatekey", "wb") as key_file:
    key_file.write(rsakey_data)

with open("Templates_Ex/sign_rsa_pubkey.pem", "wb") as key_file:
    key_file.write(rsakey_pub_data)


class Connection:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.conn = socket(AF_INET, SOCK_STREAM)

    def sendall(self, data: bytes):
        """send the bytes over socket"""
        self.conn.sendall(data)

    def recvall(self, size: int) -> bytes:
        ans = b""
        while len(ans) < size:
            chunk = self.conn.recv(size - len(ans))
            if not chunk:
                raise IOError("Connection closed before receiving expected data.")
            ans += chunk

        return ans

    def send_msg(self, msg: bytes):
        """send with the length at the start"""
        self.sendall(int.to_bytes(len(msg), 4, "big"))
        self.sendall(msg)

    def recv_msg(self) -> bytes:
        """recv with the length at the start"""
        length = int.from_bytes(self.recvall(4), "big")
        return self.recvall(length)

    def connect(self):
        self.conn.connect((self.host, self.port))

    def start(self) -> bool:
        pass

    def close(self):
        self.conn.close()


class ServerEncConnection(Connection):

    def __init__(self, host, port):
        """
        initiate the network connection and import the RSA private key

        Args:
            host (str): the host to connect to
            port (int): the port to connect to
        """
        super().__init__(host, port)
        self.session_key = None
        self.rsa_key = RSA.import_key(open("private.pem").read())

    def send_msg(self, data: bytes):
        """
        Generate a random IV, encrypt the data with AES and send the IV and the ciphertext

        Args:
            data (bytes): the data to send
        """
        cipher = AES.new(self.session_key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        payload = base64.b64encode(cipher.iv + encrypted_data)
        self.conn.sendall(payload)

    def recv_msg(self) -> bytes:
        """
        recv the IV and the ciphertext, decrypt the ciphertext and return the plaintext

        Returns:
            bytes: the plaintext
        """
        encrypted_data = base64.b64decode(self.recvall(4096))
        iv = encrypted_data[:AES.block_size]
        encrypted_message = encrypted_data[AES.block_size:]
        cipher = AES.new(self.session_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(encrypted_message), AES.block_size)

    def start(self):
        """
        perform the handshake at the start of the connection
        receive and decrypt the RSA-encrypted AES key from the client
        """
        public_key = RSA.import_key(self.conn.recv(4096))
        cipher_rsa = PKCS1_OAEP.new(public_key)
        self.session_key = get_random_bytes(16)
        encrypted_session_key = cipher_rsa.encrypt(self.session_key)
        self.conn.send(encrypted_session_key)


class ClientEncConnection(Connection):

    def __init__(self, host, port):
        """
        initiate the network connection and import the RSA public key of the server

        Args:
            host (str): the host to connect to
            port (int): the port to connect to
        """
        ...

    def send_msg(self, data: bytes):
        """
        Generate a random IV, encrypt the data with AES and send the IV and the ciphertext

        Args:
            data (bytes): the data to send
        """
        ...

    def recv_msg(self) -> bytes:
        """
        recv the IV and the ciphertext, decrypt the ciphertext and return the plaintext

        Returns:
            bytes: the plaintext
        """
        ...

    def start(self):
        """
        perform the handshake at the start of the connection
        generate an AES key, encrypt it with the RSA public key of the server and send it to the server
        """
        ...
