description = r"""
## Trust Game
Two players play a trust game. The trustor (player 1) has 10 units of resources. They can transfer some portion \((0 \leq x \leq 10)\) to the trustee (player 2), and the transferred amount is tripled. The trustee can then return some amount \((y \leq 3x)\) to the trustor.

(1) Player 1's payoff function \(u_1(x, y)\) is `Blank1`, and player 2's payoff function \(u_2(x, y)\) is `Blank2`. (1 pts)

(2) The pure-strategy Nash equilibrium is `Blank3`. (3 pts)
"""

math_template = """(1) Blank1: []; Blank2: []。

(2) Blank3: []。"""

knowledge = ["finite_nash"]

title = "Trust Game (4 pts)"
score = 4

answer = r"""
(1) Player 1's payoff is \(u_1(x, y) = 10 - x + y\), and player 2's payoff is \(u_2(x, y) = 3x - y\).

(2) Player 2 maximizes payoff by returning 0:

$$
y^* = \arg\max_{y} u_2(x^*, y) = 0
$$

Given \(y^*=0\), player 1 maximizes payoff by sending 0:

$$
x^* = \arg\max_{x} u_1(x, y^*) = 0
$$

Therefore the pure-strategy Nash equilibrium is (0, 0).
"""
