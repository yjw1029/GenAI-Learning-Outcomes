description = r"""
## Found Document Game
Company representative A is going to sign a contract expected to bring 100,000 in profit. Unfortunately, a key document is lost and picked up by passerby B. If A cannot retrieve it in time, the deal fails, causing a potential reputation loss of 30,000; the document has no value to B.
A contacts B, and both know the document is important to A and worthless to B. B has two choices:

* Ask for a reward of 20,000 to return the document. B gains 20,000 but suffers moral pressure equivalent to a 15,000 loss.
* Return it for free: no monetary gain, but moral satisfaction worth 15,000.

A's choices:

* Pay the 20,000 reward to retrieve the document. Total loss is 20,000 (paying avoids the 30,000 reputation loss and 100,000 profit loss).
* Give up the document and bear a total loss of 130,000.

(1) The payoff matrix is:

| A/B   | Ask for Reward | No Reward |
| -------- | -------- | -------- |
| Retrieve | `A1`,`A2`    | `B1`,`B2`    |
| Not Retrieve | `C1`,`C2`    | `D1`,`D2`    |

Fill in `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `D1`, `D2`. (1 pts)

(2) The pure-strategy Nash equilibrium is `Blank1`. (1 pts)
"""

math_template = """(1) A1: []; A2: []; B1: []; B2: []; C1: []; C2: []; D1: []; D2: [];

(2) Blank1: []。"""

knowledge = ["express", "finite_nash"]

title = "Found Document Game (2 pts)"

score = 3

answer = r"""
(1) The payoff matrix is:

| A/B         | Ask for Reward | No Reward |
| ----------- | ------------- | -------------- |
| Retrieve    | 8, 0.5        | 10, 1.5        |
| Not Retrieve | -3, -1.5     | -3, 1.5        |

(2) Underline method:

| A/B         | Ask for Reward | No Reward |
| ----------- | ------------- | -------------- |
| Retrieve    | <u>8</u>, 0.5  | <u>10</u>, <u>1.5</u> |
| Not Retrieve | -3, -1.5     | -3, <u>1.5</u> |

Therefore the pure-strategy Nash equilibrium is (Retrieve, No Reward).
"""
