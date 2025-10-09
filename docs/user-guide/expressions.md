# Expression Representation

This guide explains how XTK represents expressions using Abstract Syntax Trees (ASTs).

## The AST Model

XTK uses nested Python lists to represent expressions. This simple yet powerful representation makes expressions easy to construct, manipulate, and understand.

### Why Lists?

Using nested lists for ASTs offers several advantages:

1. **Simplicity**: No complex class hierarchies to learn
2. **Familiarity**: Python programmers already know lists
3. **Transparency**: You can see exactly what's in an expression
4. **Serialization**: Easy to save/load (JSON, pickle, etc.)
5. **Flexibility**: Works with any domain

## Basic Structure

### Atomic Expressions

Atomic expressions are the building blocks:

```python
# Constants (numbers)
42
3.14
-7
2.5e10

# Variables (strings)
'x'
'y'
'alpha'
'foo'
```

### Compound Expressions

Compound expressions are lists with an operator and operands:

```python
[operator, operand1, operand2, ...]
```

## Examples

### Arithmetic

| Mathematical | XTK Representation |
|--------------|-------------------|
| \\(5\\) | `5` |
| \\(x\\) | `'x'` |
| \\(x + 3\\) | `['+', 'x', 3]` |
| \\(2 \times x\\) | `['*', 2, 'x']` |
| \\(x - y\\) | `['-', 'x', 'y']` |
| \\(\frac{x}{2}\\) | `['/', 'x', 2]` |

### Powers and Roots

| Mathematical | XTK Representation |
|--------------|-------------------|
| \\(x^2\\) | `['^', 'x', 2]` |
| \\(x^n\\) | `['^', 'x', 'n']` |
| \\(\sqrt{x}\\) | `['^', 'x', 0.5]` or `['sqrt', 'x']` |
| \\(\sqrt[3]{x}\\) | `['^', 'x', ['/', 1, 3]]` |

### Functions

| Mathematical | XTK Representation |
|--------------|-------------------|
| \\(\sin(x)\\) | `['sin', 'x']` |
| \\(\cos(x)\\) | `['cos', 'x']` |
| \\(\ln(x)\\) | `['ln', 'x']` |
| \\(e^x\\) | `['^', 'e', 'x']` |
| \\(f(x, y)\\) | `['f', 'x', 'y']` |

### Calculus

| Mathematical | XTK Representation |
|--------------|-------------------|
| \\(\frac{d}{dx}(x^2)\\) | `['dd', ['^', 'x', 2], 'x']` |
| \\(\int x\,dx\\) | `['int', 'x', 'x']` |
| \\(\lim_{x \to 0} f(x)\\) | `['lim', ['f', 'x'], 'x', 0]` |

### Nested Expressions

Complex expressions are built by nesting:

```python
# (x + 3) * 4
['*', ['+', 'x', 3], 4]

# sin(x^2)
['sin', ['^', 'x', 2]]

# (x + y)^2
['^', ['+', 'x', 'y'], 2]

# (2*x + 1) / (x - 3)
['/', ['+', ['*', 2, 'x'], 1], ['-', 'x', 3]]
```

## Tree Structure

Expressions form tree structures:

```
    *
   / \
  +   4
 / \
x   3
```

This represents `['*', ['+', 'x', 3], 4]` or \\((x + 3) \times 4\\).

### Walking the Tree

```python
def walk(expr):
    """Recursively walk an expression tree."""
    if isinstance(expr, list):
        operator = expr[0]
        operands = expr[1:]
        print(f"Operator: {operator}")
        for operand in operands:
            walk(operand)
    else:
        print(f"Atom: {expr}")

# Example
expr = ['*', ['+', 'x', 3], 4]
walk(expr)
# Output:
# Operator: *
# Operator: +
# Atom: x
# Atom: 3
# Atom: 4
```

## Type System

XTK distinguishes between three types of atomic values:

### Constants

Numbers (integers and floats):

```python
42      # Integer constant
3.14    # Float constant
-7      # Negative constant
2.5e10  # Scientific notation
```

### Variables

Strings representing symbolic variables:

```python
'x'     # Variable x
'y'     # Variable y
'alpha' # Greek letter alpha
'foo'   # Any identifier
```

### Operators

The first element of a list is typically an operator:

```python
'+'     # Addition
'*'     # Multiplication
'sin'   # Sine function
'dd'    # Derivative operator
```

## Constructing Expressions

### Manually

Build expressions directly:

```python
# x + 3
expr = ['+', 'x', 3]

# 2*x^2 + 3*x + 1
poly = ['+',
    ['+',
        ['*', 2, ['^', 'x', 2]],
        ['*', 3, 'x']
    ],
    1
]
```

### Programmatically

Build expressions with helper functions:

```python
def binary_op(op, left, right):
    return [op, left, right]

def power(base, exp):
    return ['^', base, exp]

# x^2 + y^2
expr = binary_op('+', power('x', 2), power('y', 2))
```

### From Parser

Parse string representations (if parser is available):

```python
from xtk.parser import parse

expr = parse("2*x + 3")
# Returns: ['+', ['*', 2, 'x'], 3]
```

## Inspecting Expressions

### Type Checking

```python
from xtk.rewriter import constant, variable, compound

constant(42)              # True
constant('x')             # False

variable('x')             # True
variable(42)              # False

compound(['+', 2, 3])     # True
compound(42)              # False
```

### Decomposition

```python
from xtk.rewriter import car, cdr

expr = ['+', 'x', 'y']

operator = car(expr)      # '+'
operands = cdr(expr)      # ['x', 'y']

first_operand = car(operands)   # 'x'
second_operand = car(cdr(operands))  # 'y'
```

## Expression Equality

### Structural Equality

Python's `==` checks structural equality:

```python
expr1 = ['+', 'x', 3]
expr2 = ['+', 'x', 3]
expr1 == expr2  # True

expr3 = ['+', 3, 'x']
expr1 == expr3  # False (different order)
```

### Semantic Equality

To check semantic equality, you need to normalize:

```python
from xtk.simplifier import simplifier

rules = [...]  # Normalization rules
simplify = simplifier(rules)

expr1 = ['+', 'x', 0]
expr2 = 'x'

simplify(expr1) == simplify(expr2)  # True
```

## Best Practices

### 1. Use Consistent Operators

Choose standard operators and stick to them:

```python
# Good: standard operator names
['+', 'x', 'y']
['*', 2, 'x']

# Avoid: non-standard names
['add', 'x', 'y']
['times', 2, 'x']
```

### 2. Maintain Tree Structure

Keep expressions as trees, not graphs:

```python
# Good: tree structure
['+', ['*', 'x', 2], ['*', 'y', 3]]

# Avoid: shared sub-expressions (unless intentional)
shared = ['*', 'x', 2]
['+', shared, shared]  # Both point to same object
```

### 3. Normalize Early

Apply normalization rules early:

```python
# Convert to standard form early
def normalize(expr):
    # Apply commutativity, associativity, etc.
    return expr
```

### 4. Document Custom Operators

If you define custom operators, document them:

```python
# Custom operator: 'dot' for dot product
# Usage: ['dot', [1, 2, 3], [4, 5, 6]]
```

## Conversion to Other Formats

### To String

```python
def to_infix(expr):
    """Convert to infix string notation."""
    if isinstance(expr, list):
        op = expr[0]
        if op in ['+', '-', '*', '/', '^']:
            left = to_infix(expr[1])
            right = to_infix(expr[2])
            return f"({left} {op} {right})"
        else:
            args = ', '.join(to_infix(e) for e in expr[1:])
            return f"{op}({args})"
    else:
        return str(expr)

# Example
expr = ['+', ['*', 2, 'x'], 3]
print(to_infix(expr))  # ((2 * x) + 3)
```

### To LaTeX

```python
def to_latex(expr):
    """Convert to LaTeX notation."""
    if isinstance(expr, list):
        op = expr[0]
        if op == '+':
            return f"{to_latex(expr[1])} + {to_latex(expr[2])}"
        elif op == '*':
            return f"{to_latex(expr[1])} \\cdot {to_latex(expr[2])}"
        elif op == '^':
            return f"{to_latex(expr[1])}^{{{to_latex(expr[2])}}}"
        elif op == '/':
            return f"\\frac{{{to_latex(expr[1])}}}{{{to_latex(expr[2])}}}"
        else:
            args = ', '.join(to_latex(e) for e in expr[1:])
            return f"\\{op}({args})"
    else:
        return str(expr)
```

### From Other Formats

```python
# From SymPy
def from_sympy(sympy_expr):
    # Convert SymPy expression to XTK
    pass

# From string
def from_string(s):
    # Parse string to XTK expression
    pass
```

## Next Steps

- Learn about [Pattern Matching](pattern-matching.md) on expressions
- Explore [Rewrite Rules](rules.md) for transforming expressions
- Try [Simplification](simplification.md) techniques
