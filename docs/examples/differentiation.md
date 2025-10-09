# Symbolic Differentiation

This example demonstrates how to use XTK for symbolic differentiation, one of its most powerful applications.

## Overview

Symbolic differentiation computes derivatives of expressions symbolically (not numerically). XTK implements differentiation through rewrite rules based on calculus rules.

## Basic Differentiation

### Derivative of a Constant

The derivative of a constant is always zero: \\(\frac{d}{dx}(c) = 0\\)

```python
from xtk import rewriter
from xtk.rule_loader import load_rules

# Load derivative rules
rules = load_rules('src/xtk/rules/deriv_rules.py')
diff = rewriter(rules)

# Differentiate a constant
expr = ['dd', 5, 'x']  # d/dx(5)
result = diff(expr)
print(result)  # 0
```

### Derivative of a Variable

The derivative of a variable with respect to itself is 1: \\(\frac{d}{dx}(x) = 1\\)

```python
expr = ['dd', 'x', 'x']  # d/dx(x)
result = diff(expr)
print(result)  # 1
```

## Power Rule

The power rule: \\(\frac{d}{dx}(x^n) = n \cdot x^{n-1}\\)

```python
# d/dx(x^2) = 2*x^1 = 2*x
expr = ['dd', ['^', 'x', 2], 'x']
result = diff(expr)
print(result)  # ['*', 2, ['^', 'x', 1]]

# Simplify further
from xtk.simplifier import simplifier
simplify = simplifier(rules)
result = simplify(result)
print(result)  # ['*', 2, 'x']

# d/dx(x^3) = 3*x^2
expr = ['dd', ['^', 'x', 3], 'x']
result = diff(expr)
print(result)  # ['*', 3, ['^', 'x', 2]]
```

## Sum Rule

The sum rule: \\(\frac{d}{dx}(f + g) = \frac{df}{dx} + \frac{dg}{dx}\\)

```python
# d/dx(x^2 + x^3)
expr = ['dd', ['+', ['^', 'x', 2], ['^', 'x', 3]], 'x']
result = simplify(expr)
print(result)
# ['+', ['*', 2, 'x'], ['*', 3, ['^', 'x', 2]]]
```

## Product Rule

The product rule: \\(\frac{d}{dx}(f \cdot g) = \frac{df}{dx} \cdot g + f \cdot \frac{dg}{dx}\\)

```python
# d/dx(x * x) = 1*x + x*1 = 2x
expr = ['dd', ['*', 'x', 'x'], 'x']
result = simplify(expr)
print(result)  # ['*', 2, 'x'] or equivalent
```

### Example: Derivative of \\(x^2 \cdot x^3\\)

```python
expr = ['dd', ['*', ['^', 'x', 2], ['^', 'x', 3]], 'x']
result = simplify(expr)
# Result: ['*', 5, ['^', 'x', 4]]
# (This uses both product rule and simplification)
```

## Chain Rule

The chain rule: \\(\frac{d}{dx}(f(g(x))) = f'(g(x)) \cdot g'(x)\\)

```python
# d/dx((x^2)^3) = 3*(x^2)^2 * 2*x
expr = ['dd', ['^', ['^', 'x', 2], 3], 'x']
result = simplify(expr)
print(result)
# Simplified: ['*', 6, ['^', 'x', 5]]
```

## Trigonometric Functions

### Derivative of sin(x)

\\(\frac{d}{dx}(\sin(x)) = \cos(x)\\)

```python
# Load trigonometric rules too
trig_rules = load_rules('src/xtk/rules/trig_rules.py')
all_rules = rules + trig_rules
diff_trig = simplifier(all_rules)

expr = ['dd', ['sin', 'x'], 'x']
result = diff_trig(expr)
print(result)  # ['cos', 'x']
```

### Derivative of cos(x)

\\(\frac{d}{dx}(\cos(x)) = -\sin(x)\\)

```python
expr = ['dd', ['cos', 'x'], 'x']
result = diff_trig(expr)
print(result)  # ['-', 0, ['sin', 'x']] or equivalent
```

## Complete Example: Polynomial Derivative

Let's differentiate a complete polynomial: \\(f(x) = 3x^3 + 2x^2 - 5x + 7\\)

```python
from xtk import rewriter
from xtk.rule_loader import load_rules
from xtk.simplifier import simplifier

# Setup
rules = load_rules('src/xtk/rules/deriv_rules.py')
algebra_rules = load_rules('src/xtk/rules/algebra_rules.py')
all_rules = rules + algebra_rules
simplify = simplifier(all_rules)

# Define the polynomial
polynomial = ['+',
    ['+',
        ['*', 3, ['^', 'x', 3]],
        ['*', 2, ['^', 'x', 2]]
    ],
    ['+',
        ['*', -5, 'x'],
        7
    ]
]

# Differentiate
expr = ['dd', polynomial, 'x']
result = simplify(expr)

print("Derivative:")
print(result)
# Expected: 9x^2 + 4x - 5
# Output: ['+', ['+', ['*', 9, ['^', 'x', 2]], ['*', 4, 'x']], -5]
```

## Using the REPL for Differentiation

The interactive REPL makes differentiation even easier:

```
$ python -m xtk.cli
xtk> /rules load src/xtk/rules/deriv_rules.py
Loaded 15 derivative rules

xtk> (dd (^ x 2) x)
Expression: ['dd', ['^', 'x', 2], 'x']

xtk> /simplify
Simplified: ['*', 2, 'x']

xtk> /tree
*
├── 2
└── x
```

## Advanced: Multiple Variables

XTK supports partial derivatives with multiple variables:

```python
# ∂/∂x(x*y) = y
expr = ['dd', ['*', 'x', 'y'], 'x']
result = diff(expr)
print(result)  # 'y'

# ∂/∂y(x*y) = x
expr = ['dd', ['*', 'x', 'y'], 'y']
result = diff(expr)
print(result)  # 'x'

# ∂/∂x(x^2 + y^2) = 2x
expr = ['dd', ['+', ['^', 'x', 2], ['^', 'y', 2]], 'x']
result = simplify(expr)
print(result)  # ['*', 2, 'x']
```

## Building Custom Differentiation Rules

You can extend the differentiation rules:

```python
custom_rules = [
    # d/dx(e^x) = e^x
    [['dd', ['^', 'e', ['?v', 'x']], ['?v', 'x']],
     ['^', 'e', [':', 'x']]],

    # d/dx(ln(x)) = 1/x
    [['dd', ['ln', ['?v', 'x']], ['?v', 'x']],
     ['/', 1, [':', 'x']]],

    # d/dx(tan(x)) = sec^2(x)
    [['dd', ['tan', ['?v', 'x']], ['?v', 'x']],
     ['^', ['sec', [':', 'x']], 2]],
]

# Combine with existing rules
extended_rules = rules + custom_rules
diff_extended = simplifier(extended_rules)

# Use extended differentiation
expr = ['dd', ['^', 'e', 'x'], 'x']
result = diff_extended(expr)
print(result)  # ['^', 'e', 'x']
```

## Practical Applications

### 1. Finding Critical Points

```python
def find_critical_points_symbolic(func, var):
    """Return the derivative of func with respect to var."""
    deriv_expr = ['dd', func, var]
    return simplify(deriv_expr)

# f(x) = x^3 - 3x^2 + 2
func = ['+', ['-', ['^', 'x', 3], ['*', 3, ['^', 'x', 2]]], 2]
critical = find_critical_points_symbolic(func, 'x')
print("f'(x) =", critical)
# Output: 3x^2 - 6x
# Critical points where this equals 0: x=0, x=2
```

### 2. Taylor Series (First Term)

```python
def taylor_first_order(func, var, point):
    """First-order Taylor approximation: f(a) + f'(a)(x-a)"""
    # This is conceptual - you'd need evaluation rules
    deriv = ['dd', func, var]
    return ['+',
        ['eval', func, {var: point}],
        ['*', ['eval', deriv, {var: point}], ['-', var, point]]
    ]
```

### 3. Gradient Descent Step

```python
def gradient_step(func, var):
    """Compute gradient descent update direction."""
    return ['dd', func, var]

# For f(x) = x^2, gradient is 2x
# Update: x_new = x - α * 2x
```

## Error Handling

```python
# If derivative rules aren't loaded
try:
    expr = ['dd', ['^', 'x', 2], 'x']
    result = diff(expr)
    if result == expr:  # No change means rule didn't apply
        print("Warning: Derivative rules may not be loaded")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **Load rules once**: Don't reload rules for each differentiation
2. **Simplify after**: Apply simplification after differentiation
3. **Use specific rules**: More specific rules match faster
4. **Cache results**: Store computed derivatives for reuse

## Common Issues

### Issue: Derivative Not Simplifying

**Problem**: `['*', 1, 'x']` instead of `'x'`

**Solution**: Load algebra rules for simplification:

```python
algebra_rules = load_rules('src/xtk/rules/algebra_rules.py')
all_rules = deriv_rules + algebra_rules
simplify = simplifier(all_rules)
```

### Issue: Chain Rule Not Applying

**Problem**: Nested functions not differentiating correctly

**Solution**: Ensure you have chain rule in your rules and use `simplifier()` instead of `rewriter()`:

```python
from xtk.simplifier import simplifier
simplify = simplifier(rules)  # Applies rules recursively
```

## Next Steps

- Try [Integration](integration.md) examples
- Learn about [Algebraic Simplification](algebra.md)
- Explore [Trigonometric Identities](trigonometry.md)
- Read about [Custom Rules](../advanced/custom-rules.md)

## References

- [Core API Documentation](../api/core.md)
- [Simplifier API](../api/simplifier.md)
- [Pattern Matching Guide](../user-guide/pattern-matching.md)
