description = """
## Character Frequency
Write a function `char_frequency(s)` that takes a string and returns a dictionary of character counts, preserving the order of first appearance. (3 pts)
"""

title = "Character Frequency (3 pts)"
score = 3

knowledge = ["string", "dict"]

code_template = """
def char_frequency(s):
    # your code
    return ...
"""

code_entrypoint = "char_frequency"

validcases = [
    {
        "input": "hello",
        "output": {"h": 1, "e": 1, "l": 2, "o": 1},
        "comment": "Basic case",
    },
]

testcases = [
    *validcases,
    {"input": "aabbcc", "output": {"a": 2, "b": 2, "c": 2}, "comment": "Repeated characters"},
    {"input": "", "output": {}, "comment": "Empty string"},
    {
        "input": "abcd",
        "output": {"a": 1, "b": 1, "c": 1, "d": 1},
        "comment": "No repeated characters",
    },
    {"input": "aAaAaA", "output": {"a": 3, "A": 3}, "comment": "Case sensitive"},
    {"input": "123321", "output": {"1": 2, "2": 2, "3": 2}, "comment": "Numeric characters"},
    {"input": "ab!ab!", "output": {"a": 2, "b": 2, "!": 2}, "comment": "Includes special characters"},
]

answer = """
```Python
def char_frequency(s):
	frequency = {}
	for char in s:
		if char not in frequency:
			frequency[char] = 0
		frequency[char] += 1
	return frequency
```
"""
