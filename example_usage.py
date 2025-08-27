#!/usr/bin/env python3
"""
Example usage of xtk - Expression Toolkit

This demonstrates the fluent API, S-expression parsing, and symbolic computation.
"""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from xtk import (
    Expression, E, parse_sexpr, dsl_parser,
    simplify_rules, deriv_rules_fixed
)


def main():
    print("=" * 60)
    print("xtk - Expression Toolkit Examples")
    print("=" * 60)
    
    # Example 1: Basic expression creation and manipulation
    print("\n1. Creating expressions with the fluent API:")
    
    # Using ExpressionBuilder
    expr1 = E.add('x', E.multiply(2, 'y'))
    print(f"   E.add('x', E.multiply(2, 'y')) = {expr1.to_string()}")
    
    # Direct construction
    expr2 = Expression(['+', 'x', ['*', 2, 'y']])
    print(f"   Expression(['+', 'x', ['*', 2, 'y']]) = {expr2.to_string()}")
    
    # Example 2: S-expression parsing
    print("\n2. Parsing S-expressions:")
    
    sexpr_str = "(+ (* 2 x) (^ x 2))"
    expr3 = Expression(parse_sexpr(sexpr_str))
    print(f"   parse_sexpr('{sexpr_str}') = {expr3.to_string()}")
    
    # Example 3: DSL parsing (infix notation)
    print("\n3. Parsing infix notation (DSL):")
    
    dsl_str = "2*x + x^2"
    expr4 = Expression(dsl_parser.parse(dsl_str))
    print(f"   dsl_parser.parse('{dsl_str}') = {expr4.to_string()}")
    
    # Example 4: Algebraic simplification
    print("\n4. Algebraic simplification:")
    
    expr5 = Expression(['+', ['*', 'x', 1], 0])  # x*1 + 0
    print(f"   Original: {expr5.to_string()}")
    simplified = expr5.with_rules(simplify_rules).simplify()
    print(f"   Simplified: {simplified.to_string()}")
    
    # Example 5: Symbolic differentiation
    print("\n5. Symbolic differentiation:")
    
    # d/dx(x^2 + 3*x + 2)
    expr6 = Expression(['+', ['+', ['^', 'x', 2], ['*', 3, 'x']], 2])
    print(f"   f(x) = {expr6.to_string()}")
    
    deriv = expr6.differentiate('x')
    print(f"   f'(x) = {deriv.to_string()}")
    
    # Example 6: Pattern matching and transformation
    print("\n6. Pattern matching and transformation:")
    
    expr7 = Expression(['+', 'a', 'a'])
    print(f"   Original: {expr7.to_string()}")
    
    # Transform a + a to 2*a
    pattern = ['+', ['?', 'x'], ['?', 'x']]
    skeleton = ['*', 2, [':', 'x']]
    transformed = expr7.transform(pattern, skeleton)
    print(f"   After transform (a+a → 2a): {transformed.to_string()}")
    
    # Example 7: Evaluation with bindings
    print("\n7. Evaluation with bindings:")
    
    expr8 = Expression(['+', ['*', 'x', 'y'], 3])
    print(f"   Expression: {expr8.to_string()}")
    
    evaluated = expr8.bind('x', 4).bind('y', 5).bind('+', lambda a, b: a + b).bind('*', lambda a, b: a * b).evaluate()
    print(f"   With x=4, y=5: {evaluated.expr}")
    
    # Example 8: LaTeX output
    print("\n8. LaTeX output:")
    
    expr9 = Expression(['/', ['+', 'x', 1], ['-', 'x', 1]])
    print(f"   Expression: {expr9.to_string()}")
    print(f"   LaTeX: {expr9.to_latex()}")
    
    # Example 9: Substitution
    print("\n9. Variable substitution:")
    
    expr10 = Expression(['+', ['^', 'x', 2], 'x'])
    print(f"   Original: {expr10.to_string()}")
    
    substituted = expr10.substitute('x', ['+', 'a', 'b'])
    print(f"   After x → (a+b): {substituted.to_string()}")
    
    # Example 10: Chain of operations
    print("\n10. Chaining operations:")
    
    result = (Expression(['*', 'x', 'x'])  # x*x
              .transform(['*', ['?', 'a'], ['?', 'a']], ['^', [':', 'a'], 2])  # a*a → a^2
              .differentiate('x')  # d/dx
              .with_rules(simplify_rules)
              .simplify())
    
    print(f"   d/dx(x*x) with transformations = {result.to_string()}")
    
    print("\n" + "=" * 60)
    print("For interactive exploration, run: python3 -m xtk")
    print("=" * 60)


if __name__ == '__main__':
    main()