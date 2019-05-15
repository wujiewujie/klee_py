from socket import *
import numpy as np

ACTIONS = ['true', 'false']
EPSILON = 0.5


def init_socket(Socket_TCP):
    global conn, addr
    host = ""
    port = 9999
    addr = (host, port)
    Socket_TCP.bind(addr)
    Socket_TCP.listen(10)
    conn, addr = Socket_TCP.accept()
    print('connect success')


def choose_action():
    action_name = np.random.choice(ACTIONS)
    return action_name


if __name__ == "__main__":
    print("Waiting...")
    Socket_TCP = socket()
    init_socket(Socket_TCP)
    # receive the link request from klee
    while True:
        data = conn.recv(1000)
        dataset = ""
        for i in str(data):
            if i != '\\':
                dataset += i
            else:
                break
        message = dataset[2:]
        if message == 'link':
            A = choose_action()
            conn.send(bytes(A, encoding='utf-8'))

        # disconnect
        elif message == 'break':
            break
    conn.close()
    Socket_TCP.close()
