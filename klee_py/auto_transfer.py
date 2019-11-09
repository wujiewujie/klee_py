import os
import re

path = "/mnt/hd0/klee_benchmarks/benchmarks/c/seq-mthreaded"
path_temp = "/home/wj/PycharmProjects/klee_py/klee_py/"
key_char = "__VERIFIER_nondet_char"
key_uchar = "__VERIFIER_nondet_uchar"
key_int = "__VERIFIER_nondet_int"
key_uint = "__VERIFIER_nondet_uint"
key_bool = "__VERIFIER_nondet_bool"
key_assuem = "__VERIFIER_assume"
key_size = "typedef unsigned int size_t"
key_wchar = "wchar_t;"
key_main = "int main"
key_error = "__VERIFIER_error();"
key_long = "__VERIFIER_nondet_long"
key_pointer = "__VERIFIER_nondet_pointer"
append_connect = "klee_connect();"
append_stop = "klee_stop();"
append_main = "#include<klee/klee.h>\n"
append_uint = """
__attribute__((always_inline)) unsigned int __VERIFIER_nondet_uint(){
    unsigned int __sym___VERIFIER_nondet_uint;
    klee_make_symbolic(&__sym___VERIFIER_nondet_uint, sizeof(__sym___VERIFIER_nondet_uint), "__sym___VERIFIER_nondet_uint");
    return __sym___VERIFIER_nondet_uint;
}\n"""

append_char = """
__attribute__((always_inline)) char __VERIFIER_nondet_char(){
    char __sym___VERIFIER_nondet_char;
    klee_make_symbolic(&__sym___VERIFIER_nondet_char, sizeof(__sym___VERIFIER_nondet_char), "__sym___VERIFIER_nondet_char");
    return __sym___VERIFIER_nondet_char;
}\n"""

append_bool = """
__attribute__((always_inline)) _Bool __VERIFIER_nondet_bool(){
    _Bool __sym___VERIFIER_nondet_bool;
    klee_make_symbolic(&__sym___VERIFIER_nondet_bool, sizeof(__sym___VERIFIER_nondet_bool), "__sym___VERIFIER_nondet_bool");
    return __sym___VERIFIER_nondet_bool;
}\n"""
append_int = """
__attribute__((always_inline)) int __VERIFIER_nondet_int(){
    int __sym___VERIFIER_nondet_int;
    klee_make_symbolic(&__sym___VERIFIER_nondet_int, sizeof(__sym___VERIFIER_nondet_int), "__sym___VERIFIER_nondet_int");
    return __sym___VERIFIER_nondet_int;
}\n"""
append_long = """
__attribute__((always_inline)) long __VERIFIER_nondet_long(){
    long __sym___VERIFIER_nondet_long;
    klee_make_symbolic(&__sym___VERIFIER_nondet_long, sizeof(__sym___VERIFIER_nondet_long), "__sym___VERIFIER_nondet_long");
    return __sym___VERIFIER_nondet_long;
}\n"""
append_pointer = """
__attribute__((always_inline)) void * __VERIFIER_nondet_pointer(){
    void * __sym___VERIFIER_nondet_pointer;
    klee_make_symbolic(&__sym___VERIFIER_nondet_pointer, sizeof(__sym___VERIFIER_nondet_pointer), "__sym___VERIFIER_nondet_pointer");
    return __sym___VERIFIER_nondet_pointer;
}\n"""
append_uchar = """
__attribute__((always_inline)) unsigned char __VERIFIER_nondet_uchar(){
    unsigned char __sym___VERIFIER_nondet_uchar;
    klee_make_symbolic(&__sym___VERIFIER_nondet_uchar, sizeof(__sym___VERIFIER_nondet_uchar), "__sym___VERIFIER_nondet_uchar");
    return __sym___VERIFIER_nondet_uchar;
}\n"""
append_assume = """
__attribute__((always_inline)) void __VERIFIER_assume(int arg ){
    klee_assume(arg);
}
"""

rgl_exp1 = r'''
            (\s*)
            ((VOID)|(void)|(char)|(short)|(int)|(float)|(long)|(double)) # 识别函数返回值类型
            (\s*(\*)?\s*)                                                # 识别返回值是否为指针类型以及中间是否包含空格
            ((?!main)\w+)                                                        # 识别函数名
            ((\s*)(\()(\n)?)                                             # 函数开始小括号
            ((\s*)?(const|unsigned)?(\s*)?                                        # 参数前是否有const
            (void)|
            ((char)|(short)|(int)|(float)|(long)|(double)|(_Bool))        # 参数类型
            (\s*)(\*)?(\s*)?(restrict)?(\s*)?(\w+)(\s*)?(\,)?(\n)?(.*)?)*# 最后的*表示有多个参数
            ((\s*)(\))(\n)?)                                             # 函数结束小括号
            '''
rgl_exp2 = r'''
            (\s*)
            ((VOID)|(void)|(char)|(short)|(int)|(float)|(long)|(double)) # 识别函数返回值类型
            (\s*(\*)?\s*)                                                # 识别返回值是否为指针类型以及中间是否包含空格
            (main)                                                        # 识别函数名
            ((\s*)(\()(\n)?)                                             # 函数开始小括号
            ((\s*)?(const)?(\s*)?                                        # 参数前是否有const
            ((void)|(char)|(short)|(int)|(float)|(long)|(double))        # 参数类型
            (\s*)(\*)?(\s*)?(restrict)?(\s*)?(\w+)(\s*)?(\,)?(\n)?(.*)?)*# 最后的*表示有多个参数
            ((\s*)(\))(\n)?)
'''
if __name__ == "__main__":
    list_dir = os.listdir(path)
    for i in list_dir:
        flag_int = True
        flag_uint = True
        flag_char = True
        flag_uchar = True
        flag_bool = True
        flag_assume = True
        flag_long = True
        flag_point = True
        if i.split(".")[-1] == "c":
            print(i)
            file = open(path + "//" + i, "r")
            output = []
            output.append(append_main)
            for line in file.readlines():
                if key_int in line and flag_int:
                    flag_int = False
                    line = line + "\n" + append_int
                if key_uint in line and flag_uint:
                    flag_uint = False
                    line = line + "\n" + append_uint
                if key_char in line and flag_char:
                    flag_char = False
                    line = line + "\n" + append_char
                if key_uchar in line and flag_uchar:
                    flag_uchar = False
                    line = line + "\n" + append_uchar
                if key_bool in line and flag_bool:
                    flag_bool = False
                    line = line + "\n" + append_bool
                if key_long in line and flag_long:
                    flag_long = False
                    line = line + "\n" + append_long
                if key_pointer in line and flag_point:
                    flag_point = False
                    line = line + "\n" + append_pointer
                matchObj = re.match(rgl_exp1, line, re.X)
                if matchObj:
                    line = "__attribute__((always_inline)) " + line
                if key_assuem in line and flag_assume:
                    flag_assume = False
                    line = line + "\n" + append_assume
                output.append(line)

            # append klee_connect()
            for index in range(len(output)):
                if key_main in output[index]:
                    if "{" in output[index]:
                        output[index] = output[index] + "\n" + append_connect + "\n"
                    else:
                        output[index + 1] = output[index + 1] + "\n" + append_connect + "\n"
                # append klee_stop()
                if key_error in output[index]:
                    output[index] = output[index].replace(key_error, append_stop)
                    print("----", output[index])
                if key_size in output[index]:
                    output[index] = output[index].replace('size_t', 'size_t1')
                if key_wchar in output[index]:
                    output[index] = output[index].replace('wchar_t','wchar_t1')
            file = open(path + "//" + i, "w")
            file.writelines(output)
            file.close()

# if __name__ == "__main__":
#     code = """
#  int fun()
#     """
#     pat1 = re.compile(rgl_exp1, re.X)
#     ret = pat1.match(code)
#     if None == ret:
#         print('不包含C函数定义!')
#     else:
#         print('包含C函数定义!')
