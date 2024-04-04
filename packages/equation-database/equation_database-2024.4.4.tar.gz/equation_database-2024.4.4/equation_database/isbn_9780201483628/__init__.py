import sympy
from equation_database.util.parse import frac
Q = sympy.Symbol('Q')
"""Mass of the virtual photon"""

u = sympy.Symbol('u')
"""Mandelstam variable u"""
t = sympy.Symbol('t')
"""Mandelstam variable t"""

g_s = sympy.Symbol('g_s')
"""strong coupling constant """
e = sympy.Symbol('e')
"""electric charge """
e_q = sympy.Symbol('e_q')
"""electric charge of the quark """

equation_4_3_20 = e**2*e_q**2* g_s**2 *frac("4/8")*frac("1/2") * 8 * (u/t + t/u + 2*Q**2*(u+t+Q**2)/(t*u))
""" gamma* gluon -> q qbar scattering averaged matrix element"""


bibtex : str = """
@book{field1995applications,
  title={Applications Of Perturbative Qcd},
  author={Field, R.D. and Pines, D.},
  isbn={9780201483628},
  lccn={89000138},
  url={https://books.google.de/books?id=2eWnAAAACAAJ},
  year={1995},
  publisher={Avalon Publishing}
}
"""
"""Bibtex citation"""

