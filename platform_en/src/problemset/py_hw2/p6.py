description = """
## Missing Employee Info

Given two dictionaries `employee_name` and `employee_salary`, where keys are employee IDs. Values are names in `employee_name` and salaries in `employee_salary`. Write a function `find_missing_info(employee_name, employee_salary)` to find employee IDs with missing info (has a name but no salary, or has a salary but no name). Return a list of IDs sorted ascending. (4 pts)

Tip: Use `nums.sort()` to sort a list. For example,
```python
nums = [1, 3, 2, 4]
nums.sort()
print(nums) # [1, 2, 3, 4]
```

Note: `sort` returns `None`.
"""

title = "Missing Employee Info (4 pts)"
score = 4

code_template = """
def find_missing_info(employee_name, employee_salary):
    # your code
    return ...
"""

knowledge = ["dict", "loop", "condition", "bool"]

code_entrypoint = "find_missing_info"

validcases = [
    {
        "input": [{1: "Alice", 2: "Bob", 3: "Charlie"}, {1: 50000, 2: 60000}],
        "output": [3],
        "comment": "Charlie's salary info is missing",
    },
]

testcases = [
    *validcases,
    {
        "input": [{1: "Alice", 2: "Bob"}, {1: 50000, 2: 60000, 3: 70000}],
        "output": [3],
        "comment": "Employee with ID 3 has salary info but no name info",
    },
    {
        "input": [{1: "Alice", 2: "Bob", 3: "Charlie"}, {1: 50000, 2: 60000, 3: 70000}],
        "output": [],
        "comment": "All employees have both name and salary info",
    },
    {
        "input": [{1: "Alice", 2: "Bob", 4: "David"}, {1: 50000, 3: 70000, 4: 80000}],
        "output": [2, 3],
        "comment": "Bob's salary info and employee with ID 3's name info are missing",
    },
    {
        "input": [{}, {1: 50000}],
        "output": [1],
        "comment": "No name info for the employee with salary info",
    },
    {
        "input": [{2: "Bob"}, {}],
        "output": [2],
        "comment": "No salary info for Bob",
    },
    {
        "input": [{}, {}],
        "output": [],
        "comment": "Both dictionaries are empty, no missing info",
    },
    {
        "input": [{1: "Alice", 3: "Charlie"}, {2: "David", 3: 70000}],
        "output": [1, 2],
        "comment": "Alice's salary info and David's name info are missing",
    },
]
answer = ""
