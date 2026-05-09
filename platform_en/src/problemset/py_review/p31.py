description = """
## Perfect Number Check
Given an integer `num`, write `is_perfect_number(num)` to check whether it is a perfect number. A perfect number equals the sum of its positive divisors excluding itself (e.g., 28). (5 pts)
"""

title = "Perfect Number Check (5 pts)"
score = 5

knowledge = ["number", "loop", "condition"]

code_template = """
def is_perfect_number(num):
    # your code
    return ...
"""

code_entrypoint = "is_perfect_number"

validcases = [
    {"input": [28], "output": True, "comment": "28 is a perfect number"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [6], "output": True, "comment": "6 is a perfect number"},
    {"input": [10], "output": False, "comment": "10 is not a perfect number"},
    {"input": [496], "output": True, "comment": "496 is a perfect number"},
    {"input": [8128], "output": True, "comment": "8128 is a perfect number"},
    {"input": [2], "output": False, "comment": "2 is not a perfect number"},
    {"input": [1], "output": False, "comment": "1 is not a perfect number"},
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
