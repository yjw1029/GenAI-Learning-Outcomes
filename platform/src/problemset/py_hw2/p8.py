description = """
## 判断字符串两半是否相似

设计一个函数`are_halves_similar(s)`, 传入一个偶数长度的字符串 `s`。将其拆分成长度相同的两半，前一半为 `a`，后一半为 `b`。

两个字符串 **相似** 的前提是它们含有的元音数目总数相同`('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U')`。注意，`s` 可能同时含有大写和小写字母。

如果`a`和`b`相似，返回 `True`；否则，返回 `False`。（5 分）
"""

title = "判断字符串两半是否相似 (5分)"
score = 5

knowledge = ["number", "string", "condition", "loop"]

code_template = """
def are_halves_similar(s):
    # 你的代码
    return ...
"""

code_entrypoint = "are_halves_similar"

validcases = [
    {
        "input": ["bookkeeper"],
        "output": False,
        "comment": "前半部分有2个元音，后半部分有3个",
    },
]

testcases = [
    *validcases,
    {
        "input": ["bookkeeper"],
        "output": False,
        "comment": "前半部分有2个元音，后半部分有3个",
    },
    {"input": ["AaBbCc"], "output": False, "comment": "后半部分都没有元音"},
    {
        "input": ["HelloWorld"],
        "output": False,
        "comment": "前半部分有2个元音，后半部分有1个",
    },
    {"input": ["AbCdEfGh"], "output": True, "comment": "前后半部分元音数相同"},
    {"input": ["eeEEOOoo"], "output": True, "comment": "前后半部分元音数相同"},
    {"input": ["aeiobcDEIO"], "output": False, "comment": "前后半部分元音数不同"},
    {
        "input": ["bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"],
        "output": True,
        "comment": "前后半部分都没有元音",
    },
    {"input": ["abcd1234efgh5678"], "output": True, "comment": "前后半部分都有1个元音"},
    {"input": ["ae"], "output": True, "comment": "前后半部分元音数相同"},
    {"input": ["ab"], "output": False, "comment": "前后半部分元音数不同"},
]
answer = ""
