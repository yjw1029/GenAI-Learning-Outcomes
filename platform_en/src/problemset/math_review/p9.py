description = r"""
## Public Goods Problem
A village has 3 herders who graze sheep on common land. The numbers of sheep are \(g_1, g_2, g_3\). The land can support at most \(G_{max} = 10\) sheep; beyond this, the land is overgrazed and each sheep's value becomes 0. The cost per sheep is \(c=4\). The value per sheep \(v(G)\) decreases with total grazing \(G\) as \(v(G) = 20 - 2G\) for \(G < G_{max}\); otherwise \(v(G)=0\).

(1) Villager i's payoff function \(u_i(g_i, g_j, g_k)\) = `Blank1`. (2 pts)

(2) Given \(g_j=g_j^*\) and \(g_k=g_k^*\), villager i's optimal grazing is `Blank2`. (2 pts)

(3) The pure-strategy Nash equilibrium is `Blank3`. (2 pts)
"""

math_template = """(1) Blank1: []

(2) Blank2: []

(3) Blank3: []"""

knowledge = ["finite_nash"]

title = "Public Goods Problem (6 pts)"

score = 6

answer = r"""
(1) \(u_i(g_i, g_j, g_k)\) is:

$$
u_i(g_i, g_j, g_k) = \begin{cases}
g_i(16 - 2G), &g_i + g_j + g_k \leq 10, \\
-4g_i, &g_i + g_j + g_k > 10, \\
\end{cases}
$$

(2) Given \(g_j=g_j^*\) and \(g_k=g_k^*\),

$$
g_i^* = \arg\max_{g_i} u_i(g_i, g_k^*, g_j^*)
$$

When \(g_i + g_j^* + g_k^* \leq 10\):
$$
\frac{\partial u_i(g_i, g_j^*, g_k^*)}{\partial g_i} = 16 - 2G^* - 2g_i^* = 16 - 2g_j^* - 2g_k^* - 4g_i^* = 0
$$

$$
g_i^* = 4 - \frac{g_j^* + g_k^*}{2}
$$

(3) Solving the system gives \(G = 12 - G\), hence \(G = 6\), and \(g_1^* = g_2^* = g_3^* = 2\).
"""
