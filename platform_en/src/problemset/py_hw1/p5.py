description = """
## Count Vowels in a String
Write a function `count_vowels(s)` that returns the number of vowels `('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U')` in a string `s`. Note that `s` may contain both upper- and lower-case letters. (3 pts)
"""

title = "Count Vowels in a String (3 pts)"
score = 3

code_template = """
def count_vowels(s):
    # your code
    return ...
"""

knowledge = ["string", "loop", "condition", "bool"]

code_entrypoint = "count_vowels"

validcases = [
    {
        "input": "hello",
        "output": 2,
        "comment": "The word 'hello' has 2 vowels",
    },
]

testcases = [
    *validcases,
    {
        "input": "HELLO",
        "output": 2,
        "comment": "The word 'HELLO' in uppercase also has 2 vowels",
    },
    {
        "input": "abcdEfgh",
        "output": 2,
        "comment": "The string 'abcdEfgh' has 2 vowels",
    },
    {
        "input": "",
        "output": 0,
        "comment": "An empty string has 0 vowels",
    },
    {
        "input": "1234567890",
        "output": 0,
        "comment": "A string with no letters has 0 vowels",
    },
    {
        "input": "AEIOUaeiou",
        "output": 10,
        "comment": "The string 'AEIOUaeiou' contains all the vowels, both uppercase and lowercase",
    },
    {
        "input": "bcdfgBCDFG",
        "output": 0,
        "comment": "The string 'bcdfgBCDFG' has 0 vowels as it contains only consonants",
    },
    {
        "input": "python Programming",
        "output": 4,
        "comment": "The string 'python Programming' has 3 vowels",
    },
    {
        "input": "1234AEIOUabcd",
        "output": 6,
        "comment": "The string '1234AEIOUabcd' has 5 vowels",
    },
]

answer = """
```Python
def count_vowels(s):
    num = 0
    for char in s:
        if char in ('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'):
            num = num + 1
    return num
```
"""
