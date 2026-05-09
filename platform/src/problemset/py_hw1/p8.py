description = """
## 学生分数的最小差值
给定一个下标从0开始的整数列表`nums`，其中`nums[i]`表示第`i`名学生的分数。另给你一个整数`k`。编写一个函数`min_difference(nums, k)`，从数组中选出任意`k`名学生的分数，使这`k`个分数间最高分和最低分的差值达到最小化。返回这个最小的差值。（5分）

提示：使用`nums.sort()`可以对列表进行排序。例如,
```python
nums = [1, 3, 2, 4]
nums.sort()
print(nums) # [1, 2, 3, 4]
```

注意`sort`方法没有返回值
"""

title = "学生分数的最小差值 (5分)"
score = 5

code_template = """
def min_difference(nums, k):
    # 你的代码
    return ...
"""

knowledge = ["number", "list", "loop", "condition", "bool"]

code_entrypoint = "min_difference"

validcases = [
    {
        "input": [[30, 55, 70, 85, 50], 3],
        "output": 20,
        "comment": "选择子数组 [55, 50, 70]，它们的最大最小差值为 20",
    },
]

testcases = [
    *validcases,
    {
        "input": [[45, 70, 85, 32, 60], 2],
        "output": 10,
        "comment": "选择子数组 [70, 60]，差值为 10",
    },
    {
        "input": [[100, 95, 90, 85, 80], 4],
        "output": 15,
        "comment": "选择子数组 [95, 90, 85, 80]，它们的最大最小差值为 15",
    },
    {
        "input": [[22, 27, 23, 25, 24], 5],
        "output": 5,
        "comment": "子数组涵盖整个列表，差值为 5",
    },
    {
        "input": [[77, 77, 77, 77, 77], 3],
        "output": 0,
        "comment": "所有分数相同，差值为 0",
    },
    {
        "input": [[60], 1],
        "output": 0,
        "comment": "单个元素的列表，差值为 0",
    },
    {
        "input": [[33, 67, 90, 45, 21], 2],
        "output": 12,
        "comment": "最小差值出现在子数组 [33, 21] 中，差值为 22",
    },
]

answer = """
```Python
def min_difference(nums, k):
    # 如果k为1或者nums为空，则最小差值为0
    if k <= 1 or not nums:
        return 0

    # 对nums进行排序
    nums.sort()

    # 初始化最小差值为无穷大
    min_diff = None

    # 遍历数组，寻找k个连续数的最小差值
    for i in range(len(nums) - k + 1):
        diff = nums[i + k - 1] - nums[i]
        if min_diff is None:
            min_diff = diff
        else:
            if diff < min_diff:
                min_diff = diff
    return min_diff
```
"""
