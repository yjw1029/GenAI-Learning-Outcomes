description = """
## Calculate Taxed Prices
Write a function `calculate_taxed_prices(prices)` that takes a dictionary `prices` of item names to original prices. Compute the taxed price using: if price <= 10, tax rate is 10%; if price > 10, tax rate is 12%. Return a new dictionary with taxed prices. (4 pts)
"""

title = "Calculate Taxed Prices (4 pts)"
score = 4

knowledge = ["dict", "condition", "number"]

code_template = """
def calculate_taxed_prices(prices):
    # your code
    return ...
"""

code_entrypoint = "calculate_taxed_prices"

validcases = [
    {
        "input": [{"book": 15.5, "pencil": 8, "notebook": 12}],
        "output": {"book": 17.36, "pencil": 8.8, "notebook": 13.44},
        "comment": "Taxed price: book 15.5*1.12, pencil 8*1.1, notebook 12*1.12.",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [{"pen": 5, "eraser": 3}],
        "output": {"pen": 5.5, "eraser": 3.3},
        "comment": "Price not over 10, tax rate 10%.",
    },
    {
        "input": [{"laptop": 1000, "phone": 500}],
        "output": {"laptop": 1120.0, "phone": 560.0},
        "comment": "Price over 10, tax rate 12%.",
    },
    {
        "input": [{"water": 2, "chocolate": 15}],
        "output": {"water": 2.2, "chocolate": 16.8},
        "comment": "Water not over 10, chocolate over 10.",
    },
    {"input": [{}], "output": {}, "comment": "Empty dict returns empty dict."},
    {
        "input": [{"snack": 10}],
        "output": {"snack": 11.0},
        "comment": "Price equals 10, tax rate 10%.",
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
