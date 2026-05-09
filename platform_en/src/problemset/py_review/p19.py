description = """
## Generate Username
Write a function `generate_username(name, birth_year)` that takes a name and a birth year, and returns a username made of the first letter of the name and the last two digits of the birth year. (3 pts)
"""

title = "Generate Username (3 pts)"
score = 3

knowledge = ["string", "index"]

code_template = """
def generate_username(name, birth_year):
    # your code
    return ...
"""

code_entrypoint = "generate_username"

validcases = [
    {
        "input": ["Alice", 1990],
        "output": "A90",
        "comment": "First letter 'A', last two digits '90', username 'A90'",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["Bob", 1985],
        "output": "B85",
        "comment": "First letter 'B', last two digits '85', username 'B85'",
    },
    {
        "input": ["Charlie", 2001],
        "output": "C01",
        "comment": "First letter 'C', last two digits '01', username 'C01'",
    },
    {
        "input": ["Diana", 1999],
        "output": "D99",
        "comment": "First letter 'D', last two digits '99', username 'D99'",
    },
    {
        "input": ["Eva", 2022],
        "output": "E22",
        "comment": "First letter 'E', last two digits '22', username 'E22'",
    },
    {
        "input": ["Frank", 1980],
        "output": "F80",
        "comment": "First letter 'F', last two digits '80', username 'F80'",
    },
]

answer = """
```Python
def generate_username(name, birth_year):
    return name[0] + str(birth_year)[-2:]
```
"""
