description = """
## 生成斐波那契序列

设计一个函数`fibonacci_sequence(n)`，生成一个长度为`n`（`n`为非负整数）的斐波那契序列，并返回这个序列的列表。（4分）

提示：斐波那契数列（Fibonacci sequence）是一个非常经典的数学数列，其特点是每个数字是前两个数字的和，起始于0和1。
"""

title = "生成斐波那契序列 (4分)"
score = 4

knowledge = ["number", "list", "loop"]

code_template = """
def fibonacci_sequence(n):
    # 你的代码
    return ...
"""

code_entrypoint = "fibonacci_sequence"

validcases = [
    {"input": 5, "output": [0, 1, 1, 2, 3], "comment": "前5个斐波那契数"},
]

testcases = [
    *validcases,
    {"input": 0, "output": [], "comment": "长度为0的序列为空"},
    {"input": 1, "output": [0], "comment": "长度为1的序列开始于0"},
    {"input": 2, "output": [0, 1], "comment": "前2个斐波那契数"},
    {"input": 8, "output": [0, 1, 1, 2, 3, 5, 8, 13], "comment": "前8个斐波那契数"},
    {
        "input": 10,
        "output": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34],
        "comment": "前10个斐波那契数",
    },
]
answer = ""
