description = """
## 数字字符替换
编写一个函数`replace_digits_with_count(s)`，它接受一个字符串`s`作为参数。该函数需要将字符串中的每个数字字符替换为该数字字符后面紧跟的数字个数。例如，对于字符串 `"a3b2c4d"`，替换后的字符串应为 `"a333b22c4444d"`。（4 分）
"""

title = "数字字符替换（4 分）"
score = 4

knowledge = ["string", "loop", "condition"]

code_template = """
def replace_digits_with_count(s):
    # 你的代码
    return ...
"""

code_entrypoint = "replace_digits_with_count"

validcases = [
    {
        "input": ["a3b2c4d"],
        "output": "a333b22c4444d",
        "comment": "每个数字字符被替换为相应数量的重复字符",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["x5y0z2"],
        "output": "x55555yz22",
        "comment": "5被替换为5个5，0不增加字符，2被替换为2个2",
    },
    {
        "input": ["123"],
        "output": "122333",
        "comment": "1后面没有数字，2后面跟了2个2，3后面跟了3个3",
    },
    {
        "input": ["no digits"],
        "output": "no digits",
        "comment": "没有数字字符，不做替换",
    },
    {"input": ["9"], "output": "999999999", "comment": "9被替换为9个9"},
    {"input": [""], "output": "", "comment": "空字符串"},
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
