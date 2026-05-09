description = """
## 字符串最长公共前缀
编写一个函数`longest_common_prefix(str1, str2)`，它接受两个字符串作为参数，并返回它们的最长公共前缀。（4 分）
"""

title = "字符串最长公共前缀（4 分）"
score = 4

knowledge = ["string", "loop"]

code_template = """
def longest_common_prefix(str1, str2):
    # 你的代码
    return ...
"""

code_entrypoint = "longest_common_prefix"

validcases = [
    {
        "input": ["flower", "flow"],
        "output": "flow",
        "comment": "'flower' 和 'flow' 的最长公共前缀是 'flow'",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["class", "classes"],
        "output": "class",
        "comment": "'class' 和 'classes' 的最长公共前缀是 'class'",
    },
    {
        "input": ["abc", "abcd"],
        "output": "abc",
        "comment": "'abc' 和 'abcd' 的最长公共前缀是 'abc'",
    },
    {
        "input": ["", "abc"],
        "output": "",
        "comment": "一个为空字符串，最长公共前缀是 ''",
    },
    {
        "input": ["abc", "def"],
        "output": "",
        "comment": "没有公共前缀，最长公共前缀是 ''",
    },
    {
        "input": ["prefix", "prefixes"],
        "output": "prefix",
        "comment": "'prefix' 和 'prefixes' 的最长公共前缀是 'prefix'",
    },
    {
        "input": ["longest", "longer"],
        "output": "longe",
        "comment": "'longest'和'longer'的最长公共前缀是'longe'",
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
