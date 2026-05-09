description = """
## 奇偶顺序数组
编写一个函数 `order_odd_even(nums)`，对数组 `nums` 进行重新排序，使得所有的奇数位于偶数之前，并且保持原有的相对顺序不变。（3 分）
"""

title = "奇偶顺序数组（3 分）"
score = 3

knowledge = ["list", "loop"]

code_template = """
def order_odd_even(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "order_odd_even"

validcases = [
    {
        "input": [[3, 1, 2, 4]],
        "output": [3, 1, 2, 4],
        "comment": "输出数组中的奇数3, 1在偶数2, 4前面，且保持了原有的相对顺序。",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[1, 2, 3, 4, 5, 6]],
        "output": [1, 3, 5, 2, 4, 6],
        "comment": "奇数1, 3, 5在偶数2, 4, 6前面，保持原有顺序。",
    },
    {
        "input": [[10, 20, 30, 40]],
        "output": [10, 20, 30, 40],
        "comment": "全为偶数，顺序不变。",
    },
    {"input": [[5, 7, 9]], "output": [5, 7, 9], "comment": "全为奇数，顺序不变。"},
    {
        "input": [[8, 1, 3, 6, 5]],
        "output": [1, 3, 5, 8, 6],
        "comment": "奇数1, 3, 5在偶数8, 6前面，保持原有顺序。",
    },
    {
        "input": [[2, 4, 6, 8, 3, 1, 5, 7]],
        "output": [3, 1, 5, 7, 2, 4, 6, 8],
        "comment": "奇数3, 1, 5, 7在偶数2, 4, 6, 8前面，保持原有顺序。",
    },
    {
        "input": [[0, 2, 4, 6, 8]],
        "output": [0, 2, 4, 6, 8],
        "comment": "全为偶数，包括0，顺序不变。",
    },
]

answer = """
```Python
def order_odd_even(nums):
    odd = []
    even = []
    for x in nums:
        if x % 2 == 1:
            odd.append(x)
        else:
            even.append(x)
    return odd + even
```
"""
