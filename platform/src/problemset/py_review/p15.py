description = """
## 计算员工总工资
编写一个函数 calculate_total_salary(salaries)，它接受一个字典 salaries 作为参数，其中字典的键是员工名字，值是员工的工资（整数）。计算并返回所有员工工资的总和。（3 分）
"""

title = "计算员工总工资（3 分）"
score = 3

knowledge = ["dict", "loop"]

code_template = """
def calculate_total_salary(salaries):
    # 你的代码
    return ...
"""

code_entrypoint = "calculate_total_salary"

validcases = [
    {
        "input": [{"Alice": 30000, "Bob": 25000, "Charlie": 28000}],
        "output": 83000,
        "comment": "总工资为 30000 + 25000 + 28000 = 83000",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"Tom": 50000, "Jerry": 40000}],
        "output": 90000,
        "comment": "总工资为 50000 + 40000 = 90000",
    },
    {"input": [{"Anna": 60000}], "output": 60000, "comment": "只有一名员工的情况"},
    {
        "input": [{"Bob": 25000, "Charlie": 28000, "Dave": 32000}],
        "output": 85000,
        "comment": "总工资为 25000 + 28000 + 32000 = 85000",
    },
    {
        "input": [
            {},
        ],
        "output": 0,
        "comment": "空字典的情况",
    },
    {
        "input": [{"Lily": 30000, "Rose": 70000, "Daisy": 40000}],
        "output": 140000,
        "comment": "总工资为 30000 + 70000 + 40000 = 140000",
    },
]

answer = """
```Python
def calculate_total_salary(salaries):
    total_salary = 0
    for key in salaries:
        total_salary += salaries[key]
    return total_salary
```
"""
