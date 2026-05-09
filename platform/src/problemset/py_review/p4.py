description = """
## 列表是否为空
编写一个函数 `is_list_empty(lst)`，它接受一个列表作为参数，并返回一个布尔值，表示该列表是否为空。（1 分）
"""

title = "列表是否为空 (1分)"
score = 1

knowledge = ["list", "bool"]

code_template = """
def is_list_empty(lst):
    # 你的代码
    return ...
"""

code_entrypoint = "is_list_empty"

validcases = [
    {"input": [[]], "output": True, "comment": "空列表应该返回True"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[1, 2, 3]], "output": False, "comment": "非空列表应该返回False"},
    {"input": [[0]], "output": False, "comment": "只有一个元素的列表也是非空的"},
    {"input": [[[], []]], "output": False, "comment": "包含空列表的列表不是空列表"},
    {"input": [[None]], "output": False, "comment": "包含None的列表不是空列表"},
    {"input": [[""]], "output": False, "comment": "包含空字符串的列表不是空列表"},
]

answer = """
```Python
def is_list_empty(lst):
    return len(lst) == 0
```
"""
