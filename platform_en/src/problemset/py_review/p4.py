description = """
## Is List Empty
Write a function `is_list_empty(lst)` that takes a list and returns a boolean indicating whether the list is empty. (1 pts)
"""

title = "Is List Empty (1 pts)"
score = 1

knowledge = ["list", "bool"]

code_template = """
def is_list_empty(lst):
    # your code
    return ...
"""

code_entrypoint = "is_list_empty"

validcases = [
    {"input": [[]], "output": True, "comment": "Empty list should return True"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[1, 2, 3]], "output": False, "comment": "Non-empty list should return False"},
    {"input": [[0]], "output": False, "comment": "Single-element list is not empty"},
    {"input": [[[], []]], "output": False, "comment": "List containing an empty list is not empty"},
    {"input": [[None]], "output": False, "comment": "List containing None is not empty"},
    {"input": [[""]], "output": False, "comment": "List containing empty string is not empty"},
]

answer = """
```Python
def is_list_empty(lst):
    return len(lst) == 0
```
"""
