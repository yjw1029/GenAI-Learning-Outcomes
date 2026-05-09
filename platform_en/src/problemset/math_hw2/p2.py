description = r"""
## Smart Pig Game
One big pig and one small pig are kept in the same pen. There is a trough on one side and a pedal on the other (the pig that steps the pedal is farther from the trough). Each press puts 10 units of food into the trough, and the pig that presses pays a cost of 2 units. If the big pig reaches the trough first, the big and small pigs eat 9 and 1 units respectively; if the small pig reaches first, they eat 6 and 4; if both pigs press the pedal at the same time, the big and small pigs eat 7 and 3.

(1) The players in the Smart Pig Game are `Blank1` and `Blank2`. Each player can choose the strategies `Blank3` and `Blank4`. (1 pts)

(2) The payoff matrix is: (1.5 pts)

| `Blank1`/`Blank2` | `Blank3` | `Blank4` |
| --- | --- | --- |
| `Blank3` | `A1`,`A2` | `B1`,`B2` |
| `Blank4` | `C1`,`C2` | `D1`,`D2` |

Fill in `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `D1`, `D2`.

(3) Using the underline method, the pure-strategy Nash equilibrium is `Blank5`. (1.5 pts)
"""

math_template = """(1) Blank1: []; Blank2: []; Blank3: []; Blank4: [];

(2) A1: []; A2: []; B1: []; B2: []; C1: []; C2: []; D1: []; D2: []

(3) Blank5: []"""

knowledge = []

title = "Smart Pig Game (4 pts)"
score = 4

answer = r"""
(1) The players are the big pig and the small pig (positions can be swapped). Each player can choose to press the pedal or not press (also called "wait"; order can be swapped).

(2) The payoff matrix, after applying the underline method (big pig is the row player, small pig the column player):

| Big Pig / Small Pig | Press | Not Press |
| :--- | :--- | :--- |
| **Press** | 5, 1 | <u>4</u>, <u>4</u> |
| **Not Press** | <u>9</u>, -1 | 0, <u>0</u> |

Therefore A1: 5, A2: 1, B1: 4, B2: 4, C1: 9, C2: -1, D1: 0, D2: 0.

(3) The underline method gives the unique pure-strategy Nash equilibrium (Blank5) as (press, not press).
"""


answer = r"""
(1) The players are the big pig and the small pig (positions can be swapped). Each player can choose to press the pedal or not press (also called "wait"; order can be swapped).

(2) For the payoff matrix values, depending on **which player is the row player** (big/small) and the **strategy order** (press first/not press first), there are four valid answer layouts. Match the student's table header to one of the following; the underline method results are:

**Case 1: Row = big pig, column = small pig; strategy order = "press, not press"**
| Big Pig / Small Pig | Press | Not Press |
| :--- | :--- | :--- |
| **Press** | 5, 1 | <u>4</u>, <u>4</u> |
| **Not Press** | <u>9</u>, -1 | 0, <u>0</u> |

*Correct sequence:* A1:5, A2:1, B1:4, B2:4, C1:9, C2:-1, D1:0, D2:0.

**Case 2: Row = big pig, column = small pig; strategy order = "not press, press"**
| Big Pig / Small Pig | Not Press | Press |
| :--- | :--- | :--- |
| **Not Press** | 0, <u>0</u> | <u>9</u>, -1 |
| **Press** | <u>4</u>, <u>4</u> | 5, 1 |

*Correct sequence:* A1:0, A2:0, B1:9, B2:-1, C1:4, C2:4, D1:5, D2:1.

**Case 3: Row = small pig, column = big pig; strategy order = "press, not press"**
*(Note: payoffs are ordered as (small pig, big pig).)*
| Small Pig / Big Pig | Press | Not Press |
| :--- | :--- | :--- |
| **Press** | 1, 5 | -1, <u>9</u> |
| **Not Press** | <u>4</u>, <u>4</u> | <u>0</u>, 0 |

*Correct sequence:* A1:1, A2:5, B1:-1, B2:9, C1:4, C2:4, D1:0, D2:0.

**Case 4: Row = small pig, column = big pig; strategy order = "not press, press"**
*(Note: payoffs are ordered as (small pig, big pig).)*
| Small Pig / Big Pig | Not Press | Press |
| :--- | :--- | :--- |
| **Not Press** | <u>0</u>, 0 | <u>4</u>, <u>4</u> |
| **Press** | -1, <u>9</u> | 1, 5 |

*Correct sequence:* A1:0, A2:0, B1:4, B2:4, C1:-1, C2:9, D1:1, D2:5.

**(3) Nash equilibrium grading rule:**
No matter how the table is drawn, the unique pure-strategy Nash equilibrium is **big pig presses, small pig does not press (waits)**.
* If a student writes "(press, not press)", confirm it corresponds to (big pig, small pig).
* If a student writes "(not press, press)", confirm it corresponds to (small pig, big pig).
* The corresponding payoffs are always: big pig gets 4, small pig gets 4.
"""