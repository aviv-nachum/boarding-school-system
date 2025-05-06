"""
Handles encrypted communication between the client and server using RSA and AES encryption.
"""

from socket import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import os

def generate_rsa_keys():
    """
    Generates RSA public and private keys and saves them to files.
    Removes existing keys if they already exist.
    """
    # Check if private key file exists and remove it
    if os.path.exists("enc_rsa_privkey.pem"):
        os.remove("enc_rsa_privkey.pem")
    # Check if public key file exists and remove it
    if os.path.exists("enc_rsa_pubkey.pem"):
        os.remove("enc_rsa_pubkey.pem")

    # Generate a new RSA key pair
    key = RSA.generate(2048)
    private_key = key.export_key()  # Export the private key
    public_key = key.publickey().export_key()  # Export the public key

    # Save the private key to a file
    with open("enc_rsa_privkey.pem", "wb") as priv_file:
        priv_file.write(private_key)

    # Save the public key to a file
    with open("enc_rsa_pubkey.pem", "wb") as pub_file:
        pub_file.write(public_key)

# Generate RSA keys if they don't already exist
generate_rsa_keys()

class Connection:
    """
    Represents a basic network connection with methods for sending and receiving data.
    """
    def __init__(self, host: str, port: int, conn: socket):
        """
        Initializes the connection with the given host, port, and socket.

        Args:
            host (str): The host address.
            port (int): The port number.
            conn (socket): The socket object.
        """
        self.host = host
        self.port = port
        self.conn = conn

    def sendall(self, data: bytes):
        """
        Sends all the given bytes over the socket.

        Args:
            data (bytes): The data to send.
        """
        self.conn.sendall(data)

    def recvall(self, size: int) -> bytes:
        """
        Receives a fixed amount of data from the socket.

        Args:
            size (int): The number of bytes to receive.

        Returns:
            bytes: The received data.
        """
        ans = b""
        while len(ans) < size:
            ans += self.conn.recv(size - len(ans))  # Keep receiving until the required size is met
        return ans

    def send_msg(self, msg: bytes):
        """
        Sends a message with its length prepended.

        Args:
            msg (bytes): The message to send.
        """
        self.sendall(int.to_bytes(len(msg), 4, "big"))  # Send the length of the message first
        self.sendall(msg)  # Send the actual message

    def recv_msg(self) -> bytes:
        """
        Receives a message with its length prepended.

        Returns:
            bytes: The received message.
        """
        length = int.from_bytes(self.recvall(4), "big")  # Read the length of the message
        return self.recvall(length)  # Read the actual message based on the length

    def connect(self):
        """
        Connects the socket to the specified host and port.
        """
        self.conn.connect((self.host, self.port))

    def start(self) -> bool:
        """
        Placeholder for starting the connection.
        """
        pass

    def close(self):
        """
        Closes the socket connection.
        """
        self.conn.close()


class ServerEncConnection(Connection):
    """
    Represents an encrypted server connection using RSA and AES encryption.
    """
    def __init__(self, host, port, conn):
        """
        Initializes the server connection and imports the RSA private key.

        Args:
            host (str): The host address.
            port (int): The port number.
            conn (socket): The socket object.
        """
        Connection.__init__(self, host, port, conn)
        with open("enc_rsa_privkey.pem", "rb") as key_file:
            self.rsa_key = RSA.import_key(key_file.read())
        self.aes_key = b""

    def send_msg(self, data: bytes):
        """
        Encrypts the data with AES and sends it along with the IV.

        Args:
            data (bytes): The data to send.
        """
        iv = get_random_bytes(16)  # Generate a random initialization vector (IV)
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)  # Create an AES cipher in CBC mode
        enc_msg = aes_cipher.encrypt(pad(data, 16))  # Encrypt the padded data
        self.sendall(int.to_bytes(len(iv + enc_msg), 4, "big"))  # Send the length of the encrypted message
        self.sendall(iv + enc_msg)  # Send the IV and the encrypted message

    def recv_msg(self) -> bytes:
        """
        Receives and decrypts an AES-encrypted message.

        Returns:
            bytes: The decrypted plaintext.
        """
        length = int.from_bytes(self.recvall(4), "big")  # Read the length of the encrypted message
        data = self.recvall(length)  # Read the actual encrypted message
        iv = data[:16]  # Extract the IV
        ciphertext = data[16:]  # Extract the ciphertext
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)  # Create an AES cipher with the IV
        msg = aes_cipher.decrypt(ciphertext)  # Decrypt the ciphertext
        return unpad(msg, 16)  # Remove padding and return the plaintext

    def start(self):
        """
        perform the handshake at the start of the connection
        receive and decrypt the RSA-        encrypted AES key from the client
        """
        length = int.from_bytes(self.recvall(4), "big")
        enc_key = self.recvall(length)
        rsa_cipher = PKCS1_OAEP.new(self.rsa_key)
        self.aes_key = rsa_cipher.decrypt(enc_key)


class ClientEncConnection(Connection):
    """
    Represents an encrypted client connection using RSA and AES encryption.
    """
    def __init__(self, host, port, conn):
        """
        Initializes the client connection and imports the RSA public key.

        Args:
            host (str): The host address.
            port (int): The port number.
            conn (socket): The socket object.
        """
        Connection.__init__(self, host, port, conn)
        with open("enc_rsa_pubkey.pem", "rb") as key_file:
            self.pub_rsa_key = RSA.import_key(key_file.read())
        self.aes_key = b""

    def send_msg(self, data: bytes):
        """
        Encrypts the data with AES and sends it along with the IV.

        Args:
            data (bytes): The data to send.
        """
        iv = get_random_bytes(16)  # Generate a random initialization vector (IV)
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)  # Create an AES cipher in CBC mode
        enc_msg = aes_cipher.encrypt(pad(data, 16))  # Encrypt the padded data
        self.sendall(int.to_bytes(len(iv + enc_msg), 4, "big"))  # Send the length of the encrypted message
        self.sendall(iv + enc_msg)  # Send the IV and the encrypted message

    def recv_msg(self) -> bytes:
        """
        Receives and decrypts an AES-encrypted message.

        Returns:
            bytes: The decrypted plaintext.
        """
        length = int.from_bytes(self.recvall(4), "big")  # Read the length of the encrypted message
        data = self.recvall(length)  # Read the actual encrypted message
        iv = data[:16]  # Extract the IV
        ciphertext = data[16:]  # Extract the ciphertext
        aes_cipher = AES.new(self.aes_key, AES.MODE_CBC, iv=iv)  # Create an AES cipher with the IV
        msg = aes_cipher.decrypt(ciphertext)  # Decrypt the ciphertext
        return unpad(msg, 16)  # Remove padding and return the plaintext

    def start(self):
        """
        Starts the encrypted connection by sending the AES key encrypted with the RSA public key.
        """
        self.connect()  # Ensure the connection is established
        self.aes_key = get_random_bytes(16)
        rsa_cipher = PKCS1_OAEP.new(self.pub_rsa_key)
        enc_key = rsa_cipher.encrypt(self.aes_key)
        self.sendall(int.to_bytes(len(enc_key), 4, "big"))
        self.sendall(enc_key)