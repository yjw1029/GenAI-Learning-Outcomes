description = """
## Integer Sign
Given an integer variable `x`, write a function `judge_integer_sign` that sets the variable `s` to the string "POSITIVE", "NEGATIVE", or "ZERO" depending on whether `x` is positive, negative, or zero. (2 pts)
"""

title = "Integer Sign (2 pts)"
score = 2

knowledge = ["number", "condition"]

code_template = """
def judge_integer_sign(x):
    # your code
    return ...
"""

code_entrypoint = "judge_integer_sign"

validcases = [
    {"input": [5], "output": "POSITIVE", "comment": "5 is positive, so output 'POSITIVE'"},
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [0],
        "output": "ZERO",
        "comment": "0 is neither positive nor negative, so output 'ZERO'",
    },
    {"input": [-1], "output": "NEGATIVE", "comment": "-1 is negative, so output 'NEGATIVE'"},
    {"input": [10], "output": "POSITIVE", "comment": "10 is positive, so output 'POSITIVE'"},
    {
        "input": [-100],
        "output": "NEGATIVE",
        "comment": "-100 is negative, so output 'NEGATIVE'",
    },
    {"input": [999], "output": "POSITIVE", "comment": "999 is positive, so output 'POSITIVE'"},
]

answer = """
```Python
def judge_integer_sign(x):
    if x > 0:
        return "POSITIVE"
    elif x < 0:
        return "NEGATIVE"
    else:
        return "ZERO"
```
"""
