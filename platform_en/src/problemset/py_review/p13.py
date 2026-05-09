description = """
## Are Students Passing
Write a function `are_students_passing(grades)` that takes a dictionary `grades` of student names to scores. Return a new dictionary mapping each student to whether they pass (score >= 60 is True, otherwise False). (2 pts)
"""

title = "Are Students Passing (2 pts)"
score = 2

knowledge = ["dict", "condition"]

code_template = """
def are_students_passing(grades):
    # your code
    return ...
"""

code_entrypoint = "are_students_passing"

validcases = [
    {
        "input": [{"Alice": 58, "Bob": 72, "Charlie": 49}],
        "output": {"Alice": False, "Bob": True, "Charlie": False},
        "comment": "Alice and Charlie fail, Bob passes",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"Dan": 90, "Eve": 100, "Frank": 65}],
        "output": {"Dan": True, "Eve": True, "Frank": True},
        "comment": "All students pass",
    },
    {"input": [{"Gina": 59}], "output": {"Gina": False}, "comment": "Gina fails"},
    {
        "input": [{"Harry": 60, "Ian": 59}],
        "output": {"Harry": True, "Ian": False},
        "comment": "Harry passes, Ian fails",
    },
    {"input": [{"Jack": 0}], "output": {"Jack": False}, "comment": "Jack fails"},
    {"input": [{"Kim": 100}], "output": {"Kim": True}, "comment": "Kim passes"},
    {
        "input": [{"Leo": 58, "Mia": 72, "Nina": 49, "Oscar": 60}],
        "output": {"Leo": False, "Mia": True, "Nina": False, "Oscar": True},
        "comment": "Mia and Oscar pass, Leo and Nina fail",
    },
]

answer = """
```Python
def are_students_passing(grades):
    passing = {}
    for student in grades:
        passing[student] = grades[student] >= 60
    return passing
```
"""
