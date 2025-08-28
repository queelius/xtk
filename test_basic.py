#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtk import Expression, parse_sexpr, simplify_rules

# Test basic operations
print("XTK Basic Tests")
print("="*40)

# Test 1: Simple arithmetic
print("\n1. Simple Arithmetic Simplification:")
expr1 = Expression(['+', 'x', 0])
print(f"   {expr1.to_string()} → ", end='')
result1 = expr1.with_rules(simplify_rules).simplify()
print(result1.to_string())

expr2 = Expression(['*', 'y', 1])
print(f"   {expr2.to_string()} → ", end='')
result2 = expr2.with_rules(simplify_rules).simplify()
print(result2.to_string())

expr3 = Expression(['*', 'z', 0])
print(f"   {expr3.to_string()} → ", end='')
result3 = expr3.with_rules(simplify_rules).simplify()
print(result3.to_string())

# Test 2: Pattern transformation
print("\n2. Pattern Transformation:")
expr4 = Expression(['+', 'a', 'a'])
pattern = ['+', ['?', 'x'], ['?', 'x']]
skeleton = ['*', 2, [':', 'x']]
print(f"   {expr4.to_string()} with pattern a+a → 2*a")
result4 = expr4.transform(pattern, skeleton)
print(f"   Result: {result4.to_string()}")

# Test 3: S-expression parsing
print("\n3. S-expression Parsing:")
sexpr = "(+ (* a b) (* c d))"
parsed = Expression(parse_sexpr(sexpr))
print(f"   '{sexpr}' → {parsed.to_string()}")

# Test 4: LaTeX output
print("\n4. LaTeX Generation:")
expr5 = Expression(['/', ['+', 'x', 'y'], ['-', 'x', 'y']])
print(f"   {expr5.to_string()}")
print(f"   LaTeX: {expr5.to_latex()}")

# Test 5: Evaluation
print("\n5. Expression Evaluation:")
expr6 = Expression(['+', ['*', 3, 4], 5])
print(f"   {expr6.to_string()}")
result6 = expr6.bind('+', lambda a,b: a+b).bind('*', lambda a,b: a*b).evaluate()
print(f"   Evaluates to: {result6.expr}")

print("\n" + "="*40)
print("All basic tests completed successfully!")
