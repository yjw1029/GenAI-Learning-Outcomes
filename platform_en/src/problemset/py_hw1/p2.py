description = """
## Leap Year Check
Write a function `is_leap_year(year)` to check whether a given year is a leap year. Return `True` if it is, otherwise `False`. A leap year is:
- Divisible by 4 but not by 100; or
- Divisible by 400. (2 pts)
"""

title = "Leap Year Check (2 pts)"
score = 2

code_template = """
def is_leap_year(year):
    # your code
    return ...
"""

knowledge = ["number", "condition", "bool"]

code_entrypoint = "is_leap_year"

validcases = [
    {
        "input": 2000,
        "output": True,
        "comment": "2000 is a leap year because it is divisible by 400",
    },
]

testcases = [
    *validcases,
    {"input": 2001, "output": False, "comment": "2001 is not a leap year"},
    {
        "input": 1900,
        "output": False,
        "comment": "1900 is not a leap year because it is divisible by 100 but not by 400",
    },
    {
        "input": 2004,
        "output": True,
        "comment": "2004 is a leap year because it is divisible by 4 but not by 100",
    },
    {
        "input": 2100,
        "output": False,
        "comment": "2100 is not a leap year because it is divisible by 100 but not by 400",
    },
    {
        "input": 1600,
        "output": True,
        "comment": "1600 is a leap year because it is divisible by 400",
    },
    {"input": 2024, "output": True, "comment": "2024 is a leap year"},
    {"input": 2023, "output": False, "comment": "2023 is not a leap year"},
]

answer = """
```Python
def is_leap_year(year):
	if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
		return True
	else:
		return False
```
"""
