import sympy

s = sympy.Symbol('s')
"""Mandelstam variable s"""
t = sympy.Symbol('t')
"""Mandelstam variable t"""
u = sympy.Symbol('u')
"""Mandelstam variable u"""
e = sympy.Symbol('e')
"""Elementary charge"""

equation_6_30 = 2*e**4 * (s**2 + u **2)/t**2
"""unpolarized e-mu- -> e-mu- scattering amplitude"""
equation_6_31 = 2*e**4 * (t**2 + u **2)/s**2
"""unpolarized e-e+ -> mu-mu+ scattering amplitude"""

equation_6_113 = 2*e**4 * (- u/s - s/u)
"""spin averaged Compton amplitude"""

bibtex : str = """
@book{Halzen:1984mc,
    author = "Halzen, F. and Martin, Alan D.",
    title = "{QUARKS AND LEPTONS: AN INTRODUCTORY COURSE IN MODERN PARTICLE PHYSICS}",
    isbn = "978-0-471-88741-6",
    year = "1984"
}
"""