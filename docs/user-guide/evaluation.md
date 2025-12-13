# Evaluation

Evaluation computes concrete values from symbolic expressions by substituting variables and applying operations. XTK's evaluator works with a bindings dictionary that maps names to values or functions.

## Basic Evaluation

### The evaluate Function

```python
from xtk.rewriter import evaluate

# Define bindings
bindings = [
    ['x', 5],
    ['y', 3],
    ['+', lambda a, b: a + b],
    ['*', lambda a, b: a * b],
]

# Evaluate expression
expr = ['+', 'x', 'y']
result = evaluate(expr, bindings)
print(result)  # 8
```

### How It Works

1. **Variable lookup**: Replace variables with their bound values
2. **Recursive evaluation**: Evaluate sub-expressions first
3. **Function application**: Apply operator functions to evaluated arguments

## Bindings Format

Bindings are lists of `[name, value]` pairs:

```python
bindings = [
    # Variable bindings
    ['x', 10],
    ['y', 20],

    # Operator bindings
    ['+', lambda a, b: a + b],
    ['-', lambda a, b: a - b],
    ['*', lambda a, b: a * b],
    ['/', lambda a, b: a / b if b != 0 else float('inf')],
    ['^', lambda a, b: a ** b],
]
```

## Examples

### Arithmetic Evaluation

```python
from xtk.rewriter import evaluate

bindings = [
    ['+', lambda a, b: a + b],
    ['*', lambda a, b: a * b],
    ['x', 3],
]

# Evaluate 2*x + 1
expr = ['+', ['*', 2, 'x'], 1]
result = evaluate(expr, bindings)
print(result)  # 7
```

### Function Evaluation

```python
import math

bindings = [
    ['sin', math.sin],
    ['cos', math.cos],
    ['^', lambda a, b: a ** b],
    ['x', math.pi / 4],
]

# Evaluate sin(x)
expr = ['sin', 'x']
result = evaluate(expr, bindings)
print(result)  # 0.707... (sin(pi/4))
```

### Nested Expressions

```python
bindings = [
    ['+', lambda a, b: a + b],
    ['*', lambda a, b: a * b],
    ['^', lambda a, b: a ** b],
    ['x', 2],
]

# Evaluate (x + 1)^2
expr = ['^', ['+', 'x', 1], 2]
result = evaluate(expr, bindings)
print(result)  # 9
```

## Partial Evaluation

When not all variables are bound, evaluation returns a partially simplified expression:

```python
bindings = [
    ['+', lambda a, b: a + b],
    ['x', 5],
    # 'y' is not bound
]

expr = ['+', 'x', 'y']
result = evaluate(expr, bindings)
print(result)  # ['+', 5, 'y']
```

## Evaluation vs Simplification

| Feature | evaluate | rewriter (simplify) |
|---------|----------|---------------------|
| Purpose | Compute values | Transform structure |
| Input | Bindings dictionary | Rewrite rules |
| Output | Value or partial expression | Simplified expression |
| Use case | Numerical computation | Symbolic manipulation |

### Combined Usage

```python
from xtk import rewriter
from xtk.rewriter import evaluate

# First simplify symbolically
rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
simplify = rewriter(rules)
expr = ['+', ['*', 2, 'x'], 0]
simplified = simplify(expr)  # ['*', 2, 'x']

# Then evaluate numerically
bindings = [['*', lambda a, b: a * b], ['x', 5]]
result = evaluate(simplified, bindings)
print(result)  # 10
```

## Standard Bindings

Create a comprehensive set of bindings for common operations:

```python
import math

standard_bindings = [
    # Arithmetic
    ['+', lambda a, b: a + b],
    ['-', lambda a, b: a - b],
    ['*', lambda a, b: a * b],
    ['/', lambda a, b: a / b if b != 0 else float('inf')],
    ['^', lambda a, b: a ** b],

    # Trigonometric
    ['sin', math.sin],
    ['cos', math.cos],
    ['tan', math.tan],

    # Exponential/Logarithmic
    ['exp', math.exp],
    ['log', math.log],
    ['sqrt', math.sqrt],

    # Constants
    ['pi', math.pi],
    ['e', math.e],
]
```

## Error Handling

The evaluator handles errors gracefully:

```python
bindings = [
    ['/', lambda a, b: a / b if b != 0 else float('inf')],
]

# Division by zero returns infinity (or custom handling)
expr = ['/', 1, 0]
result = evaluate(expr, bindings)
print(result)  # inf
```

## Integration with Instantiate

Evaluation is used internally during skeleton instantiation:

```python
from xtk.rewriter import instantiate, evaluate

# Skeleton with substitution marker
skeleton = ['+', [':', 'x'], [':', 'y']]
bindings = [['x', 2], ['y', 3]]

# Instantiate replaces markers, evaluate computes
result = instantiate(skeleton, bindings)
print(result)  # ['+', 2, 3]
```

## Practical Applications

### Polynomial Evaluation

```python
def eval_polynomial(coeffs, x_val):
    """Evaluate polynomial with given coefficients at x_val."""
    bindings = [
        ['+', lambda a, b: a + b],
        ['*', lambda a, b: a * b],
        ['^', lambda a, b: a ** b],
        ['x', x_val],
    ]

    # Build polynomial expression
    terms = []
    for i, c in enumerate(coeffs):
        if i == 0:
            terms.append(c)
        else:
            terms.append(['*', c, ['^', 'x', i]])

    expr = terms[0]
    for term in terms[1:]:
        expr = ['+', expr, term]

    return evaluate(expr, bindings)

# 2 + 3x + x^2 at x=2
result = eval_polynomial([2, 3, 1], 2)
print(result)  # 12
```

### Derivative Verification

```python
def verify_derivative(expr, deriv, x_val, h=1e-7):
    """Numerically verify a symbolic derivative."""
    import math

    bindings = [
        ['+', lambda a, b: a + b],
        ['-', lambda a, b: a - b],
        ['*', lambda a, b: a * b],
        ['/', lambda a, b: a / b],
        ['^', lambda a, b: a ** b],
        ['sin', math.sin],
        ['cos', math.cos],
    ]

    # Evaluate derivative symbolically
    deriv_bindings = bindings + [['x', x_val]]
    symbolic_result = evaluate(deriv, deriv_bindings)

    # Numerical approximation
    f_x = evaluate(expr, bindings + [['x', x_val]])
    f_x_h = evaluate(expr, bindings + [['x', x_val + h]])
    numerical_result = (f_x_h - f_x) / h

    return abs(symbolic_result - numerical_result) < 0.001

# Verify d/dx(x^2) = 2x at x=3
print(verify_derivative(['^', 'x', 2], ['*', 2, 'x'], 3))  # True
```

## Next Steps

- Learn about [Rewrite Rules](rules.md) for symbolic transformation
- Explore [Simplification](simplification.md) strategies
- See [Differentiation](../examples/differentiation.md) examples
