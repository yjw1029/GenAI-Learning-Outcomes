description = r"""
## Bertrand Duopoly Model
We consider two differentiated products. If firm 1 and firm 2 choose prices \\(p_1\\) and \\(p_2\\), demand for firm \\(i\\)'s product is:

$$
q_i(p_i, p_j) = a - p_i + bp_j
$$

where \\(b>0\\), meaning firm \\(i\\)'s product is a differentiated substitute for firm \\(j\\)'s product. Assume no fixed costs and constant marginal cost \\(c\\). Find the pure-strategy Nash equilibrium. (7 pts)

Tip: Fixed costs do not change with output within a certain range (e.g., rent, management salaries, depreciation). Marginal cost is the additional cost of producing one more unit, i.e., the derivative of total cost with respect to output.

Fill in the blanks:

Let firm i's payoff be \\(u_i(p_i, p_j)\\). From the description:

$$
u_i(p_i, p_j) = [[Blank1]]
$$

The Bertrand equilibrium is \\(p_1^\*=\\)`Blank2`, \\(p_2^\*=\\)`Blank3`.

"""

math_template = """
Blank1: [];

Blank2: [];

Blank3: [].
"""

title = "Bertrand Model (7 pts)"
score = 7

knowledge = ["express", "inf_nash"]

answer = r"""
Let firm i's payoff be \\(u_i(p_i, p_j)\\). From the description:

$$
u_i(p_i, p_j) = q_i \\times (p_i - c) = (a - p_i + bp_j)(p_i -c).
$$

By definition, \\(p_i^\*\\) solves:

$$
p_i^* = \\arg\\max_{p_i \\geq 0} u_i(p_i, p_j^\*).
$$

Solving this is equivalent to the FOCs:

$$
\\frac{\\partial u_i(p_i, p_j^\*)}{\\partial p_i} = a - p_i +b p_j^\*-p_i+c = a+c+bp_j^\*-2p_i = 0,\\\\
\\frac{\\partial^2 u_i(p_i, p_j^\*)}{\\partial {p_i}^2} = -2 < 0.
$$

Thus:

$$
\\begin{cases}
a+c+bp_2^\* - 2p_1^\* &= 0,\\\\
a+c+bp_1^\* - 2p_2^\* &= 0.\\\\
\\end{cases}
$$

Solving yields \\(p_1^\* = p_2^\* = \\frac{a+c}{2 - b}\\), which is the Bertrand equilibrium.

Therefore Blank1 is \\(q_i \\times (p_i - c) = (a - p_i + bp_j)(p_i -c).\\), and Blank2 and Blank3 are both \\(\\frac{a+c}{2 - b}\\).
"""
