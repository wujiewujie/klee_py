import os
import time

# path = "/home/wj/benchmarks/c/forester-heap"
# list_dir = os.listdir(path)
#
# # transfer the .c to .bc
# for i in list_dir:
#     command = "clang-6.0 -I ../../klee/klee_dom/include/ -c -emit-llvm"
#     if i.split(".")[-1] == "c":
#         print(i)
#         # print(command)
# run the .bc
# path = "/home/wj/benchmarks/bc"
# list = os.listdir(path)
# for i in list:
#     if i.split(".")[-1] == "bc":
#         # print(i)
#         command = "time python3  ~/PycharmProjects/klee_py/klee_py/rl_klee_dom.py "+i
# os.system(command)
import time

time1 = time.time()
i = 0
while True:
    i += 1
    if i == 100000000:
        break

time2 = time.time()
print(time2-time1)
