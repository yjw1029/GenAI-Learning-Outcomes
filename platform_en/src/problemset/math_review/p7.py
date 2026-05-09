description = r"""
## Divider-Chooser Game
A and B share a cake. The cake can be divided into two portions. A first splits the cake into two pieces, and then B chooses one. Both want as much cake as possible. Suppose A's split is \(x\) and \(1-x\) (\(x\leq0.5\)).

(1) A's payoff \(u_A\) is `Blank1`, and B's payoff \(u_B\) is `Blank2`. (3 pts)

(2) The pure-strategy Nash equilibrium is `Blank3`. (2 pts)
"""

math_template = """(1) Blank1: []; Blank2: []; 。

(2) Blank3: []。"""

knowledge = ["infinite_nash"]

title = "Divider-Chooser Game (5 pts)"

score = 5

answer = r"""
(1) \(u_A(x)\) is:

$$
u_A(x) = \begin{cases}
x, &B\text{ chooses }1-x, \\
1-x, &B\text{ chooses }x.
\end{cases}
$$

\(u_B(x)\) is:
$$
u_B(x) = \begin{cases}
1-x, &B\text{ chooses }1-x, \\
x, &B\text{ chooses }x.
\end{cases}
$$

(2) B maximizes payoff by choosing \(1-x^*\), and A chooses \(x^*\). A maximizes \(x^*\), so \(x^*=0.5\).
"""
