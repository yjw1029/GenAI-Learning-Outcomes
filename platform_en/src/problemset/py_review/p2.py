description = """
## Negate List
Given an integer list `lst`, create a new list that contains the negation of each value. For example, given `[-1, 2, -3, 4]`, the result should be `[1, -2, 3, -4]`. (1 pts)
"""

title = "Negate List (1 pts)"
score = 1

knowledge = ["list", "loop"]

code_template = """
def negate_list(lst):
    # your code
    return ...
"""

code_entrypoint = "negate_list"

validcases = [
    {
        "input": [[-1, 2, -3, 4]],
        "output": [1, -2, 3, -4],
        "comment": "Negation of each element",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[0, 0, 0]], "output": [0, 0, 0], "comment": "All-zero list stays all zeros"},
    {
        "input": [[-5, -4, -3, -2, -1]],
        "output": [5, 4, 3, 2, 1],
        "comment": "Negation of negative list gives positives",
    },
    {
        "input": [[1, 2, 3, 4, 5]],
        "output": [-1, -2, -3, -4, -5],
        "comment": "Negation of positive list gives negatives",
    },
    {
        "input": [[-1, 0, 1]],
        "output": [1, 0, -1],
        "comment": "List with negatives, zero, and positives",
    },
    {"input": [[100]], "output": [-100], "comment": "Single positive number negated"},
    {"input": [[-100]], "output": [100], "comment": "Single negative number negated"},
]


answer = """
```Python
def negate_list(lst):
    negated_list = []
    for x in lst:
        negated_list.append(-x)
    return negated_list
```
"""
