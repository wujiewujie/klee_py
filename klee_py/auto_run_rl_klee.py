import os
import time

path = "/mnt/hd0/klee_benchmarks/benchmarks/bc/eca-rers2012"
list_dir = os.listdir(path)

for i in list_dir:
    if i.split(".")[-1] == "bc":
        print(i, flush=True)
        command = "timeout 200 time python3 ~/PycharmProjects/klee_py/klee_py/rl_klee_dom.py " + i
        os.system(command)
        # print(command)
        print("-----------------------------------", flush=True)
        time.sleep(10)
