import threading
import socket
from sending import *

nick_len = 16
standard_address = "127.0.0.1 : 5050"

clients_lock = threading.Lock()
clients = set()
nicknames = set()


def send_all(msg):
    with clients_lock:
        for client in clients:
            send(client, msg)


def leave_chat_routine(client, address, nick):

    send(client, "You left the chat...")

    with clients_lock:
        clients.remove(client)
        nicknames.remove(nick)

    send_all(f"{nick.strip()} left the chat")

    client.close()

    print(f'"{address}" {nick}: left')
    return 0


def disconnected_routine(client, address, nick):

    with clients_lock:
        clients.remove(client)
        nicknames.remove(nick)

    send_all(f"{nick.strip()} disconnected")

    client.close()

    print(f'"{address}" {nick}: disconnected')

    return 1


def handle(client, address, nick):

    while True:
        try:
            msg = recv(client)

            if msg.strip() == "!exit":
                return leave_chat_routine(client, address, nick)

            send_all(f"{nick}: {msg}")

        except:
            return disconnected_routine(client, address, nick)


def join_routine(client, address):

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
                if nick not in nicknames:
                    clients.add(client)
                    nicknames.add(nick)
                    break

            send(client, "This nickname already in use")

        print(f'"{address}" {nick}: connected')

        with clients_lock:
            send(client, "Welcome! Type !exit to leave.")
        send_all(f"{nick.strip()} joined the chat.")
    except:
        with clients_lock:
            clients.remove(client)
            nicknames.remove(nick)
        print(f'"{address}" {nick}: left')

    return handle(client, address, nick)


def listener(server):

    while True:
        thread = threading.Thread(target=join_routine, args=server.accept())
        thread.start()


def start():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Enter server address as ip:port")
    print(f'Leave field empty for standard value: "{standard_address}"')
    while True:
        try:
            user_input = "".join(input("Server address: ")) or standard_address
            address = "".join(user_input.split()).split(":")

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
            print(inst)

    print(f"Server started at {user_input}")
    return listener(server)


start()
