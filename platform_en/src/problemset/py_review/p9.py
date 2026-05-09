description = """
## Calculate Average
Write a function `calculate_average(scores)` that takes a list of integer scores and returns the average score. (2 pts)
"""

title = "Calculate Average (2 pts)"
score = 2

knowledge = ["list", "loop", "number"]

code_template = """
def calculate_average(scores):
    # your code
    return ...
"""

code_entrypoint = "calculate_average"

validcases = [
    {
        "input": [[80, 90, 100]],
        "output": 90.0,
        "comment": "Average is (80 + 90 + 100) / 3 = 90.0",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[50, 60, 70, 80]],
        "output": 65.0,
        "comment": "Average is (50 + 60 + 70 + 80) / 4 = 65.0",
    },
    {"input": [[100, 100, 100]], "output": 100.0, "comment": "All scores are 100"},
    {"input": [[40, 50]], "output": 45.0, "comment": "Average is (40 + 50) / 2 = 45.0"},
    {
        "input": [[77, 88, 99, 66, 55]],
        "output": 77.0,
        "comment": "Average is (77 + 88 + 99 + 66 + 55) / 5 = 77.0",
    },
    {"input": [[83]], "output": 83.0, "comment": "Single score, average equals the score"},
]

answer = """
```Python
def calculate_average(scores):
    total = 0
    for score in scores:
        total += score
    return total / len(scores) if len(scores) > 0 else 0
```
"""
