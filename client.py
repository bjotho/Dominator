import socket
from constants import HEADER_SIZE, PORT, FORMAT, LENGTH, RESPOND, EMPTY, END, DATA

IP = socket.gethostname()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


def receive_msg(client):
    try:
        msg_header = client.recv(HEADER_SIZE).decode(FORMAT)
        if not len(msg_header):
            return False
        msg_len = int(msg_header[:-3].strip())
        respond = int(msg_header[-3])
        empty = int(msg_header[-2])
        end = "\n" if int(msg_header[-1]) else ""
        data = client_socket.recv(msg_len).decode(FORMAT)
        return {LENGTH: msg_len,
                RESPOND: respond,
                EMPTY: empty,
                END: end,
                DATA: data}
    except:
        return False


def send_msg(msg, respond=0, end=1):
    """Sends msg to server socket.
    respond [0, 1]: Whether to require response from the server.
    empty [0, 1]: Whether message is empty.
    end [0, 1]: Whether to insert newline after end of line."""
    empty = 0
    if msg == "":
        empty = 1
    msg = msg.encode(FORMAT)
    msg_header = f"{len(msg):<{HEADER_SIZE - 3}}{str(respond)}{str(empty)}{str(end)}".encode(FORMAT)
    client_socket.send(msg_header + msg)
    return True


username = ""
while not username:
    username = input("Username: ")
enc_username = username.encode(FORMAT)
username_header = f"{len(enc_username):<{HEADER_SIZE - 3}}{str(0)}{str(0)}{str(1)}".encode(FORMAT)
client_socket.send(username_header + enc_username)

while True:
    new_message = None
    while not new_message:
        new_message = receive_msg(client_socket)
    print(new_message[DATA], end=new_message[END])
    if new_message[RESPOND]:
        response = ""
        while not response:
            response = input()
            if response or new_message[EMPTY]:
                send_msg(response)
