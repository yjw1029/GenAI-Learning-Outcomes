description = """
## Merge Strings
Write a function `merge_strings(word1, word2)` that takes two strings and merges them by alternating letters, starting with `word1`. If one string is longer, append the remaining letters to the end. Return the merged string. (4 pts)
"""

title = "Merge Strings (4 pts)"
score = 4

knowledge = ["string", "loop"]

code_template = """
def merge_strings(word1, word2):
    # your code
    return ...
"""

code_entrypoint = "merge_strings"

validcases = [
    {
        "input": ["abc", "pqr"],
        "output": "apbqcr",
        "comment": "Merged alternately as 'apbqcr'",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["ab", "pqrs"],
        "output": "apbqrs",
        "comment": "Merged alternately as 'apbqrs'; word2 is longer so 'rs' is appended",
    },
    {
        "input": ["hello", "world"],
        "output": "hweolrllod",
        "comment": "Merged alternately as 'hweolrllod'",
    },
    {
        "input": ["", "abc"],
        "output": "abc",
        "comment": "One string empty, return the other",
    },
    {
        "input": ["abc", ""],
        "output": "abc",
        "comment": "One string empty, return the other",
    },
    {"input": ["123", "456"], "output": "142536", "comment": "Alternate merge for numeric strings"},
]

answer = """
```Python
def merge_strings(word1, word2):
    result = ""
    len1, len2 = len(word1), len(word2)
    for i in range(max(len1, len2)):
        if i < len1:
            result += word1[i]
        if i < len2:
            result += word2[i]
    return result
```
"""
