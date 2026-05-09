description = """
## Fibonacci Sequence

Write a function `fibonacci_sequence(n)` that generates a Fibonacci sequence of length `n` (`n` is a non-negative integer) and returns it as a list. (4 pts)

Tip: In the Fibonacci sequence, each number is the sum of the previous two, starting with 0 and 1.
"""

title = "Fibonacci Sequence (4 pts)"
score = 4

knowledge = ["number", "list", "loop"]

code_template = """
def fibonacci_sequence(n):
    # your code
    return ...
"""

code_entrypoint = "fibonacci_sequence"

validcases = [
    {"input": 5, "output": [0, 1, 1, 2, 3], "comment": "First 5 Fibonacci numbers"},
]

testcases = [
    *validcases,
    {"input": 0, "output": [], "comment": "Length 0 returns an empty list"},
    {"input": 1, "output": [0], "comment": "Length 1 starts with 0"},
    {"input": 2, "output": [0, 1], "comment": "First 2 Fibonacci numbers"},
    {"input": 8, "output": [0, 1, 1, 2, 3, 5, 8, 13], "comment": "First 8 Fibonacci numbers"},
    {
        "input": 10,
        "output": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34],
        "comment": "First 10 Fibonacci numbers",
    },
]
answer = ""
