import os
import re

path = "/home/wj/benchmarks/c/forester-heap"
append1 = "#include<klee/klee.h>\n"

rule = r'.*(void|char|short|int|long|float|double) (?!main).*[)][^;]'

list_dir = os.listdir(path)
for i in list_dir:
    if i.split(".")[-1] == "c":
        print(i)
        file = open(path + "//" + i, "r")

        content = file.read()

        content = append1 + content[:]

        file = open(path + "//" + i, "w")
        file.write(content)
        file.close()

        file = open(path + "//" + i, "r")
        output = []
        for line in file.readlines():
            matchObj = re.match(rule, line, re.I)
            if matchObj:
                line = "__attribute__((always_inline)) " + line + '\n'
            output.append(line)

        file = open(path + "//" + i, "w")
        file.writelines(output)
        file.close()
