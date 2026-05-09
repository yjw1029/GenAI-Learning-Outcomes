description = """
## 所有学生是否及格
编写一个函数`are_students_passing(grades)`，它接受一个包含学生名字和成绩的字典`grades`作为参数。返回一个新字典，其中包含每位学生的名字及其是否及格（成绩大于或等于60分为True，否则为False）。（2 分）
"""

title = "所有学生是否及格（2 分）"
score = 2

knowledge = ["dict", "condition"]

code_template = """
def are_students_passing(grades):
    # 你的代码
    return ...
"""

code_entrypoint = "are_students_passing"

validcases = [
    {
        "input": [{"Alice": 58, "Bob": 72, "Charlie": 49}],
        "output": {"Alice": False, "Bob": True, "Charlie": False},
        "comment": "Alice和Charlie不及格，Bob及格",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"Dan": 90, "Eve": 100, "Frank": 65}],
        "output": {"Dan": True, "Eve": True, "Frank": True},
        "comment": "所有学生都及格",
    },
    {"input": [{"Gina": 59}], "output": {"Gina": False}, "comment": "Gina不及格"},
    {
        "input": [{"Harry": 60, "Ian": 59}],
        "output": {"Harry": True, "Ian": False},
        "comment": "Harry及格，Ian不及格",
    },
    {"input": [{"Jack": 0}], "output": {"Jack": False}, "comment": "Jack不及格"},
    {"input": [{"Kim": 100}], "output": {"Kim": True}, "comment": "Kim及格"},
    {
        "input": [{"Leo": 58, "Mia": 72, "Nina": 49, "Oscar": 60}],
        "output": {"Leo": False, "Mia": True, "Nina": False, "Oscar": True},
        "comment": "Mia和Oscar及格，Leo和Nina不及格",
    },
]

answer = """
```Python
def are_students_passing(grades):
    passing = {}
    for student in grades:
        passing[student] = grades[student] >= 60
    return passing
```
"""
