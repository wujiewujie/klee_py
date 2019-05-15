import numpy as np
import pandas as pd
from socket import *
import threading
import os

ACTIONS = ['true', 'false']
STATE_LIST = ['0']
ACTION_STR = ''


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
            "/home/lab301/klee_origin/klee/cmake-build-debug/bin/klee -search=jie "
            "/home/lab301/klee_origin/klee/examples/regexp/Regexp.bc")


class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, e_greedy=0.7, alpha=0.1):
        self.actions = actions
        self.lr = learning_rate
        self.epsilon = e_greedy
        self.alpha = alpha
        self.q_table = pd.DataFrame(np.zeros((1, len(ACTIONS))), columns=self.actions, dtype=np.float64, index=['0'])

    def choose_action(self, state):
        self.check_state_exist(state)
        state_actions = self.q_table.loc[state, :]
        if np.random.uniform() < self.epsilon:
            action_name = np.random.choice(state_actions[state_actions == np.max(state_actions)].index)
        else:
            action_name = np.random.choice(self.actions)
        return action_name

    def check_state_exist(self, state):
        if state not in STATE_LIST:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.actions,
                    name=state
                )
            )
            STATE_LIST.append(state)

    def env_update(self, s, a):
        if a == 'true':
            s += '1'
        else:
            s += '2'
        return s

    def learn(self, s, a, r):
        # self.check_state_exist(s)
        if a is 'true':
            s_ = s + '1'
        else:
            s_ = s + '2'
        self.check_state_exist(s_)
        q_predict = self.q_table.loc[s, a]
        q_target = r + self.q_table.loc[s_, :].max()

        self.q_table.loc[s, a] += self.alpha * (q_target - q_predict)


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


def check_if_in_qtable(ACTION_STR):
    str = '0' + ACTION_STR
    if str in STATE_LIST:
        return True
    return False


if __name__ == "__main__":
    RL = QLearningTable(ACTIONS)
    state = '0'
    first_connect = True
    if_arrive = False
    round = 0
    dis_old = 0
    dis_new = 0
    while if_arrive is False:
        thread2 = MyThread2()
        if first_connect:
            state = '0'
            Socket_TCP = socket()
            init_socket(Socket_TCP)

        data = by_klee()
        if data == 'link':
            if first_connect is False:
                state = next_state
            action = RL.choose_action(state)
            if action == 'true':
                ACTION_STR += '1'
            else:
                ACTION_STR += '2'
            # util the q_table don't exist the state,we convey it to klee
            while check_if_in_qtable(ACTION_STR):
                state = RL.env_update(state, action)
                action = RL.choose_action(state)
                if action == 'true':
                    ACTION_STR += '1'
                else:
                    ACTION_STR += '2'
            next_state = RL.env_update(state, action)
            conn.send(bytes(ACTION_STR, encoding='utf-8'))
            first_connect = False

        elif data == 'fail' or data == "reach":
            print(RL.q_table)
            round += 1
            conn.close()
            Socket_TCP.close()
            if data == "fail":
                first_connect = True
                ACTION_STR = ""
            else:
                if_arrive = True
        else:
            dis = int(data)
            if dis_old is 0:
                r = dis
            elif dis is 0:
                r = 0
            else:
                r = 1 / dis_new - 1 / dis_old
            RL.learn(state, action, r)

    print("klee runs %s round" % round)
