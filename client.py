import sys
import socket
from termios import tcflush, TCIFLUSH
from constants import HEADER_SIZE, DATA_LEFT_SIZE, PORT, FORMAT, DISCONNECT, NOTHING, OVERHEAD, GAME_OVER, LENGTH,\
    RESPOND, END, DATA

LENGTH_SIZE = HEADER_SIZE - (DATA_LEFT_SIZE + 2)
RESPOND_FLAG = LENGTH_SIZE
END_FLAG = LENGTH_SIZE + 1

IP = socket.gethostname()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((IP, PORT))
# client_socket.setblocking(False)


def receive_msg():
    try:
        msg_len, respond, end, data = receive_full_msg()
        end = "\n" if end else ""
        data = data.decode(FORMAT)
        if data == NOTHING:
            data = ""
        elif data == "":
            data = OVERHEAD
        return {LENGTH: msg_len,
                RESPOND: respond,
                END: end,
                DATA: data}
    except:
        return False


def receive_full_msg():
    msg_len, respond, end, data_left = receive_header()
    data = client_socket.recv(msg_len)
    msg_len_part = len(data)

    while msg_len_part < msg_len:
        resend_len = msg_len - msg_len_part
        request_resend(data_left=resend_len)
        _msg_len, _respond, _end, _data_left = receive_header()
        new_data = client_socket.recv(_msg_len)
        msg_len_part += len(new_data)
        data += new_data

    request_resend(0)
    return msg_len, respond, end, data


def receive_header():
    msg_header = client_socket.recv(HEADER_SIZE).decode(FORMAT)
    if not len(msg_header):
        return False

    msg_len = int(msg_header[:LENGTH_SIZE].strip())
    respond = int(msg_header[RESPOND_FLAG])
    end = int(msg_header[END_FLAG])
    data_left = int(msg_header[-DATA_LEFT_SIZE:].strip())

    return msg_len, respond, end, data_left


def request_resend(data_left):
    msg_header, msg = encode_msg("", 0, 1, data_left)
    client_socket.send(msg_header)
    # delay(msg_header)


def send_msg(msg, respond=0, end=1):
    """Sends msg to server socket.
    respond [0, 1]: Whether to require response from the server.
    end [0, 1]: Whether to insert newline after end of line."""
    msg_header, msg = encode_msg(msg, respond, end, -1)
    full_msg = msg_header + msg
    msg_len = len(msg)
    data_left = msg_len
    while data_left > 0:
        msg = full_msg[msg_len - data_left:]
        client_socket.send(msg)
        # delay(msg)
        _msg_len, _respond, _end, data_left = receive_header()

    return True


def encode_msg(msg, respond, end, data_left):
    if msg == "" and data_left < 0:
        msg = NOTHING
    msg = msg.encode(FORMAT)
    msg_header = f"{len(msg):<{LENGTH_SIZE}}{respond}{end}{data_left:<{DATA_LEFT_SIZE}}"
    return msg_header.encode(FORMAT), msg


# def delay(msg=None):
#     if msg is None:
#         msg = ""
#     t = max(0.1, len(msg) / 10_000)
#     time.sleep(t)


username = ""
while not username:
    username = input("Username: ")
send_msg(username, 0, 1)

while True:
    new_message = None
    while not new_message:
        try:
            new_message = receive_msg()
        except ConnectionResetError:
            print("Server closed")
            sys.exit()
    if new_message[DATA] == OVERHEAD:
        continue
    if new_message[DATA] == GAME_OVER:
        break
    print(new_message[DATA], end=new_message[END])
    if new_message[RESPOND]:
        tcflush(sys.stdin, TCIFLUSH)
        response = input(">")
        try:
            send_msg(response)
        except (ConnectionResetError, TypeError):
            print("Server closed")
            sys.exit()

try:
    send_msg(DISCONNECT)
except (ConnectionResetError, TypeError):
    pass
