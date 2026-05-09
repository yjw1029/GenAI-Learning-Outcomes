description = """
## 雇员信息丢失

输入两个字典`employee_name`和`employee_salary`。`employee_name`的键为雇员的id，值为雇员的名字。`employee_salary`的键为雇员的id，值为雇员的薪水。编写一个函数`find_missing_info(employee_name, employee_salary)`找到信息丢失的雇员id（即有名字信息但薪水信息丢失，或有薪水信息但名字信息丢失的雇员id）。返回职员id的列表，按照职员id排序。（4分）

提示：使用`nums.sort()`可以对列表进行排序。例如,
```python
nums = [1, 3, 2, 4]
nums.sort()
print(nums) # [1, 2, 3, 4]
```

注意`sort`方法没有返回值
"""

title = "雇员信息丢失 (4分)"
score = 4

code_template = """
def find_missing_info(employee_name, employee_salary):
    # 你的代码
    return ...
"""

knowledge = ["dict", "loop", "condition", "bool"]

code_entrypoint = "find_missing_info"

validcases = [
    {
        "input": [{1: "Alice", 2: "Bob", 3: "Charlie"}, {1: 50000, 2: 60000}],
        "output": [3],
        "comment": "Charlie's salary info is missing",
    },
]

testcases = [
    *validcases,
    {
        "input": [{1: "Alice", 2: "Bob"}, {1: 50000, 2: 60000, 3: 70000}],
        "output": [3],
        "comment": "Employee with ID 3 has salary info but no name info",
    },
    {
        "input": [{1: "Alice", 2: "Bob", 3: "Charlie"}, {1: 50000, 2: 60000, 3: 70000}],
        "output": [],
        "comment": "All employees have both name and salary info",
    },
    {
        "input": [{1: "Alice", 2: "Bob", 4: "David"}, {1: 50000, 3: 70000, 4: 80000}],
        "output": [2, 3],
        "comment": "Bob's salary info and employee with ID 3's name info are missing",
    },
    {
        "input": [{}, {1: 50000}],
        "output": [1],
        "comment": "No name info for the employee with salary info",
    },
    {
        "input": [{2: "Bob"}, {}],
        "output": [2],
        "comment": "No salary info for Bob",
    },
    {
        "input": [{}, {}],
        "output": [],
        "comment": "Both dictionaries are empty, no missing info",
    },
    {
        "input": [{1: "Alice", 3: "Charlie"}, {2: "David", 3: 70000}],
        "output": [1, 2],
        "comment": "Alice's salary info and David's name info are missing",
    },
]
answer = ""
