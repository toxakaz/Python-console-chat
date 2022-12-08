import threading
import socket

from sending import send, recv
from sending import client as new_client

nick_len = 16
standard_address = "127.0.0.1 : 5050"

clients_lock = threading.Lock()
clients = dict()

output_lock = threading.Lock()


def print_info(msg, client=None):

    if client is None:
        with output_lock:
            print(msg)
    else:
        with output_lock:
            print(f'"{client.address}" {client.nick}'.ljust(nick_len + 20) + f": {msg}")


def send_all(msg, client=None):

    if client is not None:
        msg = f"{client.nick}: {msg}"
    with clients_lock:
        receivers = list(clients.values())
    for client in receivers:
        send(client, msg)


def leave_chat_routine(client):

    send(client, "You left the chat...")

    with clients_lock:
        del clients[client.nick]

    send_all(f"{client.nick.strip()} left the chat")

    client.socket.close()

    print_info("left", client)
    return 0


def disconnected_routine(client):

    with clients_lock:
        del clients[client.nick]

    send_all(f"{client.nick.strip()} disconnected")

    client.socket.close()

    print_info("disconnected", client)

    return 1


def handle(client):

    while True:
        try:
            msg = recv(client)

            if msg.strip() == "!exit":
                return leave_chat_routine(client)

            send_all(msg, client)

        except:
            return disconnected_routine(client)


def join_routine(client):

    nick = None
    try:
        send(client, f"You successfully connected to chat server!")
        while True:
            send(client, f"Enter your nickname with len less then {nick_len}")
            nick = recv(client).strip()

            if len(nick) > nick_len:
                send(client, "Too long nickname")
                continue

            if not nick:
                send(client, "Nickname mustn't be empty")
                continue

            nick = nick.ljust(nick_len)

            with clients_lock:
                if nick not in clients:
                    clients[nick] = client
                    break

            send(client, "This nickname already in use")

        client.nick = nick

        print_info("connected", client)

        with clients_lock:
            send(client, "Welcome! Type !exit to leave.")
        send_all(f"{nick.strip()} joined the chat.")
    except Exception as inst:
        if nick is not None:
            with clients_lock:
                del clients[client.nick]
            print_info("disconnected: " + inst, client)
        return 1

    return handle(client)


def listener(server):

    while True:
        socket, address = server.accept()
        client = new_client(socket)
        client.address = address
        thread = threading.Thread(target=join_routine, args=(client,))
        thread.start()


def start():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print_info("Enter server address as ip:port")
    print_info(f'Leave field empty for standard value: "{standard_address}"')
    while True:
        try:
            user_input = input("Server address: ").strip() or standard_address
            user_input = "".join(user_input.split())
            address = user_input.split(":")

            if len(address) != 2:
                raise Exception("Address should be written as ip:port")

            try:
                address[1] = int(address[1])
            except ValueError:
                raise Exception("Port should be an integer value")

            server.bind(tuple(address))
            server.listen()
            break
        except Exception as inst:
            print_info(inst)

    print_info(f"Server started at {user_input}")
    return listener(server)


start()
