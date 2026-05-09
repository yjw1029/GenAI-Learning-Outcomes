description = """
## Count List Elements
Write a function `count_elements(lst)` that takes a list and returns the number of elements in the list. (1 pts)
"""

title = "Count List Elements (1 pts)"
score = 1
knowledge = ["list"]

code_template = """
def count_elements(lst):
    # your code
    return ...
"""

code_entrypoint = "count_elements"

validcases = [
    {
        "input": [["apple", "banana", "cherry"]],
        "output": 3,
        "comment": "List has 3 elements",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[]], "output": 0, "comment": "Empty list"},
    {"input": [["orange"]], "output": 1, "comment": "List has 1 element"},
    {"input": [["apple", "banana"]], "output": 2, "comment": "List has 2 elements"},
    {
        "input": [["dog", "cat", "bird", "fish"]],
        "output": 4,
        "comment": "List has 4 elements",
    },
    {
        "input": [["a", "b", "c", "d", "e", "f", "g"]],
        "output": 7,
        "comment": "List has 7 elements",
    },
]

answer = """
```Python
def count_elements(lst):
    return len(lst)
```
"""
