description = """
## 出租车计费
编写一个函数 `calculate_taxi_fare(distance, waiting_time, time_of_day)`，它接受行驶距离（公里）、等待时间（分钟）和时间段（"day" 或 "night"）作为参数，并根据以下计价标准计算出租车费用，返回总费用。（5 分）
计价标准：
- 在“day”时间段（白天），起步价为10元，包含首3公里。
- 在“night”时间段（夜晚），起步价为13元，包含首3公里。
- 白天超出起步距离后，每公里收费2元；夜间每公里收费2.5元。
- 等待时间收费：每分钟0.5元，不分白天夜晚。
"""

title = "出租车计费（5 分）"
score = 5

knowledge = ["number", "condition"]

code_template = """
def calculate_taxi_fare(distance, waiting_time, time_of_day):
    # 你的代码
    return ...
"""

code_entrypoint = "calculate_taxi_fare"

validcases = [
    {
        "input": [5, 2, "day"],
        "output": 15.0,
        "comment": "白天时，5公里和2分钟等待的费用",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [5, 2, "night"],
        "output": 19.0,
        "comment": "夜晚时，5公里和2分钟等待的费用",
    },
    {
        "input": [2, 3, "day"],
        "output": 11.5,
        "comment": "白天时，2公里和3分钟等待的费用",
    },
    {
        "input": [2, 3, "night"],
        "output": 14.5,
        "comment": "夜晚时，2公里和3分钟等待的费用",
    },
    {
        "input": [10, 10, "day"],
        "output": 29.0,
        "comment": "白天时，10公里和10分钟等待的费用",
    },
    {
        "input": [10, 10, "night"],
        "output": 35.5,
        "comment": "夜晚时，10公里和10分钟等待的费用",
    },
]

answer = """
```Python
def calculate_taxi_fare(distance, waiting_time, time_of_day):
    if time_of_day == "day":
        fare = 10  # 白天起步价
        extra_per_km = 2  # 白天超出起步价每公里费用
    else:
        fare = 13  # 夜间起步价
        extra_per_km = 2.5  # 夜间超出起步价每公里费用

    if distance > 3:
        fare += (distance - 3) * extra_per_km
    fare += waiting_time * 0.5  # 等待时间费用

    return fare
```
"""
