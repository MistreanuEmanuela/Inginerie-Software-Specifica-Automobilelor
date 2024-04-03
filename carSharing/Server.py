import socket
from Message import Message
import re
import threading

class Server:
    MESSAGE_TYPES = {
        0: "Register Renter",
        1: "Register Owner",
        2: "login renter",
        3: "login owner",
        4: "Post Car",
        5: "Request Car",
        6: "Start Rental",
        7: "End Rental",
        8: "Car Connection"
    }
    CLIENT_TYPE = {
        0: "Owner",
        1: "Renter"
    }

    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.listUser = [("e","e")]
        self.listOwner = [("e","e")]
        self.listCars = []
        self.listCarsRenter = []
        self.carsWaiting = []

    def handle_message_mobileApp(self, client_socket, addr):
        try:
            while True:
                message_str = client_socket.recv(1024).decode()
                try:
                    exception,message = Message.from_string(message_str)
                    print(f"{message.client_id}, TYPE {self.CLIENT_TYPE.get(message.client_type)}:"
                          f" {self.MESSAGE_TYPES.get(message.message_id)} - Payload: {message.payload}")
                    print(f"Received message from Client: {message}")
                    if message.message_id == 0:
                        response = self.handleRegisterUser(message.payload)
                        print(response)
                    if message.message_id == 1:
                        response = self.handleRegisterOwner(message.payload)
                    if message.message_id == 2:
                        response = self.handleLoginUser(message.payload)
                        print(response)
                    if message.message_id == 3:
                        response = self.handleLoginOwner(message.payload)
                    if message.message_id == 5:
                        response = self.handleCarPost(message.payload, message.client_id, message.client_type)
                        if response == "Added":
                            self.send_response(self.listCars[-1][2], f"This car was post by client_id {self.listCars[-1][1]}")
                    if message.message_id == 8:
                        self.carsWaiting.append((message.payload, client_socket))
                        response = ""
                    if message.message_id == 9:
                        cars = self.handleViewCars()
                        response = ""
                        for element in cars:
                           response += f"{element[0]}. {element[1]}"

                    if message.message_id == 6:
                      self.handleStartRent(message.client_id, message.payload, client_socket)
                      response = ""
                    if message.message_id == 7:
                      self.handleEndRent(message.client_id, message.payload, client_socket)
                      response = ""

                    if message.message_id == 11:
                        if message.payload == "connection accepted":
                            self.send_response(client_socket, f"Client starting renter")

                    if message.message_id == 12:
                        if message.payload == "connection accepted end":
                            self.send_response(client_socket, f"Client stop renter")

                    self.send_response(client_socket, response)
                except Exception:
                    return "invalid format"
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            client_socket.close()

    def send_response(self, client_socket, message_response):
        response_message = message_response
        client_socket.send(response_message.encode())
        print("Response sent to the client.")


    def handleRegisterOwner(self, payload):
        pattern = r"username\s*:\s*(\w+)\s*password\s*:\s*(\w+)"
        match = re.search(pattern, payload)

        if match:
            username = match.group(1)
            password = match.group(2)

            if (username, password) in self.listOwner:
                return "You already have an account"
            else:
                self.listOwner.append((username, password))
                return "Account created successful"
        else:
            return "No username and password found."

    def handleLoginOwner(self, payload):
        pattern = r"username\s*:\s*(\w+)\s*password\s*:\s*(\w+)"
        match = re.search(pattern, payload)
        if match:
            username = match.group(1)
            password = match.group(2)
            if (username, password) in self.listOwner:
                return f"Connect successful {self.listOwner.index((username,password))}"
            else:
                return "Wrong credentials"
        else:
            return "No username and password found."

    def handleRegisterUser(self, payload):
        pattern = r"username\s*:\s*(\w+)\s*password\s*:\s*(\w+)"
        match = re.search(pattern, payload)

        if match:
            username = match.group(1)
            password = match.group(2)

            if (username, password) in self.listUser:
                return "You already have an account"
            else:
                self.listUser.append((username, password))
                return "Account created successful"
        else:
            return "No username and password found."

    def handleLoginUser(self, payload):
        print("Here")
        pattern = r"username\s*:\s*(\w+)\s*password\s*:\s*(\w+)"
        match = re.search(pattern, payload)

        if match:
            username = match.group(1)
            password = match.group(2)
            print(username, password)

            if (username, password) in self.listUser:
                response = f"Connect successful {self.listUser.index((username,password))}"
                return response
            else:
                print(self.listUser)
                return "Wrong credentials"
        else:
            return "No username and password found."

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(25)
        print("Server listening for connections...")

        try:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr} has been established.")
                client_thread = threading.Thread(target=self.handle_message_mobileApp, args=(client_socket,addr))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            server_socket.close()

    def handleCarPost(self, payload, client_id, client_type):
        if client_type != 0:
            return "Invalid request from this type of user"
        for element in self.carsWaiting:
            if payload in element[0]:
                for element2 in self.listCars:
                    if payload in element2[0]:
                        return "The car is already added"
                self.listCars.append((payload, client_id, element[1]))
                return "Added"
        return "The car is not connected to server!"

    def handleViewCars(self):
        list_car = []
        for ind, element in enumerate(self.listCars):
            list_car.append((ind, element[0]))
        return list_car

    def handleStartRent(self, client_id, payload, client_socket):
        for ind, element in enumerate(self.listCars):
            if ind == int(payload):
                print(element[2])
                del self.listCars[ind]
                self.listCarsRenter.append(element)


        car_socket = self.listCarsRenter[int(payload)][2]
        self.send_response(car_socket, "The server is trying to create connection")
        self.send_response(client_socket, "Started successful")

    def handleEndRent(self, client_id, payload, client_socket):
        for ind, element in enumerate(self.listCarsRenter):
            if ind == int(payload):
                print(element[2])
                del self.listCarsRenter[ind]
                self.listCars.append(element)

        car_socket = self.listCars[int(payload)][2]
        self.send_response(car_socket, "The server is trying to create connection end")
        self.send_response(client_socket, "Ended successful")


if __name__ == "__main__":
    server = Server()
    server.start()
