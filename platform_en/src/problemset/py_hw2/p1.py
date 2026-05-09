description = """
## String Length
Write a function `string_length(s)` that returns the length of the input string.(1 pts)
"""

title = "String Length (1 pts)"
score = 1

knowledge = ["string"]

code_template = """
def string_length(s):
    # your code
    return ...
"""

code_entrypoint = "string_length"

validcases = [
    {"input": "hello", "output": 5, "comment": "Length of 'hello' is 5"},
]

testcases = [
    *validcases,
    # common cases
    {"input": "apple", "output": 5, "comment": "Length of 'apple' is 5"},
    {"input": "", "output": 0, "comment": "Length of an empty string is 0"},
    {"input": "1234567890", "output": 10, "comment": "Length of '1234567890' is 10"},
    {"input": "chinese", "output": 7, "comment": "Length of 'chinese' is 7"},
    {"input": "a b c", "output": 5, "comment": "Length of 'a b c' is 5, including spaces"},
]
answer = ""
