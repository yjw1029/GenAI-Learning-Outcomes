description = """
## 计算税后商品价格
编写一个函数`calculate_taxed_prices(prices)`，该函数接受一个字典`prices`作为参数。字典中的键为商品名称，值为商品的原始价格。根据以下税率规则计算每个商品的税后价格，并返回一个新的字典，其中包含商品名称及其税后价格。税率规则如下：如果商品价格不超过10元，则税率为10%；如果商品价格超过10元，则税率为12%。（4 分）
"""

title = "计算税后商品价格（4 分）"
score = 4

knowledge = ["dict", "condition", "number"]

code_template = """
def calculate_taxed_prices(prices):
    # 你的代码
    return ...
"""

code_entrypoint = "calculate_taxed_prices"

validcases = [
    {
        "input": [{"book": 15.5, "pencil": 8, "notebook": 12}],
        "output": {"book": 17.36, "pencil": 8.8, "notebook": 13.44},
        "comment": "book的税后价格为15.5*1.12, pencil的税后价格为8*1.1, notebook的税后价格为12*1.12。",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"pen": 5, "eraser": 3}],
        "output": {"pen": 5.5, "eraser": 3.3},
        "comment": "商品价格不超过10元，税率为10%。",
    },
    {
        "input": [{"laptop": 1000, "phone": 500}],
        "output": {"laptop": 1120.0, "phone": 560.0},
        "comment": "商品价格超过10元，税率为12%。",
    },
    {
        "input": [{"water": 2, "chocolate": 15}],
        "output": {"water": 2.2, "chocolate": 16.8},
        "comment": "水的价格不超过10元，巧克力的价格超过10元。",
    },
    {"input": [{}], "output": {}, "comment": "空字典应返回空字典。"},
    {
        "input": [{"snack": 10}],
        "output": {"snack": 11.0},
        "comment": "商品价格等于10元，税率为10%。",
    },
]

answer = """
```Python
def calculate_taxed_prices(prices):
    taxed_prices = {}
    for item, price in prices.items():
        if price <= 10:
            tax_rate = 1.10
        else:
            tax_rate = 1.12
        taxed_prices[item] = round(price * tax_rate, 2)
    return taxed_prices
```
"""
