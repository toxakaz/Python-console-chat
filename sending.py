import threading
import socket

__all__ = ["client", "send", "recv"]

header_len = 64
fmt = "utf-8"


class client:
    def __init__(self, sock):
        self.socket = sock
        self.lock = threading.Lock()


def send(client: client, msg):
    with client.lock:
        client.socket.send(str(len(msg)).ljust(header_len).encode(fmt))
        client.socket.send(msg.encode(fmt))


def recv(client: client):
    msg_len = int(client.socket.recv(header_len).decode(fmt))
    return client.socket.recv(msg_len).decode(fmt)
