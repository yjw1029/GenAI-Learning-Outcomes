description = """
## 列表最大元素
设计一个函数`find_two_largest_numbers(lst)`返回传入的列表中最大和第二大的元素的值。传入列表长度均大于等于2。（3分）
"""

title = "列表最大元素 (3分)"
score = 3

knowledge = ["loop", "condition", "list", "number"]

code_template = """
def find_two_largest_numbers(lst):
    # 你的代码
    return ...
"""

code_entrypoint = "find_two_largest_numbers"

validcases = [
    {
        "input": [[1, 2, 3, 4, 5]],
        "output": (5, 4),
        "comment": "列表中最大的两个数是5和4",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[10, 20, 15, 12, 11, 50]],
        "output": (50, 20),
        "comment": "列表中最大的两个数是50和20",
    },
    {"input": [[3, 3, 3]], "output": (3, 3), "comment": "列表中所有元素相同"},
    {
        "input": [[-1, -3, -2, -4]],
        "output": (-1, -2),
        "comment": "列表中最大的两个数是-1和-2",
    },
    {"input": [[8, 10, 10]], "output": (10, 10), "comment": "列表中包含重复元素"},
    {"input": [[8, 10, 8]], "output": (10, 8), "comment": "列表中包含重复元素"},
    {"input": [[-1e9, 3, 1e9]], "output": (1e9, 3), "comment": "包含极大数值的列表"},
]
answer = ""
