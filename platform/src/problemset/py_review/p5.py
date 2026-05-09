description = """
## 合并两个列表
编写一个函数`merge_lists(list1, list2)`，它接受两个列表作为参数，并返回一个新的列表，该列表包含两个输入列表的所有元素。（1 分）
"""

title = "合并两个列表（1 分）"
score = 1

knowledge = ["list"]

code_template = """
def merge_lists(list1, list2):
    # 你的代码
    return ...
"""

code_entrypoint = "merge_lists"

validcases = [
    {
        "input": [[1, 2, 3], [4, 5, 6]],
        "output": [1, 2, 3, 4, 5, 6],
        "comment": "合并[1, 2, 3]和[4, 5, 6]",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[], [1, 2, 3]],
        "output": [1, 2, 3],
        "comment": "一个空列表和一个非空列表",
    },
    {
        "input": [[1, 2, 3], []],
        "output": [1, 2, 3],
        "comment": "一个非空列表和一个空列表",
    },
    {"input": [[], []], "output": [], "comment": "两个空列表"},
    {
        "input": [[-1, -2, -3], [4, 5, 6]],
        "output": [-1, -2, -3, 4, 5, 6],
        "comment": "含负数的列表",
    },
    {
        "input": [[1, 2], [3, 4, 5, 6]],
        "output": [1, 2, 3, 4, 5, 6],
        "comment": "不同长度的列表",
    },
    {
        "input": [["a", "b"], ["c", "d"]],
        "output": ["a", "b", "c", "d"],
        "comment": "字符串元素的列表",
    },
]

answer = """
```Python
def merge_lists(list1, list2):
    return list1 + list2
```
"""
