import numpy as np
import pandas as pd
from socket import *

ACTIONS = ['true', 'false']
EPSILON = 0.9
ALPHA = 0.1
GAMMA = 0.9
state_dis = dict()
list_node = []


class Node():
    def __init__(self, item):
        self.item = item
        self.true_next = None
        self.false_next = None

    def __str__(self):
        return self.item


class CFG_List():
    def __init__(self):
        self.head = None
        self.curNode = None

    def is_empty(self):
        return self.head is None

    def add(self, node, isBack=False):
        if self.is_empty():
            self.head = node
            self.curNode = node
        else:
            if isBack is False:
                self.curNode.true_next = node
                self.curNode = node
            else:
                self.curNode.false_next = node

    def print(self):
        if self.is_empty():
            print("")
        else:
            cur_node = self.head
            print(cur_node)
            while cur_node.true_next is not None:
                cur_node = cur_node.true_next
                print(cur_node, end='')
                if cur_node.false_next is not None:
                    print("(false)", end='')
                    print(cur_node.false_next)
                else:
                    print()


def init_socket(Socket_TCP):
    global conn, addr
    host = ""  # ip，服务器空ip代表本地
    port = 9999  # 端口号
    addr = (host, port)
    Socket_TCP.bind(addr)  # 服务器用bind绑定本地，也算是服务器的标识
    print("Waitting...")
    Socket_TCP.listen(10)
    conn, addr = Socket_TCP.accept()
    print('连接成功')


# 自己手动拆分程序结构
def init():
    line1 = "count = 0,i=0"
    line2 = "while i < 4"
    line3 = "input j"
    line4 = "if j > 0"
    line5 = "count += 1,i += 1"
    line6 = "if i == 3:"
    line7 = "print(hhh)"  # 目标代码
    line8 = "print(count)"
    node1 = Node(line1)
    node2 = Node(line2)
    node2.false_next = True
    node3 = Node(line3)
    node4 = Node(line4)
    node4.false_next = True
    node5 = Node(line5)
    node6 = Node(line6)
    node6.false_next = True
    node7 = Node(line7)
    node8 = Node(line8)
    index = 6
    list_node_append = [node1, node2, node3, node4, node5, node6, node7, node8]
    for i in list_node_append:
        list_node.append(i)
    for i in list_node:
        state_dis[i] = index
        index -= 1
    state_dis[node8] = np.nan


# 自己手动建cfg的部分
def CFG_Generator(list):
    cfg_list = CFG_List()
    cfg_list.add(list_node[0])
    cfg_list.add(list_node[1])
    cfg_list.add(list_node[7], isBack=True)
    cfg_list.add(list_node[2])
    cfg_list.add(list_node[3])
    cfg_list.add(list_node[7], isBack=True)
    cfg_list.add(list_node[4])
    cfg_list.add(list_node[5])
    cfg_list.add(list_node[1], isBack=True)
    cfg_list.add(list_node[6])
    cfg_list.add(list_node[1])
    return cfg_list


def build_q_table(list_node, actions):
    table = pd.DataFrame(
        np.zeros((len(list_node), len(actions))),
        columns=ACTIONS,
        index=np.arange(len(list_node))
    )
    return table


# false_next不是None的时候才选择，否则就一直走true
def choose_action(state, q_table):
    state_index = list_node.index(state)
    state_actions = q_table.iloc[state_index, :]
    if state.false_next is None:
        action_name = 'true'
    else:
        if (np.random.uniform() > EPSILON) or ((state_actions == 0).all()):
            action_name = np.random.choice(ACTIONS)
        else:  # act greedy
            action_name = state_actions.idxmax()
    return action_name


# 判断哪里走错了,需要重新开始
def out_feedback(S, A):
    isDone = False
    global R
    if A == 'true':
        if S == list_node[5]:  # terminate
            S_ = 'terminal'
            isDone = True

        else:
            S_ = list_node[list_node.index(S) + 1]
    else:
        S_ = S.false_next
        if S_ == list_node[7]:
            S_ = 'false_terminal'

    return S_, isDone


def update_env(S):
    print(S.item)


if __name__ == "__main__":
    ifStart = False
    try_again = False
    # 两个手动建模的过程
    init()
    cfg = CFG_Generator(list)
    q_table = build_q_table(list_node, ACTIONS)
    print(q_table)
    episode = 1
    while True:
        S = list_node[0]
        is_terminated = False
        print("this is the " + str(episode) + "round")
        print("-----------------------------------")
        while not is_terminated:
            update_env(S)
            A = choose_action(S, q_table)
            S_, isDone = out_feedback(S, A)  # take action & get next state and reward
            # 第一次的时候连接，之后就不用了
            if ifStart is False:
                Socket_TCP = socket()
                init_socket(Socket_TCP)
                ifStart = True
            # 此处需要把next_state传给c++,先知道next_state,c++才能给奖赏
            if isinstance(S_, str):
                conn.send(bytes(S_, encoding='utf-8'))
            else:
                conn.send(bytes(S_.item, encoding='utf-8'))
            # 此处需要c++传来的reward
            data = conn.recv(1000)  # 1000是参数缓冲区大小
            dataset = ""
            for i in str(data):
                if i != '\\':
                    dataset += i
                else:
                    break
            # 收到的信息是b'xxx格式，需要把前两个字符去掉
            R = int(dataset[2:])
            # 更新q-table
            q_predict = q_table.loc[list_node.index(S), A]
            if not isinstance(S_, str):
                q_target = R + GAMMA * q_table.iloc[list_node.index(S_), :].max()  # next state is not terminal
            elif S_ == 'false_terminal':
                S_ = list_node[0]
                q_target = R  # next state is terminal
                is_terminated = True  # terminate this episode

            else:
                # 成功了
                q_target = R  # next state is terminal
                is_terminated = True  # terminate this episode

            q_table.loc[list_node.index(S), A] += ALPHA * (q_target - q_predict)  # update
            S = S_  # move to next state

        if isDone:
            break
        else:
            episode += 1
            try_again = True
            conn.close()
            Socket_TCP.close()
            ifStart = False
    print(q_table)
    conn.close()  # 关闭客户端的连接
    Socket_TCP.close()  # 关闭套接字
