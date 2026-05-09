description = """
## 列表元素插入
设计一个函数 `insert_at_index(lst, element, index)`，它接受一个列表和两个整数：一个元素和一个正整数索引。函数应将元素插入到列表中指定的索引位置。如果索引超出列表的当前长度，将元素添加到列表的末尾。（2 分）
"""

title = "列表元素插入 (2分)"
score = 2

code_template = """
def insert_at_index(lst, element, index):
    # 你的代码
    return ...
"""

knowledge = ["list", "condition", "bool"]

code_entrypoint = "insert_at_index"

validcases = [
    {
        "input": [[1, 2, 3], 4, 1],
        "output": [1, 4, 2, 3],
        "comment": "Inserting 4 at index 1 in [1, 2, 3]",
    },
]

testcases = [
    *validcases,
    {
        "input": [[1, 2, 3], 5, 5],
        "output": [1, 2, 3, 5],
        "comment": "Index 5 exceeds the length of [1, 2, 3], so 5 is added at the end",
    },
    {
        "input": [[], 10, 0],
        "output": [10],
        "comment": "Inserting 10 at index 0 in an empty list",
    },
    {
        "input": [[1, 2, 3], 0, 3],
        "output": [1, 2, 3, 0],
        "comment": "Index 3 equals the length of [1, 2, 3], so 0 is added at the end",
    },
    {
        "input": [[1, 2, 3], 0, 0],
        "output": [0, 1, 2, 3],
        "comment": "Inserting 0 at index 0 in [1, 2, 3]",
    },
    {
        "input": [[1], 2, 1],
        "output": [1, 2],
        "comment": "Index 1 equals the length of [1], so 2 is added at the end",
    },
    {
        "input": [[1, 2, 3], 6, 10],
        "output": [1, 2, 3, 6],
        "comment": "Index 10 exceeds the length of [1, 2, 3], so 6 is added at the end",
    },
]

answer = """
```Python
def insert_at_index(lst, element, index):
	if index >= len(lst):
		lst.append(element)
	else:
		lst.insert(index, element)
	return lst
```
"""
