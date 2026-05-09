description = """
## ATM Transactions
Write a function `atm_transactions(balance, transactions)` that takes an initial balance and a transaction dictionary. The dictionary has keys "D" (deposit) and "W" (withdraw), each mapped to a list of amounts. Compute and return the final balance after all transactions. (4 pts)
"""

title = "ATM Transactions (4 pts)"
score = 4

knowledge = ["dict", "loop"]

code_template = """
def atm_transactions(balance, transactions):
    # your code
    return ...
"""

code_entrypoint = "atm_transactions"

validcases = [
    {
        "input": [1000, {"D": [300, 200], "W": [500, 100]}],
        "output": 900,
        "comment": "Start 1000. Deposits +300+200, withdrawals -500-100. Final 900.",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [500, {"D": [100], "W": [50]}],
        "output": 550,
        "comment": "Start 500. Deposit +100, withdrawal -50. Final 550.",
    },
    {
        "input": [2000, {"D": [500, 300], "W": [200, 100, 50]}],
        "output": 2450,
        "comment": "Start 2000. Deposits +500+300, withdrawals -200-100-50. Final 2450.",
    },
    {
        "input": [0, {"D": [100, 200, 300], "W": [150, 100]}],
        "output": 350,
        "comment": "Start 0. Deposits +100+200+300, withdrawals -150-100. Final 350.",
    },
    {
        "input": [750, {"D": [], "W": []}],
        "output": 750,
        "comment": "No transactions, balance unchanged.",
    },
    {
        "input": [100, {"W": [50, 10, 20]}],
        "output": 20,
        "comment": "Start 100. Only withdrawals -50-10-20. Final 20.",
    },
    {
        "input": [500, {"D": [500], "W": [1000]}],
        "output": 0,
        "comment": "Start 500. Deposit +500, withdrawal -1000. No overdraft, final 0.",
    },
]

answer = """
```Python
def atm_transactions(balance, transactions):
    for action in transactions:
        amounts = transactions[action]
        for amount in amounts:
            if action == "D":
                balance += amount
            elif action == "W":
                balance -= amount
    return balance
```
"""
