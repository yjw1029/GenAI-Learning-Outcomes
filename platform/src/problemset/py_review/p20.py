description = """
## 计算生肖
编写一个函数 `chinese_zodiac(year)`，它接受一个年份 `year` 作为参数，并返回该年份对应的中国生肖。生肖的顺序是固定的，从 "鼠" 开始，共有12个，分别是：["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]。生肖与年份之间有一个周期性的关系，每12年一个循环。例如，2020年是鼠年，那么2021年是牛年，以此类推。（3 分）
"""

title = "计算生肖（3 分）"
score = 3

knowledge = ["number", "condition"]

code_template = """
def chinese_zodiac(year):
    # 你的代码
    return ...
"""

code_entrypoint = "chinese_zodiac"

validcases = [
    {
        "input": [2020],
        "output": "鼠",
        "comment": "2020年是鼠年，因为生肖循环的起点是 '鼠'。",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [2021], "output": "牛", "comment": "2021年是牛年。"},
    {"input": [2022], "output": "虎", "comment": "2022年是虎年。"},
    {"input": [2023], "output": "兔", "comment": "2023年是兔年。"},
    {"input": [2019], "output": "猪", "comment": "2019年是猪年，生肖循环的最后一个。"},
    {"input": [2008], "output": "鼠", "comment": "2008年是鼠年，12年一个周期。"},
    {"input": [1997], "output": "牛", "comment": "1997年是牛年。"},
]

answer = """
```Python
def chinese_zodiac(year):
    animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    index = (year - 2020) % 12
    return animals[index]
```
"""
