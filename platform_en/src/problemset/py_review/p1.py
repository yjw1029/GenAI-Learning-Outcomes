description = """
## Check Positive Number
Write a function `is_positive(num)` that takes an integer and checks whether the number is positive. Return True if it is positive, otherwise return False. (1 pts)
"""

title = "Check Positive Number (1 pts)"
score = 1

knowledge = ["condition", "bool"]

code_template = """
def is_positive(num):
    # your code
    return ...
"""

code_entrypoint = "is_positive"

validcases = [
    {"input": [10], "output": True, "comment": "10 is positive"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [1], "output": True, "comment": "1 is positive"},
    {"input": [0], "output": False, "comment": "0 is not positive"},
    {"input": [-1], "output": False, "comment": "-1 is not positive"},
    {"input": [100], "output": True, "comment": "100 is positive"},
    {"input": [-100], "output": False, "comment": "-100 is not positive"},
]

answer = """
```Python
def is_positive(num):
    return num > 0
```
"""
