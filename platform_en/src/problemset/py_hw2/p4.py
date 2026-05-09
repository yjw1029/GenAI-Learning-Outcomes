description = """
## Palindrome Number
Write a function `is_palindrome(x)`. Given an integer `x`, return `True` if it is a palindrome integer; otherwise return `False`. (3 pts)

Tip: Use `str` to convert an integer to a string, e.g., `str(12345) = "12345"`.
"""

title = "Palindrome Number (3 pts)"
score = 3

knowledge = ["string", "condition"]

code_template = """
def is_palindrome(x):
    # your code
    return ...
"""

code_entrypoint = "is_palindrome"

validcases = [
    {"input": [121], "output": True, "comment": "121 is a palindrome"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [123], "output": False, "comment": "123 is not a palindrome"},
    {"input": [-121], "output": False, "comment": "-121 is not a palindrome because of the negative sign"},
    {"input": [10], "output": False, "comment": "10 is not a palindrome"},
    {"input": [1], "output": True, "comment": "1 is a palindrome"},
    {"input": [1221], "output": True, "comment": "1221 is a palindrome"},
    {"input": [0], "output": True, "comment": "0 is a palindrome"},
]
answer = ""
