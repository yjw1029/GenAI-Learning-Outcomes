description = r"""
## Hotelling Model

Suppose there is a 1 km beach with uniformly distributed visitors. Two ice-cream stands (stand 1 and stand 2) plan to open on the beach and choose locations \(a\) and \((1-b)\), with \(a + b < 1\). The ice cream is identical in quality. Prices are \(p_1\) and \(p_2\). Assume there is no fixed cost and marginal cost is a constant \(c\).

Note: Fixed cost does not change with output within a range (e.g., rent, management salaries, depreciation). Marginal cost is the additional cost of producing one more unit; it is the derivative of total cost with respect to output.

<img src="/assets/hoteling.png" alt="image" width="400" height="auto">

(1) Assume consumers know both prices. The travel cost per unit distance is \(t\), and consumers choose the stand with the lowest total cost (ice-cream price plus travel cost). Let \(x^* \in [0, 1]\) be the indifferent consumer: if \(x< x^*\), choose stand 1; if \(x>x^*\), choose stand 2. Then \(x^*\) is `Blank1`. (3 pts)

(2) The Nash equilibrium locations \(a\) and \(b\) are `Blank2`, `Blank3`. (4 pts)

(3) Now suppose locations are fixed at \(a\) and \((1-b)\), with \(a + b < 1\). The firms choose prices \(p_1\) and \(p_2\). The Nash equilibrium prices are `Blank4`, `Blank5`. (4 pts)
"""

math_template = """(1) Blank1: [];

(2) Blank2: []

Blank3: []

(3) Blank4: []

Blank5: []"""

knowledge = []

title = "Hotelling Model (11 pts)"
score = 11

answer = r"""
(1) At the indifferent point \(x^*\), total costs are equal:
\(t(x^* - a) + p_1 = t(1 - b - x^*) + p_2\)
Solving gives Blank1: \(\frac{p_2 - p_1}{2t} + \frac{1 - b + a}{2}\)

(2) Stand 1's profit is \(u_1(a, b) = (p_1 - c) \times x^*\). The partial derivative w.r.t. \(a\) is \(\frac{\partial u_1}{\partial a} = \frac{p_1 - c}{2}\). Since \(p_1 > c\), it is always positive, so stand 1 moves right (increase \(a\)).
Similarly, \(\frac{\partial u_2}{\partial b} = \frac{p_2 - c}{2} > 0\), so stand 2 moves left (increase \(b\)).
Thus both firms move to the center: the Nash equilibrium is both at the middle.
Blank2: \(1/2\) (or \(0.5\))
Blank3: \(1/2\) (or \(0.5\))

(3) With locations fixed, firms choose prices to maximize profit:
\(\pi_1 = (p_1 - c)(\frac{p_2 - p_1}{2t} + \frac{1 - b + a}{2})\)
\(\pi_2 = (p_2 - c)(\frac{p_1 - p_2}{2t} + \frac{1 + b - a}{2})\)
FOCs (reaction functions):
\(p_1 = \frac{1}{2}(p_2 + c + t(1 - b + a))\)
\(p_2 = \frac{1}{2}(p_1 + c + t(1 + b - a))\)
Solving gives equilibrium prices:
Blank4: \(c + t(1 + \frac{a - b}{3})\)
Blank5: \(c + t(1 + \frac{b - a}{3})\)
"""
