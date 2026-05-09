description = r"""
## Final-Offer Arbitration
A firm and a union dispute wages. Both submit wage demands to a neutral arbitrator. The firm and union simultaneously submit their desired wages, denoted \(w_1\) and \(w_2\) (\(w_1 < w_2\)). The arbitrator chooses one of the two demands as the outcome. The arbitrator has an ideal wage \(x\) and simply picks the offer closest to \(x\). The arbitrator knows \(x\), while the other two parties do not; they believe \(x\) is a random variable with CDF \(F(x)\) and PDF \(f(x)\).

(1) The expected wage is `Blank1`. (2 pts)

(2) Let \(w_1^*, w_2^*\) be the Nash equilibrium offers. The equilibrium condition is `Blank2` (expressed using the CDF). (6 pts)
"""

math_template = """(1) Blank1: []; 。

(2) Blank2: []。"""
knowledge = ["express", "finite_nash"]

title = "Final-Offer Arbitration (8 pts)"

score = 8

answer = r"""
(1) Since \(P(w_1\text{ chosen}) = P(x < \frac{w_1+w_2}{2}) = F(\frac{w_1+w_2}{2})\),

the expected wage is \(E[w] = w_1 * F(\frac{w_1+w_2}{2}) + w_2 * [1-F(\frac{w_1+w_2}{2})]\).

(2) The Nash equilibrium \((w_1^*, w_2^*)\) satisfies:

$$
w_1^* = \arg\min_{w_1} w_1 * F(\frac{w_1+w_2^*}{2}) + w_2^* * [1-F(\frac{w_1+w_2^*}{2})]
$$

$$
w_2^* = \arg\max_{w_2^*} w_1^* * F(\frac{w_1^*+w_2}{2}) + w_2 * [1-F(\frac{w_1^*+w_2}{2})]
$$

Taking first-order conditions gives:

$$
(w_1^* - w_2^*)*\frac{1}{2} f(\frac{w_1^*+w_2^*}{2}) = F(\frac{w_1^*+w_2^*}{2})
$$

$$
(w_1^* - w_2^*)*\frac{1}{2} f(\frac{w_1^*+w_2^*}{2}) = 1 - F(\frac{w_1^*+w_2^*}{2})
$$

This implies \(F(\frac{w_1^*+w_2^*}{2}) = \frac{1}{2}\). That is, the average of the two offers equals the median of the arbitrator's ideal wage. Also,

$$
(w_1^* - w_2^*) = \frac{1}{f(\frac{w_1^*+w_2^*}{2})}
$$
"""
