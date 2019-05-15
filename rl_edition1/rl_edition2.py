import numpy as np
import pandas as pd
from socket import *
import threading
import os

ACTIONS = ['true', 'false']
STATE_LIST = ['0']


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
    def __init__(self, actions, reward_decay=0.9, learning_rate=0.01, e_greedy=0.9, alpha=0.1):
        self.actions = actions
        self.gamma = reward_decay
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

    def learn(self, s, a, r, is_terminated):
        # self.check_state_exist(s)
        if a is 'true':
            s_ = s + '1'
        else:
            s_ = s + '2'
        self.check_state_exist(s_)
        q_predict = self.q_table.loc[s, a]
        if is_terminated is True:
            q_target = r
        else:
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()
        # if q_target > 0:
        #     self.q_table = self.q_table.rename(index={s_: 'target'})
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



def by_py():
    data = conn.recv(1000)
    dataset = ""
    for i in str(data):
        if i != '\\':
            dataset += i
        else:
            break
    message = dataset[2:]
    return message


if __name__ == "__main__":
    print("Waitting...")
    RL = QLearningTable(ACTIONS)
    state = '0'
    first_connect = True
    if_arrive = False
    round = 0
    while if_arrive is False:
        thread2 = MyThread2()
        if first_connect:
            state = '0'
            Socket_TCP = socket()
            init_socket(Socket_TCP)

        data = by_py()
        # every time the program fork,there is a link request
        if data == 'link':
            if first_connect is False:
                state = next_state
            action = RL.choose_action(state)
            next_state = RL.env_update(state, action)
            conn.send(bytes(action, encoding='utf-8'))
            first_connect = False
            reward = 0
            RL.learn(state, action, reward, False)
        # the klee gets to the target,receive a reward
        else:
            round += 1
            reward = int(data)
            RL.learn(state, action, reward, True)
            conn.close()
            Socket_TCP.close()
            # print(RL.q_table)
            first_connect = True
            if reward > 0:
                if_arrive = True

    print("klee runs %s round" % round)
