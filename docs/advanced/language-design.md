# Language Design

XTK's rule-based system enables you to design domain-specific languages (DSLs) for symbolic computation. This guide covers principles and techniques for effective language design.

## DSL Fundamentals

A domain-specific language in XTK consists of:

1. **Operators**: The vocabulary of your language
2. **Rules**: The grammar and semantics
3. **Expressions**: The sentences

## Designing Your Language

### Step 1: Define the Domain

Identify what your language should express:

- Mathematical formulas
- Logic expressions
- State machines
- Domain-specific computations

### Step 2: Choose Operators

Select operators that naturally express domain concepts:

```python
# Calculus DSL
operators = {
    'dd': 'derivative',
    'int': 'integral',
    'lim': 'limit',
    '+': 'sum',
    '*': 'product',
    '^': 'power',
}
```

### Step 3: Define Semantics via Rules

Create rules that define how operators behave:

```python
# Derivative semantics
derivative_rules = [
    [['dd', ['?c', 'c'], ['?v', 'x']], 0],
    [['dd', ['?v', 'x'], ['?v', 'x']], 1],
    [['dd', ['+', ['?', 'f'], ['?', 'g']], ['?v', 'x']],
     ['+', ['dd', [':', 'f'], [':', 'x']],
           ['dd', [':', 'g'], [':', 'x']]]],
]
```

## Expression Representation

### AST Structure

XTK uses nested lists as abstract syntax trees:

```python
# Mathematical: 2x + 3
['+', ['*', 2, 'x'], 3]

# Structure:
#      +
#     / \
#    *   3
#   / \
#  2   x
```

### Conventions

Adopt consistent conventions:

```python
# Binary operations: [op, left, right]
['+', 'a', 'b']
['*', 'x', 'y']

# Unary operations: [op, arg]
['sin', 'x']
['not', 'p']

# N-ary operations: [op, arg1, arg2, ..., argn]
['sum', 1, 2, 3, 4, 5]
```

## Turing Completeness

XTK's rule system is Turing-complete. You can implement any computable function.

### Example: Factorial

```python
factorial_rules = [
    # Base case: fact(0) = 1
    [['fact', 0], 1],

    # Recursive case: fact(n) = n * fact(n-1)
    [['fact', ['?c', 'n']],
     ['*', [':', 'n'], ['fact', ['-', [':', 'n'], 1]]]],
]

# Usage
simplify = rewriter(factorial_rules + arithmetic_rules)
result = simplify(['fact', 5])  # 120
```

### Example: Fibonacci

```python
fib_rules = [
    # Base cases
    [['fib', 0], 0],
    [['fib', 1], 1],

    # Recursive case
    [['fib', ['?c', 'n']],
     ['+', ['fib', ['-', [':', 'n'], 1]],
           ['fib', ['-', [':', 'n'], 2]]]],
]
```

## Language Layers

Build complex languages from simple components:

### Layer 1: Primitives

```python
primitive_rules = [
    [['+', ['?c', 'a'], ['?c', 'b']], ['add', [':', 'a'], [':', 'b']]],
    [['*', ['?c', 'a'], ['?c', 'b']], ['mul', [':', 'a'], [':', 'b']]],
]
```

### Layer 2: Derived Operations

```python
derived_rules = [
    # Square: sq(x) = x^2
    [['sq', ['?', 'x']], ['^', [':', 'x'], 2]],

    # Cube: cube(x) = x^3
    [['cube', ['?', 'x']], ['^', [':', 'x'], 3]],

    # Double: dbl(x) = 2*x
    [['dbl', ['?', 'x']], ['*', 2, [':', 'x']]],
]
```

### Layer 3: Domain Concepts

```python
physics_rules = [
    # Kinetic energy: KE = (1/2)mv^2
    [['KE', ['?', 'm'], ['?', 'v']],
     ['*', ['/', 1, 2], ['*', [':', 'm'], ['^', [':', 'v'], 2]]]],

    # Force: F = ma
    [['F', ['?', 'm'], ['?', 'a']],
     ['*', [':', 'm'], [':', 'a']]],
]
```

## Declarative vs Imperative

XTK encourages declarative programming:

### Imperative (traditional)

```python
def simplify_add(expr):
    if isinstance(expr, list) and expr[0] == '+':
        if expr[2] == 0:
            return expr[1]
        if expr[1] == 0:
            return expr[2]
    return expr
```

### Declarative (XTK)

```python
add_rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['+', 0, ['?', 'x']], [':', 'x']],
]
```

Benefits of declarative style:

- **Concise**: Rules state what, not how
- **Composable**: Easily combine rule sets
- **Readable**: Mathematical notation
- **Maintainable**: Rules are independent

## Type Systems

Implement type checking through pattern constraints:

### Simple Type Constraints

```python
typed_rules = [
    # Only apply to constants
    [['+', ['?c', 'a'], ['?c', 'b']], ...],

    # Only apply to variables
    [['dd', ['?v', 'x'], ['?v', 'x']], 1],
]
```

### Custom Type Predicates

```python
from xtk.rewriter import constant, variable, compound

def is_polynomial(expr):
    """Check if expression is a polynomial."""
    if constant(expr) or variable(expr):
        return True
    if compound(expr):
        op = expr[0]
        if op in ['+', '-', '*']:
            return all(is_polynomial(arg) for arg in expr[1:])
        if op == '^' and constant(expr[2]) and expr[2] >= 0:
            return is_polynomial(expr[1])
    return False
```

## Error Handling

Design your language to handle errors gracefully:

```python
error_rules = [
    # Division by zero
    [['/', ['?', 'x'], 0], ['error', 'division_by_zero']],

    # Invalid logarithm
    [['log', 0], ['error', 'log_of_zero']],

    # Propagate errors
    [['+', ['error', ['?', 'e']], ['?', 'y']], ['error', [':', 'e']]],
    [['+', ['?', 'x'], ['error', ['?', 'e']]], ['error', [':', 'e']]],
]
```

## Optimization

Design efficient languages:

### Normalization

Convert to canonical forms for faster matching:

```python
normalization_rules = [
    # Constants to the right
    [['+', ['?c', 'c'], ['?v', 'x']], ['+', [':', 'x'], [':', 'c']]],

    # Flatten nested operations
    [['+', ['+', ['?', 'a'], ['?', 'b']], ['?', 'c']],
     ['+', [':', 'a'], ['+', [':', 'b'], [':', 'c']]]],
]
```

### Short-Circuit Evaluation

```python
shortcircuit_rules = [
    # and(false, x) = false (don't evaluate x)
    [['and', False, ['?', 'x']], False],

    # or(true, x) = true
    [['or', True, ['?', 'x']], True],
]
```

## Best Practices

1. **Start small**: Begin with core operations, extend gradually
2. **Be consistent**: Use uniform conventions for operators
3. **Document**: Provide clear descriptions of each operator
4. **Test thoroughly**: Verify all rule combinations
5. **Consider efficiency**: Order rules for common cases first
6. **Handle edge cases**: Define behavior for boundary conditions
7. **Use layers**: Build complex operations from simple ones

## Example: Matrix DSL

```python
matrix_rules = [
    # Identity: A * I = A
    [['matmul', ['?', 'A'], 'I'], [':', 'A']],

    # Zero: A * 0 = 0
    [['matmul', ['?', 'A'], 'O'], 'O'],

    # Transpose of transpose
    [['transpose', ['transpose', ['?', 'A']]], [':', 'A']],

    # Transpose of product
    [['transpose', ['matmul', ['?', 'A'], ['?', 'B']]],
     ['matmul', ['transpose', [':', 'B']], ['transpose', [':', 'A']]]],
]
```

## Next Steps

- Explore [Custom Rules](custom-rules.md) in depth
- Study [Theorem Proving](theorem-proving.md) applications
- See [Examples](../examples/differentiation.md) for inspiration
