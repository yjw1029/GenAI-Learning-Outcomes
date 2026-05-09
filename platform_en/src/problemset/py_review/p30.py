description = """
## Find All Primes
Write a function `find_primes(n)` that takes an integer `n` and returns a list of all prime numbers from 2 to `n` (inclusive). (5 pts)
"""

title = "Find All Primes (5 pts)"
score = 5

knowledge = ["number", "loop", "condition"]

code_template = """
def find_primes(n):
    # your code
    return ...
"""

code_entrypoint = "find_primes"

validcases = [
    {"input": [10], "output": [2, 3, 5, 7], "comment": "Primes between 2 and 10"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [1], "output": [], "comment": "No primes when n=1"},
    {"input": [2], "output": [2], "comment": "2 is prime"},
    {"input": [5], "output": [2, 3, 5], "comment": "Primes between 2 and 5"},
    {"input": [15], "output": [2, 3, 5, 7, 11, 13], "comment": "Primes between 2 and 15"},
    {
        "input": [20],
        "output": [2, 3, 5, 7, 11, 13, 17, 19],
        "comment": "Primes between 2 and 20",
    },
]

answer = """
```Python
def find_primes(n):
    primes = []
    for num in range(2, n + 1):
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                break
        else:
            primes.append(num)
    return primes
```
"""
