description = """
## 最大公约数
编写一个函数 `gcd(a, b)`，它接受两个正整数作为参数，并返回它们的最大公约数。（4 分）

提示：约数是指可以整除给定整数的整数。例如，12的约数包括1, 2, 3, 4, 6, 12。最大公约数是指两个或多个整数共有约数中最大的一个。
"""

title = "最大公约数 (4分)"
score = 4

code_template = """
def gcd(a, b):
    # 你的代码
    return ...
"""

knowledge = ["number", "loop", "condition", "bool"]

code_entrypoint = "gcd"

validcases = [
    {
        "input": [8, 12],
        "output": 4,
        "comment": "最大公约数 of 8 and 12 is 4",
    }
]

testcases = [
    *validcases,
    {
        "input": [17, 13],
        "output": 1,
        "comment": "最大公约数 of 17 and 13 is 1",
    },
    {
        "input": [21, 14],
        "output": 7,
        "comment": "最大公约数 of 21 and 14 is 7",
    },
    {
        "input": [100, 10],
        "output": 10,
        "comment": "最大公约数 of 100 and 10 is 10",
    },
    {
        "input": [35, 10],
        "output": 5,
        "comment": "最大公约数 of 35 and 10 is 5",
    },
    {
        "input": [31, 2],
        "output": 1,
        "comment": "最大公约数 of 31 and 2 is 1",
    },
    {
        "input": [1, 1],
        "output": 1,
        "comment": "最大公约数 of 1 and 1 is 1",
    },
    {
        "input": [99, 33],
        "output": 33,
        "comment": "最大公约数 of 99 and 33 is 33",
    },
    {
        "input": [150, 100],
        "output": 50,
        "comment": "最大公约数 of 150 and 100 is 50",
    },
    {
        "input": [81, 27],
        "output": 27,
        "comment": "最大公约数 of 81 and 27 is 27",
    },
]

answer = """
```Python
# 欧几里得算法
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# 按照定义
def gcd(a, b):
    if a < b:
        min_num = a
    else:
        min_num = b

    for i in range(min_num, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
```
"""
