import socket
import argparse
from constants import HEADER_SIZE, DATA_LEFT_SIZE, PORT, FORMAT, DISCONNECT, NOTHING, OVERHEAD, GAME_OVER, LENGTH,\
    RESPOND, END, DATA

from sys import platform, stdin, exit
if platform in ["cygwin", "win32"]:
    import msvcrt
    import colorama
    colorama.init()
elif platform in ["linux", "darwin"]:
    from termios import tcflush, TCIFLUSH

LENGTH_SIZE = HEADER_SIZE - (DATA_LEFT_SIZE + 2)
RESPOND_FLAG = LENGTH_SIZE
END_FLAG = LENGTH_SIZE + 1
IP = socket.gethostname()


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
        request_resend(resend_len)
        _msg_len, _, _, _ = receive_header()
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
    msg_header = encode_header(0, 0, 1, data_left)
    client_socket.send(msg_header)


def send_msg(msg, respond=0, end=1):
    """Send msg to client.
    msg (str): message payload to send to client.
    respond (int) [0, 1]: Whether to require response from clients.
    end (int) [0, 1]: Whether to insert newline after end of line."""

    full_msg = encode_msg_body(msg)
    full_msg_len = len(full_msg)
    data_left = full_msg_len

    while data_left > 0:
        msg_header = encode_header(data_left, respond, end, -1)
        msg = msg_header + full_msg[full_msg_len - data_left:]
        client_socket.send(msg)
        _, _, _, data_left = receive_header()

    return True


def encode_header(msg_len, respond, end, data_left):
    msg_header = f"{msg_len:<{LENGTH_SIZE}}{respond}{end}{data_left:<{DATA_LEFT_SIZE}}"
    return msg_header.encode(FORMAT)


def encode_msg_body(msg):
    if msg == "":
        msg = NOTHING
    msg = msg.encode(FORMAT)
    return msg


parser = argparse.ArgumentParser(description="Connect to Dominion game host.")
parser.add_argument("host", type=str, nargs="?", help="Host IP address to connect with.")
args = parser.parse_args()
if args.host is not None:
    IP = args.host

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((IP, PORT))

username = ""
while not username:
    username = input("Username: ")
send_msg(username)

while True:
    new_message = None
    while not new_message:
        try:
            new_message = receive_msg()
        except ConnectionResetError:
            print("Server closed")
            exit()
    if new_message[DATA] == OVERHEAD:
        continue
    if new_message[DATA] == GAME_OVER:
        break
    print(new_message[DATA], end=new_message[END])
    if new_message[RESPOND]:
        if platform in ["linux", "darwin"]:
            tcflush(stdin, TCIFLUSH)
        elif platform in ["cygwin", "win32"]:
            while msvcrt.kbhit():
                msvcrt.getch()
        response = input(">")
        try:
            send_msg(response)
        except (ConnectionResetError, TypeError):
            print("Server closed")
            exit()

try:
    send_msg(DISCONNECT)
except (ConnectionResetError, TypeError):
    pass

if platform in ["cygwin", "win32"]:
    input("Press enter to close")
