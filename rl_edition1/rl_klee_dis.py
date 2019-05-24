import numpy as np
import pandas as pd
from socket import *
import threading
import os

ACTIONS = ['true', 'false']
STATE_LIST = ['0']
ACTION_STR = ''
CANDIDATE_LIST = {''}
STATE = '0'
ACTION = ''
NEXT_STATE = '0'


class MyThread1(threading.Thread):
    def __init__(self, Socket_TCP):
        threading.Thread.__init__(self)
        self.Socket_TCP = Socket_TCP

    def run(self):
        conn, addr = Socket_TCP.accept()
        self.conn = conn
        self.addr = addr

    def get_result(self):
        return self.conn, self.addr


class MyThread2(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        os.system(
            "/home/lab301/klee/klee/cmake-build-debug/bin/klee -search=jie "
            "/home/lab301/klee_benchmarks/systemc/bist_cell.cil.klee.bc")

class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, e_greedy=0.7, alpha=0.1):
        self.actions = actions
        self.lr = learning_rate
        self.epsilon = e_greedy
        self.alpha = alpha
        self.q_table = pd.DataFrame(np.zeros((1, len(ACTIONS))), columns=self.actions, dtype=np.float64, index=['0'])

    def choose_action(self):
        self.check_state_exist(STATE)
        state_actions = self.q_table.loc[STATE, :]
        if np.random.uniform() < self.epsilon:
            action_name = np.random.choice(state_actions[state_actions == np.max(state_actions)].index)
        else:
            action_name = np.random.choice(self.actions)
        return action_name

    def check_state_exist(self, STATE):
        if STATE not in STATE_LIST:
            # append new STATE to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.actions,
                    name=STATE
                )
            )
            STATE_LIST.append(STATE)

    def env_update(self):
        global ACTION_STR, NEXT_STATE, STATE
        if ACTION == 'true':
            ACTION_STR += '1'
            NEXT_STATE += '1'
        else:
            ACTION_STR += '2'
            NEXT_STATE += '2'

    def learn(self, r):
        global STATE, ACTION, NEXT_STATE
        q_predict = self.q_table.loc[STATE, ACTION]
        q_target = r + self.q_table.loc[NEXT_STATE, :].max()

        self.q_table.loc[STATE, ACTION] += self.alpha * (q_target - q_predict)


def init_socket(Socket_TCP):
    global conn, addr
    host = ""
    port = 45202
    addr = (host, port)
    Socket_TCP.bind(addr)
    Socket_TCP.listen(10)
    thread1 = MyThread1(Socket_TCP)
    thread1.start()
    thread2.start()
    thread1.join()
    conn, addr = thread1.get_result()
    # conn, addr = Socket_TCP.accept()


def by_klee():
    data = conn.recv(1000)
    dataset = ""
    for i in str(data):
        if i != '\\':
            dataset += i
        else:
            break
    message = dataset[2:]
    return message


def check_if_valid():
    global ACTION_STR, STATE_LIST, CANDIDATE_LIST
    str = '0' + ACTION_STR
    if str in STATE_LIST:
        return True
    else:
        if str[1:] in CANDIDATE_LIST:
            return False
        else:
            init()
            return True


def if_in_qtable():
    global ACTION_STR, STATE_LIST
    str = '0' + ACTION_STR
    if str in STATE_LIST:
        return True
    else:
        return False


def init():
    global ACTION_STR, STATE, NEXT_STATE
    ACTION_STR = ""
    STATE = '0'
    NEXT_STATE = '0'


if __name__ == "__main__":
    RL = QLearningTable(ACTIONS)
    if_arrive = False
    dis_old = 0
    dis_new = 0
    thread2 = MyThread2()
    Socket_TCP = socket()
    init_socket(Socket_TCP)
    while if_arrive is False:

        data = by_klee()
        if data == 'link':

            ACTION = RL.choose_action()
            RL.env_update()
            while if_in_qtable():
                ACTION = RL.choose_action()
                RL.env_update()
            conn.send(bytes(ACTION_STR, encoding='utf-8'))

        elif data == 'fail':
            init()
            ACTION = RL.choose_action()
            RL.env_update()
            while check_if_valid():
                ACTION = RL.choose_action()
                RL.env_update()
            conn.send(bytes(ACTION_STR, encoding='utf-8'))

        elif data == "reach":
            print(RL.q_table)
            conn.close()
            Socket_TCP.close()
            if_arrive = True
        else:
            dis = int(data)
            if dis_old is 0:
                r = dis
            elif dis is 0:
                r = 0
            else:
                r = dis_old-dis_new
            RL.check_state_exist(NEXT_STATE)
            CANDIDATE_LIST.add(ACTION_STR[:-1] + '1')
            CANDIDATE_LIST.add(ACTION_STR[:-1] + '2')
            RL.learn(r)
            STATE = NEXT_STATE
            # print(RL.q_table)
