description = """
## Are Two Halves Similar

Write a function `are_halves_similar(s)` that takes an even-length string `s`. Split it into two equal halves, `a` and `b`.

Two strings are **similar** if they contain the same number of vowels `('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U')`. Note that `s` may contain both upper- and lower-case letters.

If `a` and `b` are similar, return `True`; otherwise return `False`. (5 pts)
"""

title = "Are Two Halves Similar (5 pts)"
score = 5

knowledge = ["number", "string", "condition", "loop"]

code_template = """
def are_halves_similar(s):
    # your code
    return ...
"""

code_entrypoint = "are_halves_similar"

validcases = [
    {
        "input": ["bookkeeper"],
        "output": False,
        "comment": "First half has 2 vowels, second half has 3",
    },
]

testcases = [
    *validcases,
    {
        "input": ["bookkeeper"],
        "output": False,
        "comment": "First half has 2 vowels, second half has 3",
    },
    {"input": ["AaBbCc"], "output": False, "comment": "Second half has no vowels"},
    {
        "input": ["HelloWorld"],
        "output": False,
        "comment": "First half has 2 vowels, second half has 1",
    },
    {"input": ["AbCdEfGh"], "output": True, "comment": "Both halves have the same number of vowels"},
    {"input": ["eeEEOOoo"], "output": True, "comment": "Both halves have the same number of vowels"},
    {"input": ["aeiobcDEIO"], "output": False, "comment": "The halves have different vowel counts"},
    {
        "input": ["bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"],
        "output": True,
        "comment": "Both halves have no vowels",
    },
    {"input": ["abcd1234efgh5678"], "output": True, "comment": "Both halves have 1 vowel"},
    {"input": ["ae"], "output": True, "comment": "Both halves have the same number of vowels"},
    {"input": ["ab"], "output": False, "comment": "The halves have different vowel counts"},
]
answer = ""
