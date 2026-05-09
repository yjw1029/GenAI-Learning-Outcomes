description = """
## Power
Given an integer `x` (0, positive, or negative) and a non-negative integer `n`, write a function `power(x, n)` that returns `x` raised to the `n`th power. (1 pts)
"""

title = "Power (1 pts)"
score = 1

knowledge = ["number"]

code_template = """
def power(x, n):
    # your code
    return ...
"""

code_entrypoint = "power"

validcases = [
    {"input": [2, 3], "output": 8, "comment": "2^3 = 8"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [3, 2], "output": 9, "comment": "3^2 = 9"},
    {"input": [10, 0], "output": 1, "comment": "10^0 = 1"},
    {"input": [1, 100], "output": 1, "comment": "1^100 = 1"},
    {"input": [0, 5], "output": 0, "comment": "0^5 = 0"},
    {"input": [-2, 4], "output": 16, "comment": "(-2)^4 = 16"},
    {"input": [-3, 3], "output": -27, "comment": "(-3)^3 = -27"},
]

answer = """
```Python
def power(x, n):
    return x ** n
```
"""
