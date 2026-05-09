description = """
## 完美数判断
给定一个整数`num`，编写一个函数`is_perfect_number(num)`，它接受这个整数作为参数，并判断该数是否为完美数。一个完美数是指其所有正除数（不包括其自身）之和等于它本身的数。（例如，28的正除数是1、2、4、7、14，这些数的和恰好是28，因此28是一个完美数。）（5 分）
"""

title = "完美数判断（5 分）"
score = 5

knowledge = ["number", "loop", "condition"]

code_template = """
def is_perfect_number(num):
    # 你的代码
    return ...
"""

code_entrypoint = "is_perfect_number"

validcases = [
    {"input": [28], "output": True, "comment": "28是一个完美数"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [6], "output": True, "comment": "6是一个完美数"},
    {"input": [10], "output": False, "comment": "10不是一个完美数"},
    {"input": [496], "output": True, "comment": "496是一个完美数"},
    {"input": [8128], "output": True, "comment": "8128是一个完美数"},
    {"input": [2], "output": False, "comment": "2不是一个完美数"},
    {"input": [1], "output": False, "comment": "1不是一个完美数"},
]

answer = """
```Python
def is_perfect_number(num):
    if num < 2:
        return False
    sum_of_divisors = 0
    for i in range(1, num):
        if num % i == 0:
            sum_of_divisors += i
    return sum_of_divisors == num
```
"""
