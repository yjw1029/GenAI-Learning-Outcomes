description = """
## 计算字符出现频率
编写一个函数`char_frequency(s)`，它接受一个字符串作为参数，并返回一个字典。该字典显示字符串中每个字符的出现次数，并保持字典中的键在原字符串中的出现顺序。（3分）
"""

title = "计算字符出现频率 (3分)"
score = 3

knowledge = ["string", "dict"]

code_template = """
def char_frequency(s):
    # 你的代码
    return ...
"""

code_entrypoint = "char_frequency"

validcases = [
    {
        "input": "hello",
        "output": {"h": 1, "e": 1, "l": 2, "o": 1},
        "comment": "普通案例",
    },
]

testcases = [
    *validcases,
    {"input": "aabbcc", "output": {"a": 2, "b": 2, "c": 2}, "comment": "重复字符"},
    {"input": "", "output": {}, "comment": "空字符串"},
    {
        "input": "abcd",
        "output": {"a": 1, "b": 1, "c": 1, "d": 1},
        "comment": "无重复字符",
    },
    {"input": "aAaAaA", "output": {"a": 3, "A": 3}, "comment": "区分大小写"},
    {"input": "123321", "output": {"1": 2, "2": 2, "3": 2}, "comment": "数字字符"},
    {"input": "ab!ab!", "output": {"a": 2, "b": 2, "!": 2}, "comment": "包含特殊字符"},
]

answer = """
```Python
def char_frequency(s):
	frequency = {}
	for char in s:
		if char not in frequency:
			frequency[char] = 0
		frequency[char] += 1
	return frequency
```
"""
