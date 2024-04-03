import socket
from time import sleep

from Message import Message

class Client:
    MESSAGE_TYPES = {
        "register renter": 0,
        "register owner": 1,
        "login renter": 2,
        "login owner": 3,
        "post car": 4,
        "request car": 5,
        "start rental": 6,
        "end rental": 7,
    }
    CLIENT_TYPE = {
        "Owner": 0,
        "Renter": 1,
        "Car": 3
    }

    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_message(self, message):
        self.client_socket.send(message.to_string().encode())


    def receive_message(self):
        try:
            while True:
                message = self.client_socket.recv(1024).decode()
                print("Received message from server:", message)
        except KeyboardInterrupt:
            print("Closing connection...")
        finally:
            self.client_socket.close()

    def run(self):
        try:
            client_id = 0
            payload = "BT02EMA"
            message = Message(client_id, 3, 8, payload)
            print("Sending message to server:", message.to_string())
            self.send_message(message)
            while True:
                sleep(5)
                message = self.client_socket.recv(1024).decode()
                print("Received message from server:", message)
                if message == "The server is trying to create connection":
                    message = Message(client_id, 3, 11, "connection accepted")
                    print("Sending message to server:", message.to_string())
                    self.send_message(message)
                if message == "The server is trying to create connection end":
                    message = Message(client_id, 3, 12, "connection accepted end")
                    print("Sending message to server:", message.to_string())
                    self.send_message(message)

        except KeyboardInterrupt:
            print("Closing connection...")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    client = Client()
    client.run()
