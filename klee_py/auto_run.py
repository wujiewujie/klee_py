import os
import time
import subprocess

# path = "/mnt/hd0/klee_benchmarks/benchmarks/c/ssh"
# list_dir = os.listdir(path)

# transfer the .c to .bc
# for i in list_dir:
#     command = "clang-6.0 -I ~/klee/klee_dom/include/ -c -emit-llvm /mnt/hd0/klee_benchmarks/benchmarks/c/ssh/"
#     if i.split(".")[-1] == "c":
#         # print(i)
#         # print(command)
#         command = command + i
#         # print(command)
#         os.system(command)
# run the .bc
path = "/mnt/hd0/klee_benchmarks/benchmarks/bc/ssh"
list = os.listdir(path)
for i in list:
    if i.split(".")[-1] == "bc":
        print(i, flush=True)
        # command = "timeout 100 time ~/klee/klee/cmake-build-debug/bin/klee " + i
        # print(command)
        # os.system(command)
        # print("---------", flush=True)
