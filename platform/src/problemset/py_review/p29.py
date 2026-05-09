description = """
## ATM机交易
编写一个函数 `atm_transactions(balance, transactions)`，它接受一个初始余额（整数）和一个交易字典作为参数。交易字典包含两种交易类型的键："D" 代表存款和 "W" 代表取款。每个键对应的值是一个金额的列表，表示进行的一系列存款或取款操作。函数需要计算并返回经过所有交易操作后的最终余额。（4 分）
"""

title = "ATM机交易（4 分）"
score = 4

knowledge = ["dict", "loop"]

code_template = """
def atm_transactions(balance, transactions):
    # 你的代码
    return ...
"""

code_entrypoint = "atm_transactions"

validcases = [
    {
        "input": [1000, {"D": [300, 200], "W": [500, 100]}],
        "output": 900,
        "comment": "初始余额为 1000。存款操作后余额增加 300 + 200，取款操作后余额减少 500 + 100。最终余额为 900。",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [500, {"D": [100], "W": [50]}],
        "output": 550,
        "comment": "初始余额为 500。存款操作后余额增加 100，取款操作后余额减少 50。最终余额为 550。",
    },
    {
        "input": [2000, {"D": [500, 300], "W": [200, 100, 50]}],
        "output": 2450,
        "comment": "初始余额为 2000。存款操作后余额增加 500 + 300，取款操作后余额减少 200 + 100 + 50。最终余额为 2450。",
    },
    {
        "input": [0, {"D": [100, 200, 300], "W": [150, 100]}],
        "output": 350,
        "comment": "初始余额为 0。存款操作后余额增加 100 + 200 + 300，取款操作后余额减少 150 + 100。最终余额为 350。",
    },
    {
        "input": [750, {"D": [], "W": []}],
        "output": 750,
        "comment": "没有任何交易，余额不变。",
    },
    {
        "input": [100, {"W": [50, 10, 20]}],
        "output": 20,
        "comment": "初始余额为 100。仅有取款操作，余额减少 50 + 10 + 20。最终余额为 20。",
    },
    {
        "input": [500, {"D": [500], "W": [1000]}],
        "output": 0,
        "comment": "初始余额为 500。存款操作后余额增加 500，取款操作后余额减少 1000。因为不能透支，所以最终余额为 0。",
    },
]

answer = """
```Python
def atm_transactions(balance, transactions):
    for action in transactions:
        amounts = transactions[action]
        for amount in amounts:
            if action == "D":
                balance += amount
            elif action == "W":
                balance -= amount
    return balance
```
"""
