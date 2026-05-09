description = r"""
## Two-Thirds of the Average Guess
In a game, n participants simultaneously choose a number in [0, 360]. The winner is the person whose number is closest to two-thirds of the average. Participants do not know others' choices. Assuming all players are rational, what number will they choose?

(1) Let player i's choice be \(x_i\). The payoff function is \(u_i(x_1, ..., x_n)\) = `Blank1`. (1 pts)

(2) The pure-strategy Nash equilibrium is `Blank2`. (3 pts)
"""

math_template = """(1) Blank1: []。

(2) Blank2: []。"""

knowledge = ["finite_nash"]

title = "Two-Thirds of the Average Guess (4 pts)"
score = 4

answer = r"""
Let the average be \(\bar{x}=\frac{1}{n}\sum{x_i}\). Then:

$$
u_i(x_1, ..., x_n) = \begin{cases}
1, &x_i\text{ is closest to }\frac{2}{3}\bar{x}, \\
0, &\text{otherwise.}
\end{cases}
$$

By definition of Nash equilibrium, \(x_i^* = \arg\max_{x_i} u_i(x_1^*, ..., x_n^*)\), which implies \(x_i^* = \frac{2}{3}\bar{x}^*\).
Summing over all players and averaging gives \(\bar{x}^*=\frac{2}{3}\bar{x}^*\).
Thus \(\bar{x}^*=0\), and since \(x_i \ge 0\), the pure-strategy Nash equilibrium is \(x_i^* = 0\).
"""
