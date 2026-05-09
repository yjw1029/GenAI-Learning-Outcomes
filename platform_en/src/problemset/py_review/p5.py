description = """
## Merge Two Lists
Write a function `merge_lists(list1, list2)` that takes two lists and returns a new list containing all elements from both input lists. (1 pts)
"""

title = "Merge Two Lists (1 pts)"
score = 1

knowledge = ["list"]

code_template = """
def merge_lists(list1, list2):
    # your code
    return ...
"""

code_entrypoint = "merge_lists"

validcases = [
    {
        "input": [[1, 2, 3], [4, 5, 6]],
        "output": [1, 2, 3, 4, 5, 6],
        "comment": "Merge [1, 2, 3] and [4, 5, 6]",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[], [1, 2, 3]],
        "output": [1, 2, 3],
        "comment": "One empty list and one non-empty list",
    },
    {
        "input": [[1, 2, 3], []],
        "output": [1, 2, 3],
        "comment": "One non-empty list and one empty list",
    },
    {"input": [[], []], "output": [], "comment": "Two empty lists"},
    {
        "input": [[-1, -2, -3], [4, 5, 6]],
        "output": [-1, -2, -3, 4, 5, 6],
        "comment": "Lists with negatives",
    },
    {
        "input": [[1, 2], [3, 4, 5, 6]],
        "output": [1, 2, 3, 4, 5, 6],
        "comment": "Lists of different lengths",
    },
    {
        "input": [["a", "b"], ["c", "d"]],
        "output": ["a", "b", "c", "d"],
        "comment": "List of strings",
    },
]

answer = """
```Python
def merge_lists(list1, list2):
    return list1 + list2
```
"""
