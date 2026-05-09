description = """
## Greatest Common Divisor
Write a function `gcd(a, b)` that takes two positive integers and returns their greatest common divisor. (4 pts)

Tip: A divisor is an integer that divides another integer exactly. For example, divisors of 12 include 1, 2, 3, 4, 6, 12. The GCD is the largest common divisor.
"""

title = "Greatest Common Divisor (4 pts)"
score = 4

code_template = """
def gcd(a, b):
    # your code
    return ...
"""

knowledge = ["number", "loop", "condition", "bool"]

code_entrypoint = "gcd"

validcases = [
    {
        "input": [8, 12],
        "output": 4,
        "comment": "GCD of 8 and 12 is 4",
    }
]

testcases = [
    *validcases,
    {
        "input": [17, 13],
        "output": 1,
        "comment": "GCD of 17 and 13 is 1",
    },
    {
        "input": [21, 14],
        "output": 7,
        "comment": "GCD of 21 and 14 is 7",
    },
    {
        "input": [100, 10],
        "output": 10,
        "comment": "GCD of 100 and 10 is 10",
    },
    {
        "input": [35, 10],
        "output": 5,
        "comment": "GCD of 35 and 10 is 5",
    },
    {
        "input": [31, 2],
        "output": 1,
        "comment": "GCD of 31 and 2 is 1",
    },
    {
        "input": [1, 1],
        "output": 1,
        "comment": "GCD of 1 and 1 is 1",
    },
    {
        "input": [99, 33],
        "output": 33,
        "comment": "GCD of 99 and 33 is 33",
    },
    {
        "input": [150, 100],
        "output": 50,
        "comment": "GCD of 150 and 100 is 50",
    },
    {
        "input": [81, 27],
        "output": 27,
        "comment": "GCD of 81 and 27 is 27",
    },
]

answer = """
```Python
# Euclidean algorithm
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# By definition
def gcd(a, b):
    if a < b:
        min_num = a
    else:
        min_num = b

    for i in range(min_num, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
```
"""
