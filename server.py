import socket
import time
import threading
from constants import HEADER_SIZE, PORT, FORMAT, DISCONNECT_MESSAGE, LENGTH, RESPOND, EMPTY, END, DATA


class Server:
    def __init__(self):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, PORT))
        self.server_socket.listen()
        self.socket_list = [self.server_socket]
        self.clients = {}
        self.message_list = {}

        print(f"[LISTENING] Listening for connections on {self.IP}:{PORT}")

    def handle_client(self, client_socket, client_address):
        print(f"[NEW CONNECTION] {client_address} connected")
        username = ""
        while True:
            time.sleep(0.1)
            user = self.receive_msg(client_socket)
            if user is False:
                continue
            username = user[DATA]
            self.socket_list.append(client_socket)
            self.clients[client_socket] = username
            self.message_list[client_socket] = None
            print(f"{client_address} {username}")
            break

        connected = True
        while connected:
            message = self.receive_msg(client_socket)
            if not message or message[DATA] == DISCONNECT_MESSAGE or not self.clients[client_socket]:
                connected = False
            else:
                self.message_list[client_socket] = message[DATA]

        print(f"[LOST CONNECTION] {client_address} {username}")
        self.socket_list.remove(client_socket)
        del self.clients[client_socket]
        client_socket.close()

    @staticmethod
    def receive_msg(client_socket):
        """Receive a message from client_socket"""
        try:
            msg_header = client_socket.recv(HEADER_SIZE).decode(FORMAT)
            if not len(msg_header):
                return False
            msg_len = int(msg_header[:-3].strip())
            respond = int(msg_header[-3])
            empty = int(msg_header[-2])
            end = "\n" if int(msg_header[-1]) else ""
            if msg_len == 0:
                data = ""
            else:
                data = client_socket.recv(msg_len).decode(FORMAT)
            print(f"[RECEIVE] {client_socket} {msg_len}:{data}")
            return {LENGTH: msg_len,
                    RESPOND: respond,
                    EMPTY: empty,
                    END: end,
                    DATA: data}
        except:
            return False

    def send_msg(self, msg, client=None, respond=0, end=1):
        """Sends msg to client socket specified in client (all clients if not specified).
        respond [0, 1]: Whether to require response from clients.
        empty [0, 1]: Whether message is empty.
        end [0, 1]: Whether to insert newline after end of line."""
        empty = 0
        if msg == "":
            empty = 1
        msg = msg.encode(FORMAT)
        msg_header = f"{len(msg):<{HEADER_SIZE - 3}}{str(respond)}{str(empty)}{str(end)}".encode(FORMAT)
        if not client:
            for c in self.clients:
                c.send(msg_header + msg)

        elif type(client) is socket.socket:
            client.send(msg_header + msg)
        elif type(client) is list:
            for c in client:
                c.send(msg_header + msg)
        else:
            return False

        if respond:
            assert type(client) is socket.socket
            self.message_list[client] = None
            while not self.message_list[client]:
                time.sleep(0.1)
                # print(f"{self.clients[client]} message_list: {self.message_list[client]}")

            response = "".join(self.message_list[client])
            return response

        return True

    def accept_incoming_connections(self, num=1):
        """Sets up handling for incoming clients.
        Num specifies number of clients to accept."""
        try:
            accepted = 0
            while accepted < num:
                client_socket, client_address = self.server_socket.accept()
                accepted += 1
                print(f"[ACCEPTED] Accepted new connection from {client_address[0]}:{client_address[1]}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

            while len(self.clients) < num:
                time.sleep(1)
        except:
            print("[ACCEPT ERROR]")
