description = """
## Largest Elements in a List
Write a function `find_two_largest_numbers(lst)` that returns the largest and second-largest values in the list. The input list length is at least 2. (3 pts)
"""

title = "Largest Elements in a List (3 pts)"
score = 3

knowledge = ["loop", "condition", "list", "number"]

code_template = """
def find_two_largest_numbers(lst):
    # your code
    return ...
"""

code_entrypoint = "find_two_largest_numbers"

validcases = [
    {
        "input": [[1, 2, 3, 4, 5]],
        "output": (5, 4),
        "comment": "The two largest numbers are 5 and 4",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[10, 20, 15, 12, 11, 50]],
        "output": (50, 20),
        "comment": "The two largest numbers are 50 and 20",
    },
    {"input": [[3, 3, 3]], "output": (3, 3), "comment": "All elements in the list are the same"},
    {
        "input": [[-1, -3, -2, -4]],
        "output": (-1, -2),
        "comment": "The two largest numbers are -1 and -2",
    },
    {"input": [[8, 10, 10]], "output": (10, 10), "comment": "The list contains duplicates"},
    {"input": [[8, 10, 8]], "output": (10, 8), "comment": "The list contains duplicates"},
    {"input": [[-1e9, 3, 1e9]], "output": (1e9, 3), "comment": "List with very large values"},
]
answer = ""
