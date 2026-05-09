description = """
## 字符串长度
设计一个函数`string_length(s)`，返回传入字符串的长度。（1分）
"""

title = "字符串长度 (1分)"
score = 1

knowledge = ["string"]

code_template = """
def string_length(s):
    # 你的代码
    return ...
"""

code_entrypoint = "string_length"

validcases = [
    {"input": "hello", "output": 5, "comment": "'hello'的长度是5"},
]

testcases = [
    *validcases,
    # common cases
    {"input": "apple", "output": 5, "comment": "'apple'的长度是5"},
    {"input": "", "output": 0, "comment": "空字符串的长度是0"},
    {"input": "1234567890", "output": 10, "comment": "'1234567890'的长度是10"},
    {"input": "中文长度", "output": 4, "comment": "'中文长度'的长度是4"},
    {"input": "a b c", "output": 5, "comment": "'a b c'的长度是5，包括空格"},
]
answer = ""
