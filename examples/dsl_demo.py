#!/usr/bin/env python3
"""
Demonstration of XTK's multiple DSL formats for human-friendly expression input.

XTK supports three ways to write expressions:
1. JSON/Python lists (programmatic, most precise)
2. S-expressions (Lisp-like, clean and unambiguous)
3. Infix notation (natural mathematical syntax)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtk.parser import parse_sexpr, parse_dsl, dsl_parser, format_sexpr
from xtk.fluent_api import Expression
from xtk.rewriter import simplifier
from xtk.rules.algebra_rules import simplify_rules


def demo_sexpr():
    """Demonstrate S-expression (Lisp-like) syntax."""
    print("\n" + "="*60)
    print("S-EXPRESSION (LISP-LIKE) SYNTAX")
    print("="*60)
    
    examples = [
        ("(+ x y)", "Simple addition"),
        ("(* 2 (+ x 3))", "Multiplication with nested expression"),
        ("(/ (- b) (* 2 a))", "Complex fraction: -b / (2*a)"),
        ("(deriv (* x x) x)", "Derivative of x²"),
        ("(= y (+ (* m x) b))", "Equation: y = mx + b"),
    ]
    
    for sexpr_str, description in examples:
        expr = parse_sexpr(sexpr_str)
        print(f"\n{description}:")
        print(f"  Input:  {sexpr_str}")
        print(f"  Parsed: {expr}")
        print(f"  Format: {format_sexpr(expr)}")


def demo_infix():
    """Demonstrate infix mathematical notation."""
    print("\n" + "="*60)
    print("INFIX MATHEMATICAL NOTATION")
    print("="*60)
    
    examples = [
        ("x + y", "Simple addition"),
        ("2 * (x + 3)", "Multiplication with parentheses"),
        ("x^2 + 3*x - 5", "Polynomial with precedence"),
        ("sin(x) + cos(y)", "Trigonometric functions"),
        ("(a + b) * (c - d)", "Multiple grouped operations"),
    ]
    
    for infix_str, description in examples:
        # Basic parser
        expr_basic = parse_dsl(infix_str)
        # Advanced parser with precedence
        expr_advanced = dsl_parser.parse(infix_str)
        
        print(f"\n{description}:")
        print(f"  Input:    {infix_str}")
        print(f"  Basic:    {expr_basic}")
        print(f"  Advanced: {expr_advanced}")
        print(f"  S-expr:   {format_sexpr(expr_advanced)}")


def demo_json_ast():
    """Demonstrate native JSON/list AST format."""
    print("\n" + "="*60)
    print("NATIVE JSON/LIST AST FORMAT")
    print("="*60)
    
    examples = [
        (['+', 'x', 'y'], "Direct list notation"),
        (['*', 2, ['+', 'x', 3]], "Nested lists"),
        (['+', ['*', 'a', 'x'], 'b'], "ax + b"),
        (['?', 'x'], "Pattern variable"),
        ([':', 'x'], "Skeleton substitution"),
    ]
    
    for expr, description in examples:
        print(f"\n{description}:")
        print(f"  Python:  {expr}")
        print(f"  S-expr:  {format_sexpr(expr)}")


def demo_rules_in_dsl():
    """Demonstrate rule definition in different formats."""
    print("\n" + "="*60)
    print("RULE DEFINITIONS IN DIFFERENT FORMATS")
    print("="*60)
    
    print("\n1. JSON/List format (most precise):")
    rule_json = [
        [['+', ['?', 'x'], 0], [':', 'x']],  # x + 0 → x
        [['*', ['?', 'x'], 1], [':', 'x']],  # x * 1 → x
    ]
    print(f"   {rule_json}")
    
    print("\n2. S-expression format (clean and clear):")
    rule_sexpr = """
    ;; Identity rules
    ((+ (? x) 0) (: x))  ; x + 0 → x
    ((* (? x) 1) (: x))  ; x * 1 → x
    """
    print(rule_sexpr)
    
    print("\n3. Loading rules from S-expressions:")
    rule_str = "(+ (? x) 0)"
    pattern = parse_sexpr(rule_str)
    print(f"   Pattern: {rule_str} → {pattern}")


def demo_fluent_api_with_dsl():
    """Show how DSL integrates with the fluent API."""
    print("\n" + "="*60)
    print("FLUENT API WITH DSL INPUT")
    print("="*60)
    
    # Create expression from S-expression
    expr1 = Expression(parse_sexpr("(+ (* x 2) 0)"))
    print(f"\nFrom S-expr: {format_sexpr(expr1.expr)}")
    result1 = expr1.simplify(rules=simplify_rules)
    print(f"Simplified:  {format_sexpr(result1.expr)}")
    
    # Create expression from infix
    expr2 = Expression(dsl_parser.parse("x^2 + 2*x + 1"))
    print(f"\nFrom infix:  x^2 + 2*x + 1")
    print(f"As S-expr:   {format_sexpr(expr2.expr)}")
    
    # Pattern matching with DSL
    pattern = parse_sexpr("(+ (? a) (? b))")
    expr3 = Expression(parse_sexpr("(+ 3 5)"))
    if expr3.matches(pattern):
        print(f"\nPattern (+ (? a) (? b)) matches (+ 3 5)")
        print(f"Bindings: {expr3.get_bindings()}")


def demo_conversion():
    """Show conversion between formats."""
    print("\n" + "="*60)
    print("FORMAT CONVERSION")
    print("="*60)
    
    original = "2 * (x + 3)"
    print(f"\nOriginal infix: {original}")
    
    # Infix → AST
    ast = dsl_parser.parse(original)
    print(f"As AST:         {ast}")
    
    # AST → S-expression
    sexpr = format_sexpr(ast)
    print(f"As S-expr:      {sexpr}")
    
    # S-expression → AST (round trip)
    ast2 = parse_sexpr(sexpr)
    print(f"Back to AST:    {ast2}")
    
    # Verify round trip
    print(f"Round trip OK:  {ast == ast2}")


def main():
    """Run all DSL demonstrations."""
    print("\nXTK DSL (Domain Specific Language) Demonstration")
    print("=" * 60)
    print("\nXTK provides multiple ways to write expressions:")
    print("  1. JSON/Lists - Most precise, best for programs")
    print("  2. S-expressions - Clean, unambiguous, Lisp-like")
    print("  3. Infix notation - Natural mathematical syntax")
    
    demo_json_ast()
    demo_sexpr()
    demo_infix()
    demo_rules_in_dsl()
    demo_fluent_api_with_dsl()
    demo_conversion()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("""
The relationship between formats:
  
  Infix DSL:      "x + 2*y"
       ↓ parse_dsl() / dsl_parser.parse()
  S-expression:   "(+ x (* 2 y))"
       ↓ parse_sexpr()
  JSON/AST:       ['+', 'x', ['*', 2, 'y']]
       ↓ format_sexpr()
  S-expression:   "(+ x (* 2 y))"
  
All formats are equivalent and can be used interchangeably!
""")


if __name__ == "__main__":
    main()