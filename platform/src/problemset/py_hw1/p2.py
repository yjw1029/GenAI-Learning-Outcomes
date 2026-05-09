description = """
## 检查年份是否为闰年
编写一个函数 `is_leap_year(year)`，用于检查传入的年份是否为闰年。如果是闰年返回`True`，否则返回`False`。闰年的定义是：
- 年份能被4整除但不能被100整除；
- 或者年份能被400整除。（2 分）
"""

title = "检查年份是否为闰年 (2分)"
score = 2

code_template = """
def is_leap_year(year):
    # 你的代码
    return ...
"""

knowledge = ["number", "condition", "bool"]

code_entrypoint = "is_leap_year"

validcases = [
    {
        "input": 2000,
        "output": True,
        "comment": "2000 is a leap year because it is divisible by 400",
    },
]

testcases = [
    *validcases,
    {"input": 2001, "output": False, "comment": "2001 is not a leap year"},
    {
        "input": 1900,
        "output": False,
        "comment": "1900 is not a leap year because it is divisible by 100 but not by 400",
    },
    {
        "input": 2004,
        "output": True,
        "comment": "2004 is a leap year because it is divisible by 4 but not by 100",
    },
    {
        "input": 2100,
        "output": False,
        "comment": "2100 is not a leap year because it is divisible by 100 but not by 400",
    },
    {
        "input": 1600,
        "output": True,
        "comment": "1600 is a leap year because it is divisible by 400",
    },
    {"input": 2024, "output": True, "comment": "2024 is a leap year"},
    {"input": 2023, "output": False, "comment": "2023 is not a leap year"},
]

answer = """
```Python
def is_leap_year(year):
	if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
		return True
	else:
		return False
```
"""
