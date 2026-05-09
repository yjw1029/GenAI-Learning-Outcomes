description = """
## 生成星号字符串
编写一个函数`make_star_strings(nums)`，它接受一个非负整数列表`nums`作为参数，并返回一个字符串列表，其中每个字符串由星号（*）组成。每个字符串的星号数量对应输入列表中的相应数字。注意，输入列表中的零应产生一个空字符串（即零个星号的字符串）。（2 分）
"""

title = "生成星号字符串（2 分）"
score = 2

knowledge = ["list", "string"]

code_template = """
def make_star_strings(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "make_star_strings"

validcases = [
    {
        "input": [[2, 1, 3, 0]],
        "output": ["**", "*", "***", ""],
        "comment": "每个数字对应相应数量的星号，0对应空字符串",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[5, 2, 0, 1]],
        "output": ["*****", "**", "", "*"],
        "comment": "星号数量分别对应5, 2, 0, 1",
    },
    {
        "input": [[0, 0, 0]],
        "output": ["", "", ""],
        "comment": "全0列表返回空字符串列表",
    },
    {
        "input": [[1, 1, 1, 1]],
        "output": ["*", "*", "*", "*"],
        "comment": "每个数字都是1，返回相同数量的星号字符串",
    },
    {
        "input": [[10]],
        "output": ["**********"],
        "comment": "单个数字10，返回10个星号的字符串",
    },
    {
        "input": [[4, 0, 5]],
        "output": ["****", "", "*****"],
        "comment": "包含0和其他数字，返回正确数量的星号字符串和空字符串",
    },
]

answer = """
```Python
def make_star_strings(nums):
    nl = []
    for i in nums:
        nl.append("*" * i)
    return nl
```
"""
