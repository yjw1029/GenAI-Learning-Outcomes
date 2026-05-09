description = r"""
## Stag Hunt Game
Two hunters go hunting. They can hunt a deer or a hare. A deer requires cooperation by two people, while a hare can be hunted alone; the payoff from deer is higher than that from hare. Let the payoff from deer be x and from hare be y.

(1) The players in this stag hunt game are `Blank1` and `Blank2`. Each player can choose the strategies `Blank3` and `Blank4`. (1 pts)

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

title = "Stag Hunt Game (3 pts)"

score = 3

answer = r"""
(1) The players are Hunter 1 and Hunter 2. Each player can choose to hunt deer or hunt hare.

(2) The payoff matrix with underline method:

| Hunter 1 / Hunter 2 | Hunt Deer        | Hunt Hare      |
| ----------- | --------------- | ------------- |
| Hunt Deer   | <u>x</u>,<u>x</u>  | 0,y           |
| Hunt Hare   | y,0             | <u>y</u>,<u>y</u> |

Therefore the Nash equilibria are (Hunt Deer, Hunt Deer) and (Hunt Hare, Hunt Hare).
"""
