class Message:
    def __init__(self, client_id, client_type, message_id, payload):
        self.client_id = client_id
        self.client_type = client_type
        self.message_id = message_id
        self.payload = payload

    def __str__(self):
        return f"Client ID: {self.client_id}, Client Type: {self.client_type}, Message ID: {self.message_id}, Payload: {self.payload}"

    @classmethod
    def from_string(cls, message_str):
        parts = message_str.split(",", 4)
        for part in parts:
            if part == "":
                return "Invalid message format", None

        client_id = int(parts[0])
        client_type = int(parts[1])
        message_id = int(parts[2])
        payload = parts[3]

        return None, cls(client_id, client_type, message_id, payload)

    def to_string(self):
        return f"{self.client_id},{self.client_type},{self.message_id},{self.payload}"