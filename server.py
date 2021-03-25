import socket
import time
import threading
from text_formatting import RED, END
from constants import HEADER_SIZE, DATA_LEFT_SIZE, PORT, FORMAT, DISCONNECT, NOTHING, LENGTH, RESPOND,\
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
            print(f"[RECEIVE] {client_socket.getpeername()} {msg_len}:{data}")
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
        print(f"data: {data}")
        msg_len_part = len(data)

        while msg_len_part < msg_len:
            resend_len = msg_len - msg_len_part
            self.request_resend(client_socket, data_left=resend_len)
            _msg_len, _respond, _end, _data_left = self.receive_header(client_socket)
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
        msg_header, msg = self.encode_msg("", 0, 1, data_left)
        client.send(msg_header)

    def send_msg(self, msg, client=None, respond=0, end=1):
        """Sends msg to client socket specified in client (all clients if not specified).
        respond [0, 1]: Whether to require response from clients.
        end [0, 1]: Whether to insert newline after end of line.
        data_left (int): how much data was lost and needs to be re-sent."""
        msg_header, msg = self.encode_msg(msg, respond, end, -1)
        full_msg = msg_header + msg
        if not client:
            for c in self.clients:
                self.send_full_message(c, full_msg)
        elif type(client) is socket.socket:
            self.send_full_message(client, full_msg)
        elif type(client) is list:
            for c in client:
                self.send_full_message(c, full_msg)
        else:
            return False

        if respond and type(client) is socket.socket:
            response = self.receive_msg(client)[DATA]
            if response is False or response == DISCONNECT:
                self.close_client_connection(client)
                return False
            return response

        return True

    def send_full_message(self, client, full_msg):
        msg_len = len(full_msg) - HEADER_SIZE
        data_left = msg_len
        while data_left > 0:
            msg = full_msg[msg_len - data_left:]
            client.send(msg)
            print(f"[SEND] {msg}")
            _msg_len, _respond, _end, data_left = self.receive_header(client)

    @staticmethod
    def encode_msg(msg, respond, end, data_left):
        if msg == "" and data_left < 0:
            msg = NOTHING
        try:
            msg = msg.encode(FORMAT)
        except AttributeError as e:
            print(f"{RED}{e}{END}")
            msg = msg.__str__().encode(FORMAT)
        msg_header = f"{len(msg):<{LENGTH_SIZE}}{respond}{end}{data_left:<{DATA_LEFT_SIZE}}"
        return msg_header.encode(FORMAT), msg

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
