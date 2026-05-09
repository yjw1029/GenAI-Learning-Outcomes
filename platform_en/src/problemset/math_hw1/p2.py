description = """
## Yale Game Theory Classroom Game
In class, the teacher gives students two choices, “A” and “B”. Each student writes one choice on a note. Students are randomly paired, and they do not know who their partner is in advance. Each student then receives a score:
1. If I choose “A” and the other chooses “B”, I get 3 and the other gets -1.
2. If I choose “B” and the other chooses “A”, I get -1 and the other gets 3.
3. If both choose “A”, both get 0.
4. If both choose “B”, both get 1.

(1) The payoff matrix is below. Fill in each cell. (1 pts)

| Me/Other | A | B |
| --- | --- | --- |
| A | `A1`,`A2` | `B1`,`B2` |
| B | `C1`,`C2` | `D1`,`D2` |

Fill in `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `D1`, `D2`.

(2) Using iterated strict dominance elimination, which strategy profiles are not eliminated? (1.5 pts)

A: (A, A)  B: (A, B)  C: (B, A)  D: (B, B)

Your choice: `Blank1`.

(3) Using the underline method, what is the pure-strategy Nash equilibrium? (1.5 pts)

A: (A, A)  B: (A, B)  C: (B, A)  D: (B, B)

Your choice: `Blank2`.
"""

math_template = """
(1) A1: []; A2: []; B1: []; B2: []; C1: []; C2: []; D1: []; D2: [].

(2) Blank1: [].

(3) Blank2: [].
"""

knowledge = ["express", "dominated", "finite_nash"]

title = "Yale Classroom Game (4 pts)"
score = 4

answer = """
(1) The payoff matrix is:

| Me/Other | A   | B   |
| -------- | ---- | ---- |
| A        | 0,0  | 3,-1 |
| B        | -1,3 | 1,1  |

So A1:0, A2:0, B1:3, B2:-1, C1:-1, C2:3, D1:1, D2:1.

(2) For both players, B is strictly dominated by A. Thus only (A, A) survives. Blank1 = (A, A).

(3) Underline method:

| Me/Other | A                | B          |
| -------- | ---------------- | ---------- |
| A        | <u>0</u>,<u>0</u> | <u>3</u>,-1 |
| B        | -1,<u>3</u>       | 1,1        |

The pure-strategy Nash equilibrium (Blank2) is (A, A).
"""
