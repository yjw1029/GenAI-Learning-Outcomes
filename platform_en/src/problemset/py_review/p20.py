description = """
## Chinese Zodiac
Write a function `chinese_zodiac(year)` that takes a year and returns its Chinese zodiac animal. The zodiac order is fixed, starting from "鼠", with 12 animals: ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]. The zodiac cycles every 12 years. For example, 2020 is 鼠, so 2021 is 牛, and so on. (3 pts)
"""

title = "Chinese Zodiac (3 pts)"
score = 3

knowledge = ["number", "condition"]

code_template = """
def chinese_zodiac(year):
    # your code
    return ...
"""

code_entrypoint = "chinese_zodiac"

validcases = [
    {
        "input": [2020],
        "output": "鼠",
        "comment": "2020 is the Rat year because the cycle starts with '鼠'.",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [2021], "output": "牛", "comment": "2021 is the Ox year."},
    {"input": [2022], "output": "虎", "comment": "2022 is the Tiger year."},
    {"input": [2023], "output": "兔", "comment": "2023 is the Rabbit year."},
    {"input": [2019], "output": "猪", "comment": "2019 is the Pig year, the last in the cycle."},
    {"input": [2008], "output": "鼠", "comment": "2008 is the Rat year, a 12-year cycle."},
    {"input": [1997], "output": "牛", "comment": "1997 is the Ox year."},
]

answer = """
```Python
def chinese_zodiac(year):
    animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    index = (year - 2020) % 12
    return animals[index]
```
"""
