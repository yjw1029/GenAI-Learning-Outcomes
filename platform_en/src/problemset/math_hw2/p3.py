description = r"""
## n-Player Cournot Game
Consider a Cournot model with \(n\) firms. Let \(q_i\) be firm i's output, and \(Q=\sum_{i=1}^{n} q_i\) be total market output. The market-clearing price is \(P\), with \(P=P(Q)=a-Q\) (when \(Q<a\); otherwise \(P=0\)). Assume there is no fixed cost and marginal cost is a constant \(c\).

Note: Fixed cost does not change with output within a range (e.g., rent, management salaries, depreciation). Marginal cost is the additional cost of producing one more unit; it is the derivative of total cost with respect to output.

(1) Under these assumptions, each firm's profit function is: (2 pts)

$$
\pi_i(q_1,\cdots,q_n)=[[Blank1]]
$$

where \(i=1,2,...,n\).

(2) In the Nash equilibrium of the n-player Cournot game, \(q_i^*\) equals: `Blank2`. (3 pts)
"""

math_template = """(1) Blank1: [];

(2) Blank2: []"""

knowledge = []

title = "n-Player Cournot Game (5 pts)"
score = 5

answer = r"""
(1) Firm i's profit function is:
$$
\pi_i(q_1, \dots, q_n) = q_i(a - Q - c) = q_i(a - (\sum_{i=1}^n q_i) - c)
$$
So Blank1 is: q_i(a - (\sum_{i=1}^n q_i) - c).

(2) By the definition of Nash equilibrium, firm i's optimal output \(q_i^*\) solves:
$$
\max_{q_i \geq 0} \pi_i(q_1^*, \dots, q_{i-1}^*, q_i, q_{i+1}^*, \dots, q_n^*)
$$
Taking the first-order condition:
$$
\frac{\partial \pi_i}{\partial q_i} = a - (\sum_{j=1, j \neq i}^n q_j^*) - c - 2q_i = 0
$$
The second-order condition holds since \(\frac{\partial^2 \pi_i}{\partial q_i^2} = -2 < 0\).

By symmetry, all firms choose the same equilibrium output: \(q_1^* = q_2^* = \dots = q_n^* = q^*\).
Substitute into the FOC:
$$
a - (n-1)q^* - c - 2q^* = 0
$$
$$
a - c = (n+1)q^*
$$
Thus:
$$
q^* = \frac{a-c}{n+1}
$$
So Blank2 is: \frac{a-c}{n+1}.
"""
