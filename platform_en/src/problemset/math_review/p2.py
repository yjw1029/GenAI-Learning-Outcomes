description = r"""
## Hawk-Dove Game
In nature, interactions between animals can be viewed as games. For example, when two hawks discover the same food at the same time, they fight and may both be injured, so each hawk's payoff is -2. When two doves meet, they share peacefully and each gets 1. When a hawk meets a dove, the dove retreats and the hawk gets all the food, so the hawk's payoff is 2 and the dove's payoff is 0. Now suppose two birds meet.

(1) The players in the hawk-dove game are `Blank1` and `Blank2`. Each player can choose the strategies `Blank3` and `Blank4`. (1 pts)

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

title = "Hawk-Dove Game (3 pts)"
score = 3

answer = r"""
(1) The players are Bird 1 and Bird 2. Each player can choose the hawk strategy or the dove strategy.

(2) The payoff matrix with underline method:

| Bird 1 \ Bird 2 | Hawk | Dove |
| ------- | ----------- | ----------- |
| Hawk    | -2, -2      | <u>2</u>, <u>0</u> |
| Dove    | <u>0</u>, <u>2</u> | 1, 1 |

Therefore the Nash equilibria are (Hawk, Dove) and (Dove, Hawk).
"""
