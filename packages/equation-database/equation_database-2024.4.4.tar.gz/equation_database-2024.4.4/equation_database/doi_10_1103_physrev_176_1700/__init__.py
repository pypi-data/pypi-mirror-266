import sympy

s = sympy.symbols('s')
"""Mandelstam variable s"""

t = sympy.symbols('t')
"""Mandelstam variable t"""

u = sympy.symbols('u')
"""Mandelstam variable u"""

p1_mu = sympy.symbols('p1_mu')
p2_mu = sympy.symbols('p2_mu')
p3_mu = sympy.symbols('p3_mu')
p4_mu = sympy.symbols('p4_mu')

S_mu = sympy.symbols('S_mu')
T_mu = sympy.symbols('T_mu')
U_mu = sympy.symbols('U_mu')

equation_A3 = (
        sympy.Eq(S_mu, (p1_mu + p2_mu)), sympy.Eq(S_mu, (p3_mu + p4_mu)),
        sympy.Eq(U_mu, (p1_mu - p3_mu)), sympy.Eq(U_mu, (p4_mu - p2_mu)),
        sympy.Eq(T_mu, (p1_mu - p4_mu)), sympy.Eq(T_mu, (p3_mu - p2_mu)),
    )
"""Equation A3:"""

equation_A4 = sympy.Eq(s, S_mu**2),sympy.Eq(t, T_mu**2),sympy.Eq(u, U_mu**2),
"""Equation A4:"""

bibtex : str = """
@article{Balachandran:1968rj,
    author = "Balachandran, A. P. and Nuyts, J. and Meggs, W. J. and Ramond, Pierre",
    title = "{Simultaneous partial wave expansion in the Mandelstam variables: the group SU(3)}",
    doi = "10.1103/PhysRev.176.1700",
    journal = "Phys. Rev.",
    volume = "176",
    pages = "1700",
    year = "1968"
}
"""
"""Bibtex citation"""