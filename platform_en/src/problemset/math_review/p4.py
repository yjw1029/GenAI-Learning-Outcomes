description = r"""
## Market Barrier
In a market there are two companies (A and B). Each considers whether to raise market barriers to deter new entrants. If one company raises barriers and the other does not, the barrier-raising company gains a higher market share (payoff 3) and the other loses some share (payoff 1). If neither raises barriers, they keep current shares (payoff 2). If both raise barriers, competition drives costs too high and both get 0.

(1) The players are `Blank1` and `Blank2`. Each can choose strategies `Blank3` and `Blank4`. (1 pts)

(2) The payoff matrix is:

| `Blank1`/`Blank2`   | `Blank3` | `Blank4` |
| -------- | -------- | -------- |
| `Blank3` | `A1`,`A2`    | `B1`,`B2`    |
| `Blank4` | `C1`,`C2`    | `D1`,`D2`    |

Fill in `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `D1`, `D2`. The pure-strategy Nash equilibria are `Blank5`. (2 pts)
"""

math_template = """(1) Blank1: []; Blank2: []; Blank3: []; Blank4: []。

(2) A1: []; A2: []; B1: []; B2: []; C1: []; C2: []; D1: []; D2: []; Blank5: []。"""

knowledge = ["express", "finite_nash"]

title = "Market Barrier (3 pts)"

score = 3

answer = r"""
(1) The players are A and B. Each can choose to raise barriers or not.

(2) Payoff matrix with underline method:

| A/B        | Raise Barriers     | Do Not Raise     |
| -------- | ----------------- | ----------------- |
| Raise Barriers | 0,0           | <u>3</u>,<u>1</u> |
| Do Not Raise | <u>1</u>,<u>3</u> | 2,2            |

Therefore A1: 0, A2: 0, B1: 3, B2: 1, C1: 1, C2: 3, D1: 2, D2: 2.

The underline method gives Nash equilibria: (Raise Barriers, Do Not Raise) and (Do Not Raise, Raise Barriers).
"""
