description = """
## Square Dictionary
Write a function `square_dict(n)` that returns a dictionary with `n` elements. Keys are 0 to `n-1`, and each value is the square of its key. Order should be from 0 to `n-1`. (2 pts)
"""

title = "Square Dictionary (2 pts)"
score = 2

knowledge = ["dict", "loop"]

code_template = """
def square_dict(n):
    # your code
    return ...
"""

code_entrypoint = "square_dict"

validcases = [
    {
        "input": 3,
        "output": {0: 0, 1: 1, 2: 4},
        "comment": "Keys 0 to 2 with values as squares",
    },
]

testcases = [
    *validcases,
    {
        "input": 5,
        "output": {0: 0, 1: 1, 2: 4, 3: 9, 4: 16},
        "comment": "Keys 0 to 4 with values as squares",
    },
    {"input": 1, "output": {0: 0}, "comment": "Only key 0"},
    {"input": 0, "output": {}, "comment": "No key-value pairs"},
    {
        "input": 10,
        "output": {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36, 7: 49, 8: 64, 9: 81},
        "comment": "Keys 0 to 9 with values as squares",
    },
]
answer = ""
