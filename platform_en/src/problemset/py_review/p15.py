description = """
## Total Salary
Write a function `calculate_total_salary(salaries)` that takes a dictionary `salaries` mapping employee names to salaries (integers), and returns the total salary. (3 pts)
"""

title = "Total Salary (3 pts)"
score = 3

knowledge = ["dict", "loop"]

code_template = """
def calculate_total_salary(salaries):
    # your code
    return ...
"""

code_entrypoint = "calculate_total_salary"

validcases = [
    {
        "input": [{"Alice": 30000, "Bob": 25000, "Charlie": 28000}],
        "output": 83000,
        "comment": "Total salary is 30000 + 25000 + 28000 = 83000",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"Tom": 50000, "Jerry": 40000}],
        "output": 90000,
        "comment": "Total salary is 50000 + 40000 = 90000",
    },
    {"input": [{"Anna": 60000}], "output": 60000, "comment": "Single employee case"},
    {
        "input": [{"Bob": 25000, "Charlie": 28000, "Dave": 32000}],
        "output": 85000,
        "comment": "Total salary is 25000 + 28000 + 32000 = 85000",
    },
    {
        "input": [
            {},
        ],
        "output": 0,
        "comment": "Empty dictionary case",
    },
    {
        "input": [{"Lily": 30000, "Rose": 70000, "Daisy": 40000}],
        "output": 140000,
        "comment": "Total salary is 30000 + 70000 + 40000 = 140000",
    },
]

answer = """
```Python
def calculate_total_salary(salaries):
    total_salary = 0
    for key in salaries:
        total_salary += salaries[key]
    return total_salary
```
"""
