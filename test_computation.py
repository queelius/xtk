#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtk import Expression, E, parse_sexpr, simplify_rules, deriv_rules_fixed

# Test 1: Symbolic differentiation
print("1. Symbolic Differentiation:")
expr = E.add(E.power('x', 3), E.multiply(2, E.power('x', 2)), 'x')
print(f"   f(x) = {expr.to_string()}")
print(f"   f(x) = {expr.to_latex()} (LaTeX)")

deriv = expr.differentiate('x')
print(f"   f'(x) = {deriv.to_string()}")

# Test 2: Algebraic simplification  
print("\n2. Algebraic Simplification:")
expr2 = Expression(parse_sexpr("(+ (+ (* x 1) (* 0 y)) (+ 0 z))"))
print(f"   Original: {expr2.to_string()}")

simplified = expr2.with_rules(simplify_rules).simplify()
print(f"   Simplified: {simplified.to_string()}")

# Test 3: Pattern matching and transformation
print("\n3. Pattern Matching:")
expr3 = Expression(['+', ['*', 2, 'x'], ['*', 2, 'x']])
print(f"   Expression: {expr3.to_string()}")

pattern = ['+', ['*', ['?c', 'a'], ['?', 'x']], ['*', ['?c', 'a'], ['?', 'x']]]
skeleton = ['*', ['*', 2, [':', 'a']], [':', 'x']]

bindings = expr3.match_pattern(pattern)
if bindings:
    print(f"   Matched! Bindings: {bindings}")
    transformed = expr3.transform(pattern, skeleton)
    print(f"   Transformed: {transformed.to_string()}")

# Test 4: Evaluation
print("\n4. Evaluation:")
expr4 = Expression(['^', ['+', 'x', 1], 2])
print(f"   Expression: {expr4.to_string()}")

result = expr4.bind('x', 3).bind('+', lambda a,b: a+b).bind('^', lambda a,b: a**b).evaluate()
print(f"   With x=3: {result.expr}")

# Test 5: Complex expression
print("\n5. Complex Expression:")
complex_expr = parse_sexpr("(dd (* (sin x) (cos y)) x)")
print(f"   ∂/∂x[sin(x)·cos(y)] = {Expression(complex_expr).to_string()}")
