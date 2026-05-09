description = """
## Replace Digits With Count
Write a function `replace_digits_with_count(s)` that takes a string `s`. Replace each digit character with that many repeated copies of itself. For example, "a3b2c4d" becomes "a333b22c4444d". (4 pts)
"""

title = "Replace Digits With Count (4 pts)"
score = 4

knowledge = ["string", "loop", "condition"]

code_template = """
def replace_digits_with_count(s):
    # your code
    return ...
"""

code_entrypoint = "replace_digits_with_count"

validcases = [
    {
        "input": ["a3b2c4d"],
        "output": "a333b22c4444d",
        "comment": "Each digit is replaced by repeated copies",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["x5y0z2"],
        "output": "x55555yz22",
        "comment": "5 becomes five 5s, 0 adds nothing, 2 becomes two 2s",
    },
    {
        "input": ["123"],
        "output": "122333",
        "comment": "1 has no following digit; 2 becomes two 2s; 3 becomes three 3s",
    },
    {
        "input": ["no digits"],
        "output": "no digits",
        "comment": "No digits, no replacement",
    },
    {"input": ["9"], "output": "999999999", "comment": "9 becomes nine 9s"},
    {"input": [""], "output": "", "comment": "Empty string"},
]

answer = """
```Python
def replace_digits_with_count(s):
    result = ''
    i = 0
    while i < len(s):
        char = s[i]
        if char >= '0' and char <= '9':
            result += char * int(char)
        else:
            result += char
        i += 1
    return result
```
"""
