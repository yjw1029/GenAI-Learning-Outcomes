description = """
## Factorial
Write a function `factorial(n)` that takes an integer and returns its factorial. The factorial of `n` is the product of all positive integers less than or equal to `n`. If the input is negative, return `None`. (4 pts)
"""

title = "Factorial (4 pts)"
score = 4

knowledge = ["list", "loop", "condition"]

code_template = """
def factorial(n):
    # your code
    return ...
"""

code_entrypoint = "factorial"

validcases = [
    {"input": [5], "output": 120, "comment": "5! = 120"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [0], "output": 1, "comment": "0! = 1"},
    {"input": [1], "output": 1, "comment": "1! = 1"},
    {"input": [3], "output": 6, "comment": "3! = 6"},
    {"input": [10], "output": 3628800, "comment": "10! = 3628800"},
]

answer = """
```Python
def factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```
"""
