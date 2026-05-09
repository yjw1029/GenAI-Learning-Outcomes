description = """
## Pop and Return Value
Write a function `pop_and_return_value(my_dict, key)` that takes a dictionary `my_dict` and a key `key`. The function should remove the key-value pair and return the value. (1 pts)
"""

title = "Pop and Return Value (1 pts)"
score = 1

knowledge = ["dict"]

code_template = """
def pop_and_return_value(my_dict, key):
    # your code
    return ...
"""

code_entrypoint = "pop_and_return_value"

validcases = [
    {
        "input": [{"apple": 3, "banana": 2}, "apple"],
        "output": 3,
        "comment": "Remove key 'apple' and return value 3",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"apple": 3, "banana": 2, "cherry": 4}, "banana"],
        "output": 2,
        "comment": "Remove key 'banana' and return value 2",
    },
    {
        "input": [{"x": 10, "y": 20}, "x"],
        "output": 10,
        "comment": "Remove key 'x' and return value 10",
    },
    {
        "input": [{"first": 1, "second": 2}, "second"],
        "output": 2,
        "comment": "Remove key 'second' and return value 2",
    },
    {
        "input": [{"a": -1, "b": -2}, "a"],
        "output": -1,
        "comment": "Remove key 'a' and return value -1",
    },
    {
        "input": [{"hello": "world", "foo": "bar"}, "foo"],
        "output": "bar",
        "comment": "Remove key 'foo' and return value 'bar'",
    },
]

answer = """
```Python
def pop_and_return_value(my_dict, key):
    return my_dict.pop(key)
```
"""
