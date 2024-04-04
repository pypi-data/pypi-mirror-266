import sympy

s = sympy.Symbol('s')
"""
Mandelstam variable s

Reference:
    - :py:obj:`equation_database.doi_10_1103_physrev_176_1700.s`

"""
t = sympy.Symbol('t')
"""Mandelstam variable t (See :py:obj:`equation_database.doi_10_1103_physrev_176_1700.t`)"""
u = sympy.Symbol('u')
"""Mandelstam variable u"""
B = sympy.Symbol('B') 
"""squared eletroweakino-squark coupling """
g_s = sympy.Symbol('g_s')
"""strong coupling constant """
C_A = sympy.Symbol('C_A')
"""Casimir operator for the adjoint representation of SU(3) """
C_F = sympy.Symbol('C_F')
"""Casimir operator for the fundamental representation of SU(3) """
m_X = sympy.Symbol('m_chi')
"""Mass of the electroweakino """
m_sq = sympy.Symbol('m_q')
"""Mass of the squark """
M_s = sympy.Symbol('M_s')
"""Matrix element for the s channel """
M_u = sympy.Symbol('M_u')
"""Matrix element for the u channel """
M = sympy.Symbol('M')
"""Matrix element for the process """


equation_2_4 = sympy.Eq(sympy.Abs(M_s)**2 , g_s**2 * C_A*C_F * B / s *2 * (m_X**2 -t))
"""Equation (2.4)"""
equation_2_5 = sympy.Eq(sympy.Abs(M_u)**2 , g_s**2 * C_A *C_F *B/(u - m_sq**2)**2 * 2 * ( m_X**2- u) * ( m_sq**2+u))
"""Equation (2.5)"""
equation_2_6 = sympy.Eq(2*sympy.re(M_s*sympy.conjugate(M_u)), g_s**2 * C_A *C_F * B /(s*(u-m_sq**2)) * ( 2 * (m_X**4- m_sq**4) + m_sq**2 * ( 2*u -3*s) -2*m_X **2 * ( 2*m_sq**2 +u) -s*u) )
"""Equation (2.6)"""
equation_2_8 = sympy.Eq(sympy.Abs(M)**2, (equation_2_4.lhs + equation_2_5.lhs + equation_2_6.lhs )/96)
"""Equation (2.8)"""

bibtex : str = """
@article{Fiaschi:2022odp,
    author = "Fiaschi, Juri and Fuks, Benjamin and Klasen, Michael and Neuwirth, Alexander",
    title = "{Soft gluon resummation for associated squark-electroweakino production at the LHC}",
    eprint = "2202.13416",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    reportNumber = "MS-TP-22-05, LTH 1299",
    doi = "10.1007/JHEP06(2022)130",
    journal = "JHEP",
    volume = "06",
    pages = "130",
    year = "2022"
}
"""
"""Bibtex citation"""