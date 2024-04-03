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
        "view available cars": 9
    }
    CLIENT_TYPE = {
        "Owner": 0,
        "Renter": 1
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
            while True:
                client_id = 0
                print("What do you want to do?")
                print("0. Register renter \n1. Register owner \n2. Login renter \n3. Login owner")
                message_id = int(input("Enter your choice: "))
                if message_id == 1 or message_id == 3:
                    client_type_id = self.CLIENT_TYPE.get("Owner")
                else:
                    if message_id == 0 or message_id == 2:
                        client_type_id = self.CLIENT_TYPE.get("Renter")
                    else:
                        client_type_id = 100
                payload = "username : "
                payload += str(input("Enter username: "))
                payload += " password : "
                payload += str(input("Enter password: "))
                message = Message(client_id, client_type_id, message_id, payload)
                print("Sending message to server:", message.to_string())
                self.send_message(message)
                sleep(5)
                message = self.client_socket.recv(1024).decode()
                print("Received message from server:", message)
                if message_id == 3:
                    client_id == message[-1]
                    print("5. Post a car \n")
                    message_id = input("Enter your choise")
                    payload = str(input("Enter car number: "))
                    message = Message(client_id, client_type_id, message_id, payload)
                    self.send_message(message)
                    sleep(5)
                    message = self.client_socket.recv(1024).decode()
                    print("Received message from server:", message)
                if message_id == 2:
                    client_id == message[-1]
                    print("9. View available cars \n")
                    message_id = input("Enter your choise")
                    message = Message(client_id, client_type_id, message_id, payload)
                    self.send_message(message)
                    sleep(5)
                    message = self.client_socket.recv(1024).decode()
                    print("Received message from server:", message)
                    payload = input("Choose a car from this list to rent : ")
                    message_id = 6
                    message = Message(client_id, client_type_id, message_id, payload)
                    self.send_message(message)
                    sleep(5)
                    message = self.client_socket.recv(1024).decode()
                    print("Received message from server:", message)
                    print("7. Stop renting \n")
                    integer = input("7. Stop renting \n")
                    message = Message(client_id, client_type_id, 7, payload)
                    print(message)
                    self.send_message(message)
                    sleep(5)
                    message = self.client_socket.recv(1024).decode()
                    print("Received message from server:", message)


        except KeyboardInterrupt:
            print("Closing connection...")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    client = Client()
    client.run()
