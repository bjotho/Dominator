import socket
import time
import threading
from text_formatting import RED, END
from constants import HEADER_SIZE, DATA_LEFT_SIZE, PORT, MAX_SIZE, FORMAT, DISCONNECT, NOTHING, LENGTH, RESPOND,\
    END, DATA

LENGTH_SIZE = HEADER_SIZE - (DATA_LEFT_SIZE + 2)
RESPOND_FLAG = LENGTH_SIZE
END_FLAG = LENGTH_SIZE + 1


class Server:
    def __init__(self):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", PORT))
        self.server_socket.listen()
        self.socket_list = [self.server_socket]
        self.clients = {}

        print(f"[LISTENING] Listening for connections on {self.IP}:{PORT}")

    def handle_client(self, client_socket, client_address):
        print(f"[NEW CONNECTION] {client_address} connected")
        username = ""
        while True:
            user = self.receive_msg(client_socket)
            if user is False:
                print("User is False")
                continue
            username = user[DATA]
            self.socket_list.append(client_socket)
            self.clients[client_socket] = username
            print(f"{client_address} {username}")
            break

        # connected = True
        # while connected:
        #     message = self.receive_msg(client_socket)
        #     if not message or message[DATA] == DISCONNECT or not self.clients[client_socket]:
        #         connected = False
        #     else:
        #         self.message_list[client_socket] = message[DATA]
        #
        # print(f"[LOST CONNECTION] {client_address} {username}")
        # self.socket_list.remove(client_socket)
        # del self.clients[client_socket]
        # client_socket.close()

    def close_client_connection(self, client_socket):
        print(f"[LOST CONNECTION] {client_socket.getpeername()}")
        self.socket_list.remove(client_socket)
        del self.clients[client_socket]
        client_socket.close()

    def receive_msg(self, client_socket):
        """Receive a message from client_socket"""

        try:
            msg_len, respond, end, data = self.receive_full_msg(client_socket)
            end = "\n" if end else ""
            data = data.decode(FORMAT)
            if data == NOTHING:
                data = ""
            # print(f"[RECEIVE] {client_socket.getpeername()} {msg_len}:{data}")
            return {LENGTH: msg_len,
                    RESPOND: respond,
                    END: end,
                    DATA: data}
        except Exception as e:
            print(f"{RED}{e}{END}")
            return False

    def receive_full_msg(self, client_socket):
        msg_len, respond, end, data_left = self.receive_header(client_socket)
        data = client_socket.recv(msg_len)
        msg_len_part = len(data)

        while msg_len_part < msg_len:
            resend_len = msg_len - msg_len_part
            self.request_resend(client_socket, data_left=resend_len)
            _msg_len, _, _, _ = self.receive_header(client_socket)
            new_data = client_socket.recv(_msg_len)
            msg_len_part += len(new_data)
            data += new_data

        self.request_resend(client_socket, 0)
        return msg_len, respond, end, data

    @staticmethod
    def receive_header(client_socket):
        msg_header = client_socket.recv(HEADER_SIZE).decode(FORMAT)
        if not len(msg_header):
            return False

        msg_len = int(msg_header[:LENGTH_SIZE].strip())
        respond = int(msg_header[RESPOND_FLAG])
        end = int(msg_header[END_FLAG])
        data_left = int(msg_header[-DATA_LEFT_SIZE:].strip())

        return msg_len, respond, end, data_left

    def request_resend(self, client, data_left):
        msg_header = self.encode_header(0, 0, 1, data_left)
        client.send(msg_header)

    def send_msg(self, msg, client=None, respond=0, end=1):
        """Sends msg to client socket specified in client (all clients if not specified).
        respond (int) [0, 1]: Whether to require response from clients.
        end (int) [0, 1]: Whether to insert newline after end of line."""

        if not client:
            for c in self.clients:
                self.send_full_message(c, msg, respond, end)
        elif type(client) is socket.socket:
            self.send_full_message(client, msg, respond, end)
        elif type(client) is list:
            for c in client:
                self.send_full_message(c, msg, respond, end)
        else:
            return False

        if respond and type(client) is socket.socket:
            response = self.receive_msg(client)[DATA]
            if response is False or response == DISCONNECT:
                self.close_client_connection(client)
                return False
            return response

        return True

    def send_full_message(self, client, msg, respond, end):
        """Send msg to client in chunks of size MAX_SIZE.
        client (socket.socket): client socket to send message to.
        msg (str): message payload to send to client.
        respond (int) [0, 1]: Whether to require response from clients.
        end (int) [0, 1]: Whether to insert newline after end of line."""

        full_msg = self.encode_msg_body(msg)
        full_msg_len = len(full_msg)
        _respond = respond
        _end = end
        if full_msg_len > MAX_SIZE:
            _respond = 0
            _end = 0

        chunks = [full_msg[i:i + MAX_SIZE] for i in range(0, len(full_msg), MAX_SIZE)]

        for n, chunk in enumerate(chunks):
            data_left = len(chunk)
            if n == len(chunks) - 1:
                _respond = respond
                _end = end
            while data_left > 0:
                msg_header = self.encode_header(data_left, _respond, _end, -1)
                msg = msg_header + chunk[len(chunk) - data_left:]
                client.send(msg)
                # print(f"[SEND] {msg}")
                _, _, _, data_left = self.receive_header(client)

    @staticmethod
    def encode_header(msg_len, respond, end, data_left):
        msg_header = f"{msg_len:<{LENGTH_SIZE}}{respond}{end}{data_left:<{DATA_LEFT_SIZE}}"
        return msg_header.encode(FORMAT)

    @staticmethod
    def encode_msg_body(msg):
        if msg == "":
            msg = NOTHING
        try:
            msg = msg.encode(FORMAT)
        except AttributeError as e:
            print(f"{RED}{e}{END}")
            msg = msg.__str__().encode(FORMAT)
        return msg

    def accept_incoming_connections(self, num=1):
        """Sets up handling for incoming clients.
        Num specifies number of clients to accept."""
        try:
            accepted = 0
            while accepted < num:
                client_socket, client_address = self.server_socket.accept()
                print(f"[ACCEPTED] Accepted new connection from {client_address[0]}:{client_address[1]}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
                accepted += 1

            while len(self.clients) < num:
                time.sleep(1)
        except:
            print("[ACCEPT ERROR]")
