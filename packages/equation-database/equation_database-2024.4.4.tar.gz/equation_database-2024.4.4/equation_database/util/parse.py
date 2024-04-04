import sympy 
from sympy.parsing.sympy_parser import parse_expr

def frac(s :str) -> sympy.Rational:
    r = parse_expr(s)
    assert r.is_rational
    return r