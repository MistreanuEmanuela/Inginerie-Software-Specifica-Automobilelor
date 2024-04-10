import socket
import select
import pickle
import datetime

from typing import *


class ObjectSocketParams:
    """
       A class containing all the parameters used.

       Attributes:
           OBJECT_HEADER_SIZE_BYTES (int): Size of header in bytes used in transmission.
           DEFAULT_TIMEOUT_S (int): Default timeout value in seconds (max time that is waiting for a response).
           CHUNK_SIZE_BYTES (int): Size of the data chunk in bytes.
       """
    OBJECT_HEADER_SIZE_BYTES = 4
    DEFAULT_TIMEOUT_S = 1
    CHUNK_SIZE_BYTES = 1024


class ObjectSenderSocket:
    """
    A class representing a socket for sending objects.

    Attributes:
        ip (str): IP address to bind the socket.
        port (int): Port number to bind the socket.
        sock (socket.socket): TCP socket object.
        conn (socket.socket): Connected socket object.
        print_when_awaiting_receiver (bool): Flag for printing when awaiting receiver connection.
        print_when_sending_object (bool): Flag for printing when sending an object.
    """

    def __init__(self, ip: str, port: int,
                 print_when_awaiting_receiver: bool = False,
                 print_when_sending_object: bool = False):
        """
        The class constructor initializing the attributes.

        :param ip: IP address.
        :param port: Port number for binding.
        :param print_when_awaiting_receiver: Flag for awaiting, set to False by default.
        :param print_when_sending_object: Flag for sending, set to False by default.
        """
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.conn = None

        self.print_when_awaiting_receiver = print_when_awaiting_receiver
        self.print_when_sending_object = print_when_sending_object

        self.await_receiver_connection()

    def await_receiver_connection(self):
        """
        A method that waits to receive a connection.
        When a connection is established, the 'conn' attribute is set, indicating the connected socket.
        """
        if self.print_when_awaiting_receiver:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] awaiting receiver connection...')

        self.sock.listen(1)
        self.conn, _ = self.sock.accept()

        if self.print_when_awaiting_receiver:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] receiver connected')

    def close(self):
        """
        A method that closes the connection and set the 'conn' attribute to None.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def is_connected(self) -> bool:
        """
        A method that checks if a connection is established using the 'conn' attribute.

        :return: True if a connection exists, False otherwise.
        """
        return self.conn is not None

    def send_object(self, obj: Any):
        """
        Sends an object through the socket.

        :param obj: Object to send.
        """
        try:
            data = pickle.dumps(obj)
            data_size = len(data)
            data_size_encoded = data_size.to_bytes(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES, 'little')
            self.conn.sendall(data_size_encoded)
            self.conn.sendall(data)
            if self.print_when_sending_object:
                print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] Sent object of size {data_size} bytes.')
        except Exception as e:
            print(f'Error occurred while sending object: {e}')

class ObjectReceiverSocket:

    """
    A class representing a socket for receiving objects.

    Attributes:
        ip (str): IP address to connect to.
        port (int): Port number to connect to.
        conn (socket.socket): Connected socket object.
        print_when_connecting_to_sender (bool): Flag for printing when connecting to the sender.
        print_when_receiving_object (bool): Flag for printing when receiving an object.
    """
    ip: str
    port: int
    conn: socket.socket
    print_when_connecting_to_sender: bool
    print_when_receiving_object: bool

    def __init__(self, ip: str, port: int,
                 print_when_connecting_to_sender: bool = False,
                 print_when_receiving_object: bool = False):
        """
           The class constructor initializing the attributes.

           :param ip: IP address.
           :param port: Port number for binding.
           :param print_when_connecting_to_sender: Flag for when make connection to sender, set to False by default.
           :param print_when_receiving_object: Flag for receiving, set to False by default.
        """

        self.ip = ip
        self.port = port
        self.print_when_connecting_to_sender = print_when_connecting_to_sender
        self.print_when_receiving_object = print_when_receiving_object

        self.connect_to_sender()

    def connect_to_sender(self):
        """
        Connects to the sender.
        When a connection is established, the 'conn' attribute is set, indicating the connected socket.

        """

        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connecting to sender...')

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))

        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connected to sender')

    def close(self):
        """
            A method that closes the connection and set the 'conn' attribute to None.
        """
        self.conn.close()
        self.conn = None

    def is_connected(self) -> bool:
        """
              A method that checks if a connection is established using the 'conn' attribute.

              :return: True if a connection exists, False otherwise.
        """
        return self.conn is not None

    def recv_object(self) -> Any:
        """
          Receives an object from the socket.
        :return: the obj receive
        """
        obj_size_bytes = self._recv_object_size()
        data = self._recv_all(obj_size_bytes)
        obj = pickle.loads(data)
        if self.print_when_receiving_object:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] Received object of size {obj_size_bytes} bytes.')
        return obj

    def _recv_with_timeout(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> Optional[bytes]:
        """
        Receive data from the connection with a specified timeout.
        :param n_bytes: The number of bytes to receive.
        :param timeout_s: The timeout value in seconds (Defaults to ObjectSocketParams.DEFAULT_TIMEOUT_S)

        :return: The received data as bytes if data is received within the timeout, otherwise None.

        """
        rlist, _1, _2 = select.select([self.conn], [], [], timeout_s)
        if rlist:
            data = self.conn.recv(n_bytes)
            return data
        else:
            return None  # Only returned on timeout

    def _recv_all(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> bytes:
        """
        Receive all data from the connection until the specified number of bytes is received or a timeout occurs.

        :param n_bytes: The total number of bytes to receive.
        :param timeout_s: The timeout value in seconds.
        :return:The received data as bytes.

        Raises:
        socket.error: If a timeout occurs without receiving all expected data.
        """
        data = []
        left_to_recv = n_bytes
        while left_to_recv > 0:
            desired_chunk_size = min(ObjectSocketParams.CHUNK_SIZE_BYTES, left_to_recv)
            chunk = self._recv_with_timeout(desired_chunk_size, timeout_s)
            if chunk is not None:
                data += [chunk]
                left_to_recv -= len(chunk)
            else:  # no more data incoming, timeout
                bytes_received = sum(map(len, data))
                raise socket.error(f'Timeout elapsed without any new data being received. '
                                   f'{bytes_received} / {n_bytes} bytes received.')
        data = b''.join(data)
        return data

    def _recv_object_size(self) -> int:
        """
        Receive the size of the object from the connection.

        Returns:
            int: The size of the object in bytes.

        Raises:
            socket.error: If a timeout occurs without receiving the object size header.
        """
        data = self._recv_all(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES)
        obj_size_bytes = int.from_bytes(data, 'little')
        return obj_size_bytes


