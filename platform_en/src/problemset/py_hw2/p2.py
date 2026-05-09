description = """
## Absolute Difference
Given two values `x` and `y`, write a function `absolute_difference(x, y)` to compute the absolute difference.(2 pts)
"""

title = "Absolute Difference (2 pts)"
score = 2

knowledge = ["number", "condition"]

code_template = """
def absolute_difference(x, y):
    # your code
    return ...
"""

code_entrypoint = "absolute_difference"

validcases = [
    {"input": [3, 7], "output": 4, "comment": "Absolute difference |3 - 7| = 4"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [10, 5], "output": 5, "comment": "Absolute difference |10 - 5| = 5"},
    {"input": [-3, 2], "output": 5, "comment": "Absolute difference |-3 - 2| = 5"},
    {"input": [0, 0], "output": 0, "comment": "Absolute difference |0 - 0| = 0"},
    {"input": [-5, -10], "output": 5, "comment": "Absolute difference |-5 - (-10)| = 5"},
    {"input": [15, -5], "output": 20, "comment": "Absolute difference |15 - (-5)| = 20"},
]
answer = ""
