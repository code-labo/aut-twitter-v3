import random

# 3つの関数を定義する（例）
def function1(arg):
    print("Function 1 executed with argument:", arg)

def function2(arg1, arg2):
    print("Function 2 executed with arguments:", arg1, "and", arg2)

def function3():
    print("Function 3 executed")

# 各関数に渡す引数を定義する（例）
args1 = ("argument1",)
args2 = (22222, "argument2_2")

# 関数と引数のリストを作成する
# function_args_pairs = [(function1, args1,1), (function2, args2,2), (function3, None,3)]
function_args_pairs=[]
function_args_pairs.append((function1, args1,1))
function_args_pairs.append((function2, args2,2))
function_args_pairs.append((function3, None,3))

# リストをシャッフルする
random.shuffle(function_args_pairs)
print(function_args_pairs)

# シャッフルされた順番で関数を実行する
for function, args,idx in function_args_pairs:
    print("[",idx,"]")
    if args is not None:
        function(*args)
    else:
        function()
