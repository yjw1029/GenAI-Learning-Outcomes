description = """
## Abstract Game 3
Given the following normal-form game.

(1) Using iterated elimination, the strategies that are not eliminated are `Blank1`. (1.5 pts)

(2) Using the underline method, the pure-strategy Nash equilibria are `Blank2`. (1.5 pts)

| Player 1 / Player 2 | L | C | R |
| -- | -- | -- | -- |
| T | 2, 0 | 1, 1 | 4, 2 |
| M | 3, 4 | 1, 2 | 2, 3 |
| B | 1, 3 | 0, 2 | 3, 0 |
"""

math_template = """
(1) Blank1:

(2) Blank2:
"""

knowledge = []

title = "Abstract Game 3 (3 pts)"
score = 3

answer = """
(1) For player 1, B is strictly dominated by T (2>1, 1>0, 4>3), so eliminate B.
For player 2, with T and M remaining, C is strictly dominated by R (R payoffs 2,3 vs C payoffs 1,2), so eliminate C.
Remaining strategies are T, M, L, R.

(2) Underline method:

| Player 1 / Player 2 | L | C | R |
| :---: | :---: | :---: | :---: |
| T | 2, 0 | <u>1</u>, 1 | <u>4</u>, <u>2</u> |
| M | <u>3</u>, <u>4</u> | <u>1</u>, 2 | 2, 3 |
| B | 1, <u>3</u> | 0, 2 | 3, 0 |

The pure-strategy Nash equilibria are (T, R) and (M, L).
"""
