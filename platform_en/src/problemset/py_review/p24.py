description = """
## Longest Common Prefix
Write a function `longest_common_prefix(str1, str2)` that takes two strings and returns their longest common prefix. (4 pts)
"""

title = "Longest Common Prefix (4 pts)"
score = 4

knowledge = ["string", "loop"]

code_template = """
def longest_common_prefix(str1, str2):
    # your code
    return ...
"""

code_entrypoint = "longest_common_prefix"

validcases = [
    {
        "input": ["flower", "flow"],
        "output": "flow",
        "comment": "Longest common prefix of 'flower' and 'flow' is 'flow'",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["class", "classes"],
        "output": "class",
        "comment": "Longest common prefix of 'class' and 'classes' is 'class'",
    },
    {
        "input": ["abc", "abcd"],
        "output": "abc",
        "comment": "Longest common prefix of 'abc' and 'abcd' is 'abc'",
    },
    {
        "input": ["", "abc"],
        "output": "",
        "comment": "One is empty string, LCP is ''",
    },
    {
        "input": ["abc", "def"],
        "output": "",
        "comment": "No common prefix, LCP is ''",
    },
    {
        "input": ["prefix", "prefixes"],
        "output": "prefix",
        "comment": "Longest common prefix of 'prefix' and 'prefixes' is 'prefix'",
    },
    {
        "input": ["longest", "longer"],
        "output": "longe",
        "comment": "Longest common prefix of 'longest' and 'longer' is 'longe'",
    },
]

answer = """
```Python
def longest_common_prefix(str1, str2):
    i = 0
    while i < len(str1) and i < len(str2) and str1[i] == str2[i]:
        i += 1
    return str1[:i]
```
"""
