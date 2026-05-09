description = """
## The Blonde Girl
In a movie, two men (A and B) go to a bar with several women. One is a beautiful blonde, and the rest are ordinary women. The men want to approach someone. This is modeled as a two-player game: matching with the blonde gives payoff 2, matching with an ordinary woman gives payoff 1, and getting no one gives payoff 0. (If both pursue the blonde, they interfere and nobody succeeds, so payoff is 0. If only one person approaches a woman, it is considered successful.)

(1) The participants in this game are `Blank1` and `Blank2`. Each participant's strategies are `Blank3` and `Blank4`. (1 pts)


(2) The payoff matrix is:

| `Blank1`/`Blank2` | `Blank3` | `Blank4` |
| --- | --- | --- |
| `Blank3` | `A1`,`A2` | `B1`,`B2` |
| `Blank4` | `C1`,`C2` | `D1`,`D2` |

Fill in `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `D1`, `D2`, and the Nash equilibria are `Blank5`. (2 pts)
"""

math_template = """(1) Blank1: []; Blank2: []; Blank3: []; Blank4: [].

(2) A1: []; A2: []; B1: []; B2: []; C1: []; C2: []; D1: []; D2: []; Blank5: [].
"""

knowledge = ["express", "finite_nash"]

title = "The Blonde Girl (3 pts)"
score = 3

answer = """
(1) The participants are A and B (order can be swapped, so Blank1/Blank2 can be A/B or B/A). The strategies are: blonde and ordinary (order can be swapped).

(2) Because the game is symmetric, swapping row/column players does not change the payoffs; **values only depend on the strategy order**. Either of the following matrices is correct:

**Case 1: if the student puts “blonde” in the first row/column (i.e., Blank3 is blonde):**

| (Row)/(Column) | Blonde | Ordinary |
| --- | --- | --- |
| Blonde | 0, 0 | 2, 1 |
| Ordinary | 1, 2 | 1, 1 |

So: A1:0, A2:0, B1:2, B2:1, C1:1, C2:2, D1:1, D2:1.

**Case 2: if the student puts “ordinary” in the first row/column (i.e., Blank3 is ordinary):**

| (Row)/(Column) | Ordinary | Blonde |
| --- | --- | --- |
| Ordinary | 1, 1 | 1, 2 |
| Blonde | 2, 1 | 0, 0 |

So: A1:1, A2:1, B1:1, B2:2, C1:2, C2:1, D1:0, D2:0.

**Nash equilibria (Blank5):**
The equilibria are (ordinary, blonde) and (blonde, ordinary).
Notes:
1. Regardless of who is row/column, the equilibria are “one chooses blonde, the other chooses ordinary.”
2. Students may describe in words (e.g., “A blonde/B ordinary or A ordinary/B blonde”) or as strategy pairs.
"""
