description = """
## 列表计数
编写一个函数`count_elements(lst)`，它接受一个列表作为参数，并返回列表中元素的数量。（1 分）
"""

title = "列表计数（1 分）"
score = 1
knowledge = ["list"]

code_template = """
def count_elements(lst):
    # 你的代码
    return ...
"""

code_entrypoint = "count_elements"

validcases = [
    {
        "input": [["apple", "banana", "cherry"]],
        "output": 3,
        "comment": "列表中有3个元素",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[]], "output": 0, "comment": "空列表"},
    {"input": [["orange"]], "output": 1, "comment": "列表中有1个元素"},
    {"input": [["apple", "banana"]], "output": 2, "comment": "列表中有2个元素"},
    {
        "input": [["dog", "cat", "bird", "fish"]],
        "output": 4,
        "comment": "列表中有4个元素",
    },
    {
        "input": [["a", "b", "c", "d", "e", "f", "g"]],
        "output": 7,
        "comment": "列表中有7个元素",
    },
]

answer = """
```Python
def count_elements(lst):
    return len(lst)
```
"""
