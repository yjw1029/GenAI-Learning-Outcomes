description = """
## Compare Prices Across Shops
Given a list `prices` and a product name `product`. `prices[i]` is a dict for shop i, where keys are product names and values are prices. Write `find_lowest_price(prices, product)` to return the lowest price for `product`. Some shops may not have `product`. (4 pts)
"""

title = "Compare Prices Across Shops (4 pts)"
score = 4

knowledge = ["loop", "condition", "list", "dict"]

code_template = """
def find_lowest_price(prices, product):
    # your code
    return ...
"""

code_entrypoint = "find_lowest_price"

validcases = [
    {
        "input": [[{"apple": 50, "banana": 20}, {"apple": 60, "orange": 30}], "apple"],
        "output": 50,
        "comment": "Apple is cheapest in the first shop at 50",
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
        "comment": "Banana is cheapest in the second shop at 100",
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
        "comment": "Apple is cheapest in the third shop at 60",
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
        "comment": "Orange is cheapest in the third shop at 20",
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
        "comment": "Grape is cheapest in the third shop at 50",
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
        "comment": "Melon price in the first shop is 60",
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
        "comment": "Apple is cheapest in the first shop at 300",
    },
]

answer = """
```Python
def find_lowest_price(prices, product):
    # Initialize lowest price as None
    lowest_price = None

    # Iterate over each shop price list
    for price_list in prices:
        # Check if the shop has the product
        if product in price_list:
            # Get the product price
            price = price_list[product]
            # Update the lowest price
            if lowest_price is None or price < lowest_price:
                lowest_price = price
    return lowest_price
```
"""
