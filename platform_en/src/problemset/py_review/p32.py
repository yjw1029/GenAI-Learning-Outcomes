description = """
## Taxi Fare
Write a function `calculate_taxi_fare(distance, waiting_time, time_of_day)` that takes distance (km), waiting time (minutes), and time of day ("day" or "night") and computes the fare using the rules below. (5 pts)
Pricing rules:
- In "day", the base fare is 10, including the first 3 km.
- In "night", the base fare is 13, including the first 3 km.
- After the base distance, daytime costs 2 per km; nighttime costs 2.5 per km.
- Waiting time costs 0.5 per minute in both day and night.
"""

title = "Taxi Fare (5 pts)"
score = 5

knowledge = ["number", "condition"]

code_template = """
def calculate_taxi_fare(distance, waiting_time, time_of_day):
    # your code
    return ...
"""

code_entrypoint = "calculate_taxi_fare"

validcases = [
    {
        "input": [5, 2, "day"],
        "output": 15.0,
        "comment": "Daytime fare for 5 km and 2 minutes waiting",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [5, 2, "night"],
        "output": 19.0,
        "comment": "Night fare for 5 km and 2 minutes waiting",
    },
    {
        "input": [2, 3, "day"],
        "output": 11.5,
        "comment": "Daytime fare for 2 km and 3 minutes waiting",
    },
    {
        "input": [2, 3, "night"],
        "output": 14.5,
        "comment": "Night fare for 2 km and 3 minutes waiting",
    },
    {
        "input": [10, 10, "day"],
        "output": 29.0,
        "comment": "Daytime fare for 10 km and 10 minutes waiting",
    },
    {
        "input": [10, 10, "night"],
        "output": 35.5,
        "comment": "Night fare for 10 km and 10 minutes waiting",
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
