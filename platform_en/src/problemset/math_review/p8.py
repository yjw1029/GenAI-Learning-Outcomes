description = r"""
## Bertrand Model 2
Suppose two firms (1 and 2) sell a homogeneous product. Each sets its price \(p_1\) and \(p_2\). Consumers buy from the lower-priced firm. If prices are equal, consumers split equally. Each firm has constant marginal cost \(c\), and market demand is \(D(p)=D_0-k \cdot p\), where \(p\) is the lowest market price, and \(D_0\), \(k\) are constants.

(1) The payoff function is \(u_i(p_i, p_j)\) = `Blank1`. (2 pts)

(2) The pure-strategy Nash equilibrium is `Blank2`. (4 pts)
"""

math_template = """(1) Blank1: []; 。

(2) Blank2: []。"""

knowledge = ["finite_nash"]

title = "Bertrand Model 2 (6 pts)"

score = 6

answer = r"""
(1) \(u_i(p_i, p_j)\) is:

$$
u_i(p_i, p_j) = \begin{cases}
(D_0 - kp_i)(p_i - c), &p_i < p_j, \\
(D_0 - kp_i)\frac{p_i - c}{2}, &p_i = p_j, \\
0, &p_i > p_j, \\
\end{cases}
$$

(2) Since \(u_i\) is maximized when \(p_i < p_j\), each firm wants to price slightly below the other and capture the market.

A simple proof shows (c, c) is the unique Nash equilibrium.
First, given the other firm prices at c, pricing at c yields zero profit. Pricing above c gives zero profit, and pricing below c gives negative profit. So c is a best response to c for both firms, hence (c, c) is a Nash equilibrium.
Second, since there are no fixed costs, firms will not price below c. If both price above c, each has an incentive to undercut slightly, so no equilibrium. If one prices above c and the other at c, the high-price firm wants to undercut, so not an equilibrium. Thus the unique Nash equilibrium is (c, c).
"""
