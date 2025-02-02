from socket import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad


class Connection:

    def __init__(self, host: str, port: int, conn: socket):
        self.host = host
        self.port = port
        self.conn = conn

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

    def __init__(self, host, port, conn):
        """
        initiate the network connection and import the RSA private key

        Args:
            host (str): the host to connect to
            port (int): the port to connect to
        """
        Connection.__init__(self, host, port, conn)
        with open("enc_rsa_privatekey", "rb") as key_file:
            self.rsa_key = RSA.import_key(key_file.read())
        self.aes_key=b""
        ...

    def send_msg(self, data: bytes):
        """
        Generate a random IV, encrypt the data with AES and send the IV and the ciphertext

        Args:
            data (bytes): the data to send
        """
        iv = get_random_bytes(16)
        aes_cipher = AES.new(self.aes_key,AES.MODE_CBC,iv=iv)
        enc_msg = aes_cipher.encrypt(pad(data,16))
        self.sendall(int.to_bytes(len(iv+enc_msg), 4, "big"))
        self.sendall(iv+enc_msg)        

    def recv_msg(self) -> bytes:
        """
        recv the IV and the ciphertext, decrypt the ciphertext and return the plaintext

        Returns:
            bytes: the plaintext
        """
        length = int.from_bytes(self.recvall(4), "big")
        data = self.recvall(length)
        iv = data[:16]
        ciphertext = data[16:]
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)
        msg = aes_cipher.decrypt(ciphertext)
        return unpad(msg,16)

    def start(self):
        """
        perform the handshake at the start of the connection
        receive and decrypt the RSA-encrypted AES key from the client
        """
        length = int.from_bytes(self.recvall(4), "big")
        enc_key = self.recvall(length)
        rsa_cipher = PKCS1_OAEP.new(self.rsa_key)
        self.aes_key = rsa_cipher.decrypt(enc_key)        

class ClientEncConnection(Connection):

    def __init__(self, host, port, conn):
        """
        initiate the network connection and import the RSA public key of the server

        Args:
            host (str): the host to connect to
            port (int): the port to connect to
        """
        Connection.__init__(self,host,port, conn)
        with open ("enc_rsa_pubkey.pem", "rb") as key_file:
            self.pub_rsa_key = RSA.import_key(key_file.read())
        self.aes_key=b""

    def send_msg(self, data: bytes):
        """
        Generate a random IV, encrypt the data with AES and send the IV and the ciphertext

        Args:
            data (bytes): the data to send
        """
        iv = get_random_bytes(16)
        aes_cipher = AES.new(self.aes_key,AES.MODE_CBC,iv=iv)
        enc_msg = aes_cipher.encrypt(pad(data,16))
        self.sendall(int.to_bytes(len(iv+enc_msg), 4, "big"))
        self.sendall(iv+enc_msg)  

    def recv_msg(self) -> bytes:
        """
        recv the IV and the ciphertext, decrypt the ciphertext and return the plaintext

        Returns:
            bytes: the plaintext
        """
        length = int.from_bytes(self.recvall(4), "big")
        data = self.recvall(length)
        iv=data[:16]
        ciphertext=data[16:]
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)
        msg = aes_cipher.decrypt(ciphertext)
        return unpad(msg,16)

    def start(self):
        """
        perform the handshake at the start of the connection
        generate an AES key, encrypt it with the RSA public key of the server and send it to the server
        """
        self.aes_key = get_random_bytes(16)
        rsa_cipher = PKCS1_OAEP.new(self.pub_rsa_key)
        enc_key = rsa_cipher.encrypt(self.aes_key)
        self.sendall(int.to_bytes(len(enc_key), 4, "big"))
        self.sendall(enc_key)