description = """
## Order Odds Before Evens
Write a function `order_odd_even(nums)` that reorders the list `nums` so that all odd numbers come before even numbers, while preserving the original relative order. (3 pts)
"""

title = "Order Odds Before Evens (3 pts)"
score = 3

knowledge = ["list", "loop"]

code_template = """
def order_odd_even(nums):
    # your code
    return ...
"""

code_entrypoint = "order_odd_even"

validcases = [
    {
        "input": [[3, 1, 2, 4]],
        "output": [3, 1, 2, 4],
        "comment": "Odds 3, 1 before evens 2, 4, order preserved.",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[1, 2, 3, 4, 5, 6]],
        "output": [1, 3, 5, 2, 4, 6],
        "comment": "Odds 1, 3, 5 before evens 2, 4, 6, order preserved.",
    },
    {
        "input": [[10, 20, 30, 40]],
        "output": [10, 20, 30, 40],
        "comment": "All even, order unchanged.",
    },
    {"input": [[5, 7, 9]], "output": [5, 7, 9], "comment": "All odd, order unchanged."},
    {
        "input": [[8, 1, 3, 6, 5]],
        "output": [1, 3, 5, 8, 6],
        "comment": "Odds 1, 3, 5 before evens 8, 6, order preserved.",
    },
    {
        "input": [[2, 4, 6, 8, 3, 1, 5, 7]],
        "output": [3, 1, 5, 7, 2, 4, 6, 8],
        "comment": "Odds 3, 1, 5, 7 before evens 2, 4, 6, 8, order preserved.",
    },
    {
        "input": [[0, 2, 4, 6, 8]],
        "output": [0, 2, 4, 6, 8],
        "comment": "All even including 0, order unchanged.",
    },
]

answer = """
```Python
def order_odd_even(nums):
    odd = []
    even = []
    for x in nums:
        if x % 2 == 1:
            odd.append(x)
        else:
            even.append(x)
    return odd + even
```
"""
