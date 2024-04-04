import sympy
from equation_database.util.parse import frac


s = sympy.Symbol('s')
"""Mandelstam variable s"""
t = sympy.Symbol('t')
"""Mandelstam variable t"""
u = sympy.Symbol('u')
"""Mandelstam variable u"""
g = sympy.Symbol('g')
"""Strong coupling constant"""

table_7_1= {
    "quark_quarkprime_to_quark_quarkprime"       : frac("4/9")   * (s**2+u**2)/(t**2),
    "quark_quarkprimebar_to_quark_quarkprimebar" : frac("4/9")   * (s**2+u**2)/(t**2),
    "quark_quark_to_quark_quark"                 : frac("4/9")   * ( (s**2+u**2)/(t**2) + (s**2+t**2)/(u**2) ) - frac("8/27") * s**2/(u*t),
    "quark_quarkbar_to_quarkprime_quarkprimebar" : frac("4/9")   * ( (t**2+u**2)/(s**2) ),
    "quark_quarkbar_to_quark_quarkbar"           : frac("4/9")   * ( (s**2+u**2)/(t**2) + (t**2+u**2)/(s**2) ) - frac("8/27") * u**2/(s*t),
    "quark_quarkbar_to_gluon_gluon"              : frac("32/27") * (t**2+u**2)/(t*u) - frac("8/3") * (t**2+u**2)/(s**2),
    "gluon_gluon_to_quark_quarkbar"              : frac("1/6")   * (t**2+u**2)/(t*u) - frac("3/8") * (t**2+u**2)/(s**2),
    "gluon_quark_to_gluon_quark"                 : frac("-4/9")  * (s**2+u**2)/(s*u) + (u**2+s**2)/t**2,
    "gluon_gluon_to_gluon_gluon"                 : frac("9/2")   * (3 - t*u/s**2 - s*u/t**2 - s*t/u**2),
}
"""The invariant matrix elements squared for two-to-two parton subprocesses with massless partons. The colour and spin indices are averaged (summed) over initial (final) states."""


N = sympy.Symbol('N')
"""Number of colors"""

table_7_2 = {
    "quark_quarkbar_to_gammastar_gluon" :  (N**2-1)/N**2 * (t**2+u**2 + 2*s * (s+t+u))/(t*u),
    "gluon_quark_to_gammastar_quark"     : - 1/N * (s**2 + u**2 + s*t*(s+t+u)/(s*u)),
}
"""Lowest order processes for virtual photon production. The colour and spin indices are averaged (summed) over initial (final) states. For a real photon (s +1 + u) = 0 and for SU(3) we have N = 3"""

bibtex : str = """
@book{Ellis:1996mzs,
    author = "Ellis, R. Keith and Stirling, W. James and Webber, B. R.",
    title = "{QCD and collider physics}",
    doi = "10.1017/CBO9780511628788",
    isbn = "978-0-511-82328-2, 978-0-521-54589-1",
    publisher = "Cambridge University Press",
    volume = "8",
    month = "2",
    year = "2011"
}
"""

# Backward compatibility
table_7_1_qqp_qqp =  table_7_1["quark_quarkprime_to_quark_quarkprime"]
table_7_1_qqpb_qqpb = table_7_1["quark_quarkprimebar_to_quark_quarkprimebar"]
table_7_1_qq_qq = table_7_1["quark_quark_to_quark_quark"]
table_7_1_qqb_qpqpb = table_7_1["quark_quarkbar_to_quarkprime_quarkprimebar"]
table_7_1_qqb_qqb = table_7_1["quark_quarkbar_to_quark_quarkbar"]
table_7_1_qqb_gg = table_7_1["quark_quarkbar_to_gluon_gluon"]
table_7_1_gg_qqb = table_7_1["gluon_gluon_to_quark_quarkbar"]
table_7_1_gq_gq = table_7_1 ["gluon_quark_to_gluon_quark"]
table_7_1_gg_gg = table_7_1["gluon_gluon_to_gluon_gluon"]