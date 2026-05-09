description = """
## Insert List Element
Write a function `insert_at_index(lst, element, index)` that takes a list and two integers: an element and a positive index. Insert the element at the specified index. If the index exceeds the current length, append the element to the end. (2 pts)
"""

title = "Insert List Element (2 pts)"
score = 2

code_template = """
def insert_at_index(lst, element, index):
    # your code
    return ...
"""

knowledge = ["list", "condition", "bool"]

code_entrypoint = "insert_at_index"

validcases = [
    {
        "input": [[1, 2, 3], 4, 1],
        "output": [1, 4, 2, 3],
        "comment": "Inserting 4 at index 1 in [1, 2, 3]",
    },
]

testcases = [
    *validcases,
    {
        "input": [[1, 2, 3], 5, 5],
        "output": [1, 2, 3, 5],
        "comment": "Index 5 exceeds the length of [1, 2, 3], so 5 is added at the end",
    },
    {
        "input": [[], 10, 0],
        "output": [10],
        "comment": "Inserting 10 at index 0 in an empty list",
    },
    {
        "input": [[1, 2, 3], 0, 3],
        "output": [1, 2, 3, 0],
        "comment": "Index 3 equals the length of [1, 2, 3], so 0 is added at the end",
    },
    {
        "input": [[1, 2, 3], 0, 0],
        "output": [0, 1, 2, 3],
        "comment": "Inserting 0 at index 0 in [1, 2, 3]",
    },
    {
        "input": [[1], 2, 1],
        "output": [1, 2],
        "comment": "Index 1 equals the length of [1], so 2 is added at the end",
    },
    {
        "input": [[1, 2, 3], 6, 10],
        "output": [1, 2, 3, 6],
        "comment": "Index 10 exceeds the length of [1, 2, 3], so 6 is added at the end",
    },
]

answer = """
```Python
def insert_at_index(lst, element, index):
	if index >= len(lst):
		lst.append(element)
	else:
		lst.insert(index, element)
	return lst
```
"""
