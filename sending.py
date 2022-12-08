import socket

__all__ = ["send", "recv"]

header_len = 64
fmt = "utf-8"


def send(sock: socket.socket, msg):
    sock.send(str(len(msg)).ljust(header_len).encode(fmt))
    sock.send(msg.encode(fmt))


def recv(sock: socket.socket):
    msg_len = int(sock.recv(header_len).decode(fmt))
    return sock.recv(msg_len).decode(fmt)
