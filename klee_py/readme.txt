将修改后的klee重新编译之后，在rl_klee_dis.py的34-37行(MyThread2的run函数)，修改路径为编译后的klee位置，后面搜索的参数是-search=jie,最后是.bc文件的绝对路径。这样就可以直接运行了
