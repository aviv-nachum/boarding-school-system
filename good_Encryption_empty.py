from socket import socket, AF_INET, SOCK_STREAM
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad

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
            ans += self.conn.recv(size - len(ans))

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
        receive and decrypt the RSA-encrypted AES key from the client
        """
        ...


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
