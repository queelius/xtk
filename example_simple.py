#!/usr/bin/env python3
"""
Simple example usage of xtk - Expression Toolkit
"""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from xtk import Expression, E, parse_sexpr, dsl_parser


def main():
    print("=" * 60)
    print("xtk - Expression Toolkit Simple Examples")
    print("=" * 60)
    
    # Example 1: Creating and parsing expressions
    print("\n1. Creating expressions:")
    
    # Direct construction
    expr1 = Expression(['+', 'x', ['*', 2, 'y']])
    print(f"   ['+', 'x', ['*', 2, 'y']] → {expr1.to_string()}")
    
    # S-expression parsing
    expr2 = Expression(parse_sexpr("(+ x (* 2 y))"))
    print(f"   '(+ x (* 2 y))' → {expr2.to_string()}")
    
    # Infix parsing
    expr3 = Expression(dsl_parser.parse("x + 2*y"))
    print(f"   'x + 2*y' → {expr3.to_string()}")
    
    # Example 2: Pattern matching
    print("\n2. Pattern matching:")
    
    expr = Expression(['+', 'a', 'a'])
    pattern = ['+', ['?', 'x'], ['?', 'x']]  # Matches a+a where both terms are the same
    
    bindings = expr.match_pattern(pattern)
    if bindings:
        print(f"   Expression: {expr.to_string()}")
        print(f"   Pattern: {Expression(pattern).to_string()}")
        print(f"   Bindings: {bindings}")
    
    # Example 3: Transformation
    print("\n3. Transformation (a+a → 2*a):")
    
    skeleton = ['*', 2, [':', 'x']]
    transformed = expr.transform(pattern, skeleton)
    print(f"   Before: {expr.to_string()}")
    print(f"   After: {transformed.to_string()}")
    
    # Example 4: Evaluation
    print("\n4. Evaluation with bindings:")
    
    expr4 = Expression(['+', ['*', 'x', 2], 'y'])
    print(f"   Expression: {expr4.to_string()}")
    
    result = (expr4
              .bind('x', 3)
              .bind('y', 5)
              .bind('+', lambda a, b: a + b)
              .bind('*', lambda a, b: a * b)
              .evaluate())
    
    print(f"   With x=3, y=5: {result.expr}")
    
    # Example 5: LaTeX output
    print("\n5. LaTeX formatting:")
    
    expr5 = Expression(['/', ['+', 'x', 1], ['^', 'x', 2]])
    print(f"   Expression: {expr5.to_string()}")
    print(f"   LaTeX: {expr5.to_latex()}")
    
    # Example 6: Variable substitution
    print("\n6. Substitution:")
    
    expr6 = Expression(['+', 'x', ['^', 'x', 2]])
    substituted = expr6.substitute('x', 'y')
    print(f"   Original: {expr6.to_string()}")
    print(f"   x → y: {substituted.to_string()}")
    
    # Example 7: History tracking
    print("\n7. Transformation history:")
    
    expr7 = Expression(['+', 'a', 0])
    expr7 = expr7.transform(['+', ['?', 'x'], 0], [':', 'x'])
    expr7 = expr7.substitute('a', 'b')
    
    history = expr7.get_history()
    for i, step in enumerate(history):
        print(f"   Step {i}: {Expression(step).to_string() if isinstance(step, list) else step}")
    
    print("\n" + "=" * 60)
    print("For more examples, see example_usage.py")
    print("For interactive mode, run: python3 -m xtk")
    print("=" * 60)


if __name__ == '__main__':
    main()