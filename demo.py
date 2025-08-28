#!/usr/bin/env python3
"""
XTK Demo - Showcasing the Expression Toolkit
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtk import Expression, E, parse_sexpr

def demo_header(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

# Main demo
print("""
╔══════════════════════════════════════════════════╗
║     XTK - Expression Toolkit Demonstration      ║
║         Symbolic Computation in Python          ║
╚══════════════════════════════════════════════════╝
""")

demo_header("1. MULTIPLE INPUT FORMATS")

# S-expression
expr1 = Expression(parse_sexpr("(+ (* 2 x) y)"))
print(f"S-expr:  (+ (* 2 x) y)")
print(f"Result:  {expr1.to_string()}")

# Builder API
expr2 = E.add(E.multiply(2, 'x'), 'y')
print(f"Builder: E.add(E.multiply(2, 'x'), 'y')")
print(f"Result:  {expr2.to_string()}")

# Direct construction
expr3 = Expression(['+', ['*', 2, 'x'], 'y'])
print(f"Direct:  Expression(['+', ['*', 2, 'x'], 'y'])")
print(f"Result:  {expr3.to_string()}")

demo_header("2. PATTERN MATCHING & TRANSFORMATION")

expr = Expression(['+', 'x', 'x'])
print(f"Original: {expr.to_string()}")

pattern = ['+', ['?', 'a'], ['?', 'a']]
skeleton = ['*', 2, [':', 'a']]
result = expr.transform(pattern, skeleton)
print(f"Pattern:  a + a → 2*a")
print(f"Result:   {result.to_string()}")

demo_header("3. SYMBOLIC SIMPLIFICATION")

complex_expr = Expression(['+', ['*', 'x', 1], ['+', 0, ['*', 'y', 0]]])
print(f"Original:   {complex_expr.to_string()}")

from xtk import simplify_rules
simplified = complex_expr.with_rules(simplify_rules).simplify()
print(f"Simplified: {simplified.to_string()}")

demo_header("4. EXPRESSION EVALUATION")

expr = Expression(['+', ['*', 'x', 'y'], ['^', 'x', 2]])
print(f"Expression: {expr.to_string()}")

result = (expr
    .bind('x', 3)
    .bind('y', 4)
    .bind('+', lambda a,b: a+b)
    .bind('*', lambda a,b: a*b)
    .bind('^', lambda a,b: a**b)
    .evaluate())

print(f"With x=3, y=4: {result.expr}")

demo_header("5. OUTPUT FORMATS")

expr = Expression(['/', ['-', ['^', 'x', 2], 1], ['+', 'x', 1]])

print(f"S-expression: {expr.to_string()}")
print(f"LaTeX:        {expr.to_latex()}")

demo_header("6. TRANSFORMATION HISTORY")

expr = Expression(['+', 'a', 0])
expr = expr.transform(['+', ['?', 'x'], 0], [':', 'x'])
expr = expr.substitute('a', 'b')
expr = expr.transform(['?v', 'x'], ['^', [':', 'x'], 2])

print("Transformation steps:")
for i, step in enumerate(expr.get_history()):
    if isinstance(step, list):
        print(f"  Step {i}: {Expression(step).to_string()}")
    else:
        print(f"  Step {i}: {step}")

print("""
╔══════════════════════════════════════════════════╗
║  For more examples: python3 example_simple.py   ║
║  Interactive REPL:  python3 -m src.xtk          ║
║  Documentation:     See README.md               ║
╚══════════════════════════════════════════════════╝
""")
