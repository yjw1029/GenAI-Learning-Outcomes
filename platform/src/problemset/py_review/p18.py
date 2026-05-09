description = """
## 偶数索引元素乘积
编写一个函数`product_even_index(nums)`，它接受一个数字列表作为参数，并返回列表中所有偶数索引位置上元素的乘积。（3 分）
"""

title = "偶数索引元素乘积（3 分）"
score = 3

knowledge = ["list", "loop"]

code_template = """
def product_even_index(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "product_even_index"

validcases = [
    {
        "input": [[1, 3, 5, 7, 9]],
        "output": 45,
        "comment": "索引0, 2, 4的元素之乘积为1*5*9=45",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[2, 4, 6, 8, 10]],
        "output": 120,
        "comment": "索引0, 2, 4的元素之乘积为2*6*10=120",
    },
    {"input": [[3, 3, 3, 3]], "output": 9, "comment": "索引0, 2的元素之乘积为3*3=9"},
    {"input": [[10]], "output": 10, "comment": "只有索引0的元素，乘积为10"},
    {"input": [[1, 2]], "output": 1, "comment": "只有索引0的元素，乘积为1"},
    {
        "input": [[-2, 3, -4, 5, -6]],
        "output": -48,
        "comment": "索引0, 2, 4的元素之乘积为-2*(-4)*(-6)=-48",
    },
]

answer = """
```Python
def product_even_index(nums):
    product = 1
    for i in range(0, len(nums), 2):
        product *= nums[i]
    return product
```
"""
