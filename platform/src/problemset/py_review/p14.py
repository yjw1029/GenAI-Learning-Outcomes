description = """
## 计数直到中断
编写一个函数`count_until_break(nums)`，它接受一个整数列表`nums`。函数应该计算列表中元素的个数，直到遇到数字`0`。一旦遇到`0`，函数应该停止计数并返回当前的计数值。（3 分）
"""

title = "计数直到中断（3 分）"
score = 3

knowledge = ["list", "loop"]

code_template = """
def count_until_break(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "count_until_break"

validcases = [
    {
        "input": [[1, 2, 3, 0, 4, 5]],
        "output": 3,
        "comment": "遇到0之前，列表中有3个元素",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[5, 4, 3, 2, 1, 0]],
        "output": 5,
        "comment": "遇到0之前，列表中有5个元素",
    },
    {"input": [[0, 1, 2, 3, 4]], "output": 0, "comment": "列表的第一个元素就是0"},
    {"input": [[1, 2, 3, 4, 5]], "output": 5, "comment": "列表中没有0，计算全部元素"},
    {
        "input": [[-1, -2, 0, 1, 2]],
        "output": 2,
        "comment": "遇到0之前，列表中有2个负数元素",
    },
    {"input": [[0]], "output": 0, "comment": "列表只有一个元素，且为0"},
    {"input": [[1, 0, 0, 0]], "output": 1, "comment": "遇到第一个0之后就停止计数"},
]

answer = """
```Python
def count_until_break(nums):
    count = 0
    for num in nums:
        if num == 0:
            break
        count += 1
    return count
```
"""
