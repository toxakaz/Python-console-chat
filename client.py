import socket
import threading
from sending import *

standard_address = "127.0.0.1 : 5050"


def receive_routine(client):
    while True:
        try:
            message = recv(client)
            print(message)
        except:
            print("Error. Client shutting down...")
            client.close()
            break


def sending_routine(client):
    while True:
        msg = input()
        send(client, msg)


def start():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

            client.connect(tuple(address))
            break
        except Exception as inst:
            print(inst)

    receive_thread = threading.Thread(target=receive_routine, args=(client,))
    receive_thread.start()

    write_thread = threading.Thread(target=sending_routine, args=(client,))
    write_thread.start()


start()
