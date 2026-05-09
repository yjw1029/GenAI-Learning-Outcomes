description = """
## 删除并返回键
编写一个函数`pop_and_return_value(my_dict, key)`，它接受一个字典`my_dict`和一个键`key`作为参数。该函数需要删除字典中的这个键值对，并返回该键对应的值。（1 分）
"""

title = "删除并返回键（1 分）"
score = 1

knowledge = ["dict"]

code_template = """
def pop_and_return_value(my_dict, key):
    # 你的代码
    return ...
"""

code_entrypoint = "pop_and_return_value"

validcases = [
    {
        "input": [{"apple": 3, "banana": 2}, "apple"],
        "output": 3,
        "comment": "删除键 'apple' 并返回其值 3",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"apple": 3, "banana": 2, "cherry": 4}, "banana"],
        "output": 2,
        "comment": "删除键 'banana' 并返回其值 2",
    },
    {
        "input": [{"x": 10, "y": 20}, "x"],
        "output": 10,
        "comment": "删除键 'x' 并返回其值 10",
    },
    {
        "input": [{"first": 1, "second": 2}, "second"],
        "output": 2,
        "comment": "删除键 'second' 并返回其值 2",
    },
    {
        "input": [{"a": -1, "b": -2}, "a"],
        "output": -1,
        "comment": "删除键 'a' 并返回其值 -1",
    },
    {
        "input": [{"hello": "world", "foo": "bar"}, "foo"],
        "output": "bar",
        "comment": "删除键 'foo' 并返回其值 'bar'",
    },
]

answer = """
```Python
def pop_and_return_value(my_dict, key):
    return my_dict.pop(key)
```
"""
