description = """
## 生成用户名
编写一个函数`generate_username(name, birth_year)`，它接受一个名字`name`和出生年份`birth_year`作为参数，并返回一个用户名。用户名由名字的首字母和出生年份的最后两位组成。（3 分）
"""

title = "生成用户名（3 分）"
score = 3

knowledge = ["string", "index"]

code_template = """
def generate_username(name, birth_year):
    # 你的代码
    return ...
"""

code_entrypoint = "generate_username"

validcases = [
    {
        "input": ["Alice", 1990],
        "output": "A90",
        "comment": "名字首字母为 'A'，年份最后两位为 '90'，组合得到用户名 'A90'",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": ["Bob", 1985],
        "output": "B85",
        "comment": "名字首字母为 'B'，年份最后两位为 '85'，组合得到用户名 'B85'",
    },
    {
        "input": ["Charlie", 2001],
        "output": "C01",
        "comment": "名字首字母为 'C'，年份最后两位为 '01'，组合得到用户名 'C01'",
    },
    {
        "input": ["Diana", 1999],
        "output": "D99",
        "comment": "名字首字母为 'D'，年份最后两位为 '99'，组合得到用户名 'D99'",
    },
    {
        "input": ["Eva", 2022],
        "output": "E22",
        "comment": "名字首字母为 'E'，年份最后两位为 '22'，组合得到用户名 'E22'",
    },
    {
        "input": ["Frank", 1980],
        "output": "F80",
        "comment": "名字首字母为 'F'，年份最后两位为 '80'，组合得到用户名 'F80'",
    },
]

answer = """
```Python
def generate_username(name, birth_year):
    return name[0] + str(birth_year)[-2:]
```
"""
