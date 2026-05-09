description = """
## 货比n家
给你一个列表`prices`和一个商品名称`product`。`prices[i]`是一个字典，表示第`i`个商家的价目表，其中键是商品名称，值是商品价格。请编写一个函数`find_lowest_price(prices, product)`，找出并返回`product`最低的价格。注意，有的商家可能没有`product`。 （4分）
"""

title = "货比n家 (4分)"
score = 4

knowledge = ["loop", "condition", "list", "dict"]

code_template = """
def find_lowest_price(prices, product):
    # 你的代码
    return ...
"""

code_entrypoint = "find_lowest_price"

validcases = [
    {
        "input": [[{"apple": 50, "banana": 20}, {"apple": 60, "orange": 30}], "apple"],
        "output": 50,
        "comment": "苹果在第一个商家的价格最低，为50",
    },
]

testcases = [
    *validcases,
    {
        "input": [
            [
                {"apple": 140, "banana": 120},
                {"apple": 130, "orange": 115, "banana": 100},
                {"apple": 150, "banana": 110},
            ],
            "banana",
        ],
        "output": 100,
        "comment": "香蕉在第二个商家的价格最低，为100",
    },
    {
        "input": [
            [
                {"apple": 95, "banana": 85},
                {"banana": 80, "apple": 90, "orange": 75},
                {"banana": 70, "orange": 65, "apple": 60},
            ],
            "apple",
        ],
        "output": 60,
        "comment": "苹果在第三个商家的价格最低，为60",
    },
    {
        "input": [
            [
                {"apple": 45, "banana": 35, "orange": 25},
                {"banana": 40, "orange": 30, "apple": 50},
                {"orange": 20, "grape": 15},
            ],
            "orange",
        ],
        "output": 20,
        "comment": "橙子在第三个商家的价格最低，为20",
    },
    {
        "input": [
            [
                {"apple": 200, "banana": 180, "orange": 160},
                {"banana": 150, "grape": 130, "apple": 110},
                {"watermelon": 90, "melon": 70, "grape": 50},
            ],
            "grape",
        ],
        "output": 50,
        "comment": "葡萄在第三个商家的价格最低，为50",
    },
    {
        "input": [
            [
                {
                    "apple": 10,
                    "banana": 20,
                    "orange": 30,
                    "grape": 40,
                    "watermelon": 50,
                    "melon": 60,
                }
            ],
            "melon",
        ],
        "output": 60,
        "comment": "哈密瓜在第一个商家的价格是60",
    },
    {
        "input": [
            [
                {"apple": 300, "banana": 400, "orange": 500, "grape": 600},
                {"banana": 350, "grape": 450, "orange": 550, "apple": 650},
            ],
            "apple",
        ],
        "output": 300,
        "comment": "苹果在第一个商家的价格最低，为300",
    },
]

answer = """
```Python
def find_lowest_price(prices, product):
    # 初始化最低价格为None
    lowest_price = None

    # 遍历每个商家的价格表
    for price_list in prices:
        # 检查该商家是否有指定的商品
        if product in price_list:
            # 获取商品价格
            price = price_list[product]
            # 更新最低价格
            if lowest_price is None or price < lowest_price:
                lowest_price = price
    return lowest_price
```
"""
