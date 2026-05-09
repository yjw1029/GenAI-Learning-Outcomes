description = """
## 平方数字典
设计一个函数`square_dict(n)`，生成并返回一个包含`n`个元素的字典，其中字典的键值为0到`n-1`，每键对应的值为该键的平方。字典顺序需要从0到`n-1`。（2 分）
"""

title = "平方数字典 (2分)"
score = 2

knowledge = ["dict", "loop"]

code_template = """
def square_dict(n):
    # 你的代码
    return ...
"""

code_entrypoint = "square_dict"

validcases = [
    {
        "input": 3,
        "output": {0: 0, 1: 1, 2: 4},
        "comment": "字典键从0到2，值为每个键的平方",
    },
]

testcases = [
    *validcases,
    {
        "input": 5,
        "output": {0: 0, 1: 1, 2: 4, 3: 9, 4: 16},
        "comment": "字典键从0到4，值为每个键的平方",
    },
    {"input": 1, "output": {0: 0}, "comment": "字典键仅为0"},
    {"input": 0, "output": {}, "comment": "没有键值对"},
    {
        "input": 10,
        "output": {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36, 7: 49, 8: 64, 9: 81},
        "comment": "字典键从0到9，值为每个键的平方",
    },
]
answer = ""
