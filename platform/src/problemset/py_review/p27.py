description = """
## 合并字符串
编写一个函数`merge_strings(word1, word2)`，它接受两个字符串`word1`和`word2`作为参数。函数应从`word1`开始，通过交替添加每个字符串的字母来合并这两个字符串。如果一个字符串比另一个字符串长，就将多出来的字母追加到合并后字符串的末尾。返回合并后的字符串。（4 分）
"""

title = "合并字符串（4 分）"
score = 4

knowledge = ["string", "loop"]

code_template = """
def merge_strings(word1, word2):
    # 你的代码
    return ...
"""

code_entrypoint = "merge_strings"

validcases = [
    {
        "input": ["abc", "pqr"],
        "output": "apbqcr",
        "comment": "字符串交替合并为 'apbqcr'",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["ab", "pqrs"],
        "output": "apbqrs",
        "comment": "字符串交替合并为 'apbqrs'，由于word2比word1长，所以剩余的'rs'被添加到最后",
    },
    {
        "input": ["hello", "world"],
        "output": "hweolrllod",
        "comment": "字符串交替合并为 'hweolrllod'",
    },
    {
        "input": ["", "abc"],
        "output": "abc",
        "comment": "一个字符串为空，直接返回另一个字符串",
    },
    {
        "input": ["abc", ""],
        "output": "abc",
        "comment": "一个字符串为空，直接返回另一个字符串",
    },
    {"input": ["123", "456"], "output": "142536", "comment": "数字字符串交替合并"},
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
