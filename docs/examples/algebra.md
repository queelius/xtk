# Algebraic Simplification

This guide demonstrates how to use XTK for algebraic simplification, including identity rules, factoring, and expansion.

## Basic Simplification

### Identity Rules

Simplify expressions using algebraic identities:

```python
from xtk import rewriter

identity_rules = [
    # Additive identity
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['+', 0, ['?', 'x']], [':', 'x']],

    # Multiplicative identity
    [['*', ['?', 'x'], 1], [':', 'x']],
    [['*', 1, ['?', 'x']], [':', 'x']],

    # Multiplication by zero
    [['*', ['?', 'x'], 0], 0],
    [['*', 0, ['?', 'x']], 0],
]

simplify = rewriter(identity_rules)

# Examples
print(simplify(['+', 'x', 0]))     # 'x'
print(simplify(['*', 'y', 1]))     # 'y'
print(simplify(['*', 'z', 0]))     # 0
```

### Power Rules

```python
power_rules = [
    [['^', ['?', 'x'], 0], 1],        # x^0 = 1
    [['^', ['?', 'x'], 1], [':', 'x']], # x^1 = x
    [['^', 1, ['?', 'x']], 1],        # 1^x = 1
]

simplify = rewriter(power_rules)

print(simplify(['^', 'x', 0]))  # 1
print(simplify(['^', 'x', 1]))  # 'x'
```

## Combining Like Terms

```python
from xtk import rewriter

combine_rules = [
    # x + x = 2x
    [['+', ['?', 'x'], ['?', 'x']], ['*', 2, [':', 'x']]],

    # ax + bx = (a+b)x
    [['+', ['*', ['?c', 'a'], ['?', 'x']],
           ['*', ['?c', 'b'], ['?', 'x']]],
     ['*', ['+', [':', 'a'], [':', 'b']], [':', 'x']]],

    # x * x = x^2
    [['*', ['?', 'x'], ['?', 'x']], ['^', [':', 'x'], 2]],
]

simplify = rewriter(combine_rules)

print(simplify(['+', 'x', 'x']))
# Result: ['*', 2, 'x']

print(simplify(['+', ['*', 3, 'x'], ['*', 4, 'x']]))
# Result: ['*', 7, 'x']
```

## Factoring

### Difference of Squares

Factor \\(a^2 - b^2 = (a + b)(a - b)\\):

```python
factor_rules = [
    [['-', ['^', ['?', 'a'], 2], ['^', ['?', 'b'], 2]],
     ['*', ['+', [':', 'a'], [':', 'b']],
           ['-', [':', 'a'], [':', 'b']]]],
]

simplify = rewriter(factor_rules)

# Factor x^2 - 1
expr = ['-', ['^', 'x', 2], 1]
result = simplify(expr)
print(result)
# Result: ['*', ['+', 'x', 1], ['-', 'x', 1]]
```

### Common Factor

```python
common_factor_rules = [
    # ax + ay = a(x + y)
    [['+', ['*', ['?', 'a'], ['?', 'x']],
           ['*', ['?', 'a'], ['?', 'y']]],
     ['*', [':', 'a'], ['+', [':', 'x'], [':', 'y']]]],
]

simplify = rewriter(common_factor_rules)

# Factor 2x + 2y
expr = ['+', ['*', 2, 'x'], ['*', 2, 'y']]
result = simplify(expr)
print(result)
# Result: ['*', 2, ['+', 'x', 'y']]
```

### Perfect Square Trinomials

```python
perfect_square_rules = [
    # a^2 + 2ab + b^2 = (a + b)^2
    [['+', ['+', ['^', ['?', 'a'], 2],
                 ['*', 2, ['*', ['?', 'a'], ['?', 'b']]]],
           ['^', ['?', 'b'], 2]],
     ['^', ['+', [':', 'a'], [':', 'b']], 2]],
]
```

## Expansion

### Distributive Property

```python
distribute_rules = [
    # a(x + y) = ax + ay
    [['*', ['?', 'a'], ['+', ['?', 'x'], ['?', 'y']]],
     ['+', ['*', [':', 'a'], [':', 'x']],
           ['*', [':', 'a'], [':', 'y']]]],

    # (x + y)a = xa + ya
    [['*', ['+', ['?', 'x'], ['?', 'y']], ['?', 'a']],
     ['+', ['*', [':', 'x'], [':', 'a']],
           ['*', [':', 'y'], [':', 'a']]]],
]

simplify = rewriter(distribute_rules)

# Expand 2(x + 3)
expr = ['*', 2, ['+', 'x', 3]]
result = simplify(expr)
print(result)
# Result: ['+', ['*', 2, 'x'], ['*', 2, 3]]
```

### FOIL Method

Expand \\((a + b)(c + d)\\):

```python
foil_rules = [
    [['*', ['+', ['?', 'a'], ['?', 'b']],
           ['+', ['?', 'c'], ['?', 'd']]],
     ['+', ['+', ['+', ['*', [':', 'a'], [':', 'c']],
                       ['*', [':', 'a'], [':', 'd']]],
                       ['*', [':', 'b'], [':', 'c']]],
                       ['*', [':', 'b'], [':', 'd']]]],
]

simplify = rewriter(foil_rules)

# Expand (x + 1)(x + 2)
expr = ['*', ['+', 'x', 1], ['+', 'x', 2]]
result = simplify(expr)
# Result: x^2 + 2x + x + 2 (needs further simplification)
```

### Binomial Squares

```python
binomial_square_rules = [
    # (a + b)^2 = a^2 + 2ab + b^2
    [['^', ['+', ['?', 'a'], ['?', 'b']], 2],
     ['+', ['+', ['^', [':', 'a'], 2],
                 ['*', 2, ['*', [':', 'a'], [':', 'b']]]],
                 ['^', [':', 'b'], 2]]],

    # (a - b)^2 = a^2 - 2ab + b^2
    [['^', ['-', ['?', 'a'], ['?', 'b']], 2],
     ['+', ['-', ['^', [':', 'a'], 2],
                 ['*', 2, ['*', [':', 'a'], [':', 'b']]]],
                 ['^', [':', 'b'], 2]]],
]
```

## Complete Example

Simplify a complex algebraic expression:

```python
from xtk import rewriter
from xtk.rule_loader import load_rules

# Load all algebra rules
algebra_rules = load_rules('src/xtk/rules/algebra_rules.py')
simplify = rewriter(algebra_rules)

# Complex expression: (x + 0) * 1 + (y * 0)
expr = ['+',
    ['*', ['+', 'x', 0], 1],
    ['*', 'y', 0]
]

result = simplify(expr)
print(result)  # 'x'
```

## Polynomial Operations

### Polynomial Addition

```python
# Represent polynomials and add them
# 2x^2 + 3x + 1
poly1 = ['+', ['+', ['*', 2, ['^', 'x', 2]], ['*', 3, 'x']], 1]

# x^2 + 2x + 3
poly2 = ['+', ['+', ['^', 'x', 2], ['*', 2, 'x']], 3]

# Add them
sum_poly = ['+', poly1, poly2]
result = simplify(sum_poly)
# Result: 3x^2 + 5x + 4
```

### Polynomial Multiplication

```python
# (x + 1)(x + 2) = x^2 + 3x + 2
expr = ['*', ['+', 'x', 1], ['+', 'x', 2]]

expand = rewriter(foil_rules + combine_rules + identity_rules)
result = expand(expr)
```

## Using the REPL

```
$ python -m xtk.cli
xtk> /rules load src/xtk/rules/algebra_rules.py
Loaded algebra rules

xtk> (+ (* x 1) 0)
xtk> /rw
Rewritten: x

xtk> (- (^ x 2) 1)
xtk> /rw
Rewritten: (* (+ x 1) (- x 1))

xtk> /tree
*
+-- +
|   +-- x
|   +-- 1
+-- -
    +-- x
    +-- 1
```

## Best Practices

1. **Order rules carefully**: Identity rules before expansion
2. **Combine rule sets**: Mix simplification with expansion as needed
3. **Test incrementally**: Verify each transformation step
4. **Use constant folding**: Let the rewriter evaluate numeric constants

## Next Steps

- Explore [Trigonometric Identities](trigonometry.md)
- Learn about [Symbolic Differentiation](differentiation.md)
- Create [Custom Rules](../advanced/custom-rules.md) for your domain
