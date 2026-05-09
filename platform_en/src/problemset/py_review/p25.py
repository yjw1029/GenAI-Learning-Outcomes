description = """
## Majority Element
Given an array of size `n`, write `majority_element(nums)` to find the element that appears more than [n/2] times. If no element appears more than [n/2], return `None`. (4 pts)
"""

title = "Majority Element (4 pts)"
score = 4

knowledge = ["list", "loop", "condition"]

code_template = """
def majority_element(nums):
    # your code
    return ...
"""

code_entrypoint = "majority_element"

validcases = [
    {"input": [[3, 2, 3]], "output": 3, "comment": "3 appears more than half the time"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[1, 1, 2, 2, 2]], "output": 2, "comment": "2 appears more than half the time"},
    {
        "input": [[1, 2, 3, 4, 5]],
        "output": None,
        "comment": "No element appears more than half",
    },
    {"input": [[6, 6, 6, 7, 7]], "output": 6, "comment": "6 appears more than half the time"},
    {"input": [[8]], "output": 8, "comment": "Single element is the majority by default"},
    {
        "input": [[9, 9, 9, 10, 10, 10, 10]],
        "output": 10,
        "comment": "10 appears more than half the time",
    },
]

answer = """
```python
def majority_element(nums):
    count = {}
    for num in nums:
        if num in count:
            count[num] += 1
        else:
            count[num] = 1

        if count[num] > len(nums) // 2:
            return num

    return None
```
"""
