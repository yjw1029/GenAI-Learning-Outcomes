description = """
## Product of Even Indices
Write a function `product_even_index(nums)` that takes a list of numbers and returns the product of elements at even indices. (3 pts)
"""

title = "Product of Even Indices (3 pts)"
score = 3

knowledge = ["list", "loop"]

code_template = """
def product_even_index(nums):
    # your code
    return ...
"""

code_entrypoint = "product_even_index"

validcases = [
    {
        "input": [[1, 3, 5, 7, 9]],
        "output": 45,
        "comment": "Product of indices 0, 2, 4 is 1*5*9=45",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[2, 4, 6, 8, 10]],
        "output": 120,
        "comment": "Product of indices 0, 2, 4 is 2*6*10=120",
    },
    {"input": [[3, 3, 3, 3]], "output": 9, "comment": "Product of indices 0, 2 is 3*3=9"},
    {"input": [[10]], "output": 10, "comment": "Only index 0 element, product is 10"},
    {"input": [[1, 2]], "output": 1, "comment": "Only index 0 element, product is 1"},
    {
        "input": [[-2, 3, -4, 5, -6]],
        "output": -48,
        "comment": "Product of indices 0, 2, 4 is -2*(-4)*(-6)=-48",
    },
]

answer = """
```Python
def product_even_index(nums):
    product = 1
    for i in range(0, len(nums), 2):
        product *= nums[i]
    return product
```
"""
