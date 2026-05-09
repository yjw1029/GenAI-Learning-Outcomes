description = """
## 找出所有素数
编写一个函数`find_primes(n)`，它接受一个整数`n`作为参数，并返回一个列表，该列表包含从2到`n`（包含）之间的所有素数。（5 分）
"""

title = "找出所有素数（5 分）"
score = 5

knowledge = ["number", "loop", "condition"]

code_template = """
def find_primes(n):
    # 你的代码
    return ...
"""

code_entrypoint = "find_primes"

validcases = [
    {"input": [10], "output": [2, 3, 5, 7], "comment": "2到10之间的素数"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [1], "output": [], "comment": "1没有素数"},
    {"input": [2], "output": [2], "comment": "2是素数"},
    {"input": [5], "output": [2, 3, 5], "comment": "2到5之间的素数"},
    {"input": [15], "output": [2, 3, 5, 7, 11, 13], "comment": "2到15之间的素数"},
    {
        "input": [20],
        "output": [2, 3, 5, 7, 11, 13, 17, 19],
        "comment": "2到20之间的素数",
    },
]

answer = """
```Python
def find_primes(n):
    primes = []
    for num in range(2, n + 1):
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                break
        else:
            primes.append(num)
    return primes
```
"""
