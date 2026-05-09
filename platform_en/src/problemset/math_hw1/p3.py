description = r"""
## Splitting One Dollar
Two people negotiate over how to split one dollar. They simultaneously propose desired shares \\(s_1\\) and \\(s_2\\), with \\(0 \leq s_1, s_2 \leq 1 \\). If \\(s_1 + s_2 \leq 1\\), each gets their requested share; if \\(s_1 + s_2 > 1\\), both get nothing. Find the pure-strategy Nash equilibria. (5 pts)

$$
u_i(s_i, s_j) = \\begin{cases}
[[Blank1]], s_1 + s_2 \leq 1 \\\\
[[Blank2]], s_1 + s_2 > 1
\\end{cases}
$$

By definition of Nash equilibrium, \\(s_i^\* = \\arg\max_{0 \leq s_i \leq 1} u_i(s_i, s_j^\*)\\).

Solving yields: `Blank3`

Therefore the pure-strategy Nash equilibria are `Blank4`.
"""

math_template = """
Blank1: [];

Blank2: [];

Blank3: [];

Blank4: [].
"""

knowledge = ["express", "inf_nash"]


title = "Splitting One Dollar (5 pts)"
score = 5

answer = r"""
Let player i's payoff be \\(u_i(s_i, s_j)\\), defined as:

$$
u_i(s_i, s_j) = \\begin{cases}
s_i, &s_i + s_j \\leq 1, \\\\
0, &s_i + s_j > 1.
\\end{cases}
$$

By definition, \\(s_i^\* = \\arg\\max_{0 \\leq s_i \\leq 1} u_i(s_i, s_j^\*)\\).

It follows that \\(s_i^\* = 1 - s_j^\*\\). Therefore there are infinitely many pure-strategy Nash equilibria: any point satisfying \\(s_i^\*+ s_j^\*= 1\\).

Thus Blank1 is \\(s_i\\), Blank2 is 0, Blank3 is \\(s_i^\* = 1 - s_j^\*\\), and Blank4 is any point with \\(s_i^\*+ s_j^\*= 1\\).
"""
