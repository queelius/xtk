# Trigonometric Identities

This guide demonstrates how to use XTK for simplifying and proving trigonometric identities.

## Basic Trigonometric Rules

### Value Rules

```python
from xtk import rewriter

trig_value_rules = [
    # sin(0) = 0
    [['sin', 0], 0],

    # cos(0) = 1
    [['cos', 0], 1],

    # tan(0) = 0
    [['tan', 0], 0],

    # sin(pi) = 0
    [['sin', 'pi'], 0],

    # cos(pi) = -1
    [['cos', 'pi'], -1],

    # sin(pi/2) = 1
    [['sin', ['/', 'pi', 2]], 1],

    # cos(pi/2) = 0
    [['cos', ['/', 'pi', 2]], 0],
]

simplify = rewriter(trig_value_rules)

print(simplify(['sin', 0]))  # 0
print(simplify(['cos', 0]))  # 1
```

## Pythagorean Identities

### Fundamental Identity

\\(\sin^2(x) + \cos^2(x) = 1\\)

```python
pythagorean_rules = [
    [['+', ['^', ['sin', ['?', 'x']], 2],
           ['^', ['cos', ['?', 'x']], 2]], 1],

    # Rearrangements
    # sin^2(x) = 1 - cos^2(x)
    [['^', ['sin', ['?', 'x']], 2],
     ['-', 1, ['^', ['cos', [':', 'x']], 2]]],

    # cos^2(x) = 1 - sin^2(x)
    [['^', ['cos', ['?', 'x']], 2],
     ['-', 1, ['^', ['sin', [':', 'x']], 2]]],
]

simplify = rewriter(pythagorean_rules)

# Simplify sin^2(x) + cos^2(x)
expr = ['+', ['^', ['sin', 'x'], 2], ['^', ['cos', 'x'], 2]]
result = simplify(expr)
print(result)  # 1
```

### Other Pythagorean Forms

```python
extended_pythagorean = [
    # 1 + tan^2(x) = sec^2(x)
    [['+', 1, ['^', ['tan', ['?', 'x']], 2]],
     ['^', ['sec', [':', 'x']], 2]],

    # 1 + cot^2(x) = csc^2(x)
    [['+', 1, ['^', ['cot', ['?', 'x']], 2]],
     ['^', ['csc', [':', 'x']], 2]],
]
```

## Reciprocal Identities

```python
reciprocal_rules = [
    # tan(x) = sin(x) / cos(x)
    [['tan', ['?', 'x']],
     ['/', ['sin', [':', 'x']], ['cos', [':', 'x']]]],

    # cot(x) = cos(x) / sin(x)
    [['cot', ['?', 'x']],
     ['/', ['cos', [':', 'x']], ['sin', [':', 'x']]]],

    # sec(x) = 1 / cos(x)
    [['sec', ['?', 'x']],
     ['/', 1, ['cos', [':', 'x']]]],

    # csc(x) = 1 / sin(x)
    [['csc', ['?', 'x']],
     ['/', 1, ['sin', [':', 'x']]]],
]

simplify = rewriter(reciprocal_rules)

# Convert tan(x) to sin(x)/cos(x)
expr = ['tan', 'x']
result = simplify(expr)
print(result)  # ['/', ['sin', 'x'], ['cos', 'x']]
```

## Double Angle Formulas

```python
double_angle_rules = [
    # sin(2x) = 2*sin(x)*cos(x)
    [['sin', ['*', 2, ['?', 'x']]],
     ['*', 2, ['*', ['sin', [':', 'x']], ['cos', [':', 'x']]]]],

    # cos(2x) = cos^2(x) - sin^2(x)
    [['cos', ['*', 2, ['?', 'x']]],
     ['-', ['^', ['cos', [':', 'x']], 2],
           ['^', ['sin', [':', 'x']], 2]]],

    # Alternative: cos(2x) = 2*cos^2(x) - 1
    [['cos', ['*', 2, ['?', 'x']]],
     ['-', ['*', 2, ['^', ['cos', [':', 'x']], 2]], 1]],
]

simplify = rewriter(double_angle_rules)

# Expand sin(2x)
expr = ['sin', ['*', 2, 'x']]
result = simplify(expr)
print(result)  # ['*', 2, ['*', ['sin', 'x'], ['cos', 'x']]]
```

## Angle Sum/Difference Formulas

```python
sum_diff_rules = [
    # sin(a + b) = sin(a)cos(b) + cos(a)sin(b)
    [['sin', ['+', ['?', 'a'], ['?', 'b']]],
     ['+', ['*', ['sin', [':', 'a']], ['cos', [':', 'b']]],
           ['*', ['cos', [':', 'a']], ['sin', [':', 'b']]]]],

    # sin(a - b) = sin(a)cos(b) - cos(a)sin(b)
    [['sin', ['-', ['?', 'a'], ['?', 'b']]],
     ['-', ['*', ['sin', [':', 'a']], ['cos', [':', 'b']]],
           ['*', ['cos', [':', 'a']], ['sin', [':', 'b']]]]],

    # cos(a + b) = cos(a)cos(b) - sin(a)sin(b)
    [['cos', ['+', ['?', 'a'], ['?', 'b']]],
     ['-', ['*', ['cos', [':', 'a']], ['cos', [':', 'b']]],
           ['*', ['sin', [':', 'a']], ['sin', [':', 'b']]]]],

    # cos(a - b) = cos(a)cos(b) + sin(a)sin(b)
    [['cos', ['-', ['?', 'a'], ['?', 'b']]],
     ['+', ['*', ['cos', [':', 'a']], ['cos', [':', 'b']]],
           ['*', ['sin', [':', 'a']], ['sin', [':', 'b']]]]],
]
```

## Even/Odd Identities

```python
parity_rules = [
    # sin(-x) = -sin(x)
    [['sin', ['-', ['?', 'x']]],
     ['-', 0, ['sin', [':', 'x']]]],

    # cos(-x) = cos(x)
    [['cos', ['-', ['?', 'x']]],
     ['cos', [':', 'x']]],

    # tan(-x) = -tan(x)
    [['tan', ['-', ['?', 'x']]],
     ['-', 0, ['tan', [':', 'x']]]],
]

simplify = rewriter(parity_rules)

# cos(-x) simplifies to cos(x)
expr = ['cos', ['-', 'x']]
result = simplify(expr)
print(result)  # ['cos', 'x']
```

## Proving Identities

### Example: Prove \\(\sin^2(x) + \cos^2(x) = 1\\)

```python
from xtk import rewriter

# This identity is directly encoded as a rule
identity_rules = [
    [['+', ['^', ['sin', ['?', 'x']], 2],
           ['^', ['cos', ['?', 'x']], 2]], 1],
]

simplify = rewriter(identity_rules)

# The left-hand side simplifies to 1
lhs = ['+', ['^', ['sin', 'x'], 2], ['^', ['cos', 'x'], 2]]
result = simplify(lhs)

if result == 1:
    print("Identity proved: sin^2(x) + cos^2(x) = 1")
```

### Example: Prove \\(\tan(x) = \frac{\sin(x)}{\cos(x)}\\)

```python
# Use the reciprocal rule to verify
simplify = rewriter(reciprocal_rules)

tan_x = ['tan', 'x']
sin_over_cos = ['/', ['sin', 'x'], ['cos', 'x']]

# Transform tan(x) to sin(x)/cos(x)
result = simplify(tan_x)
print(result == sin_over_cos)  # True
```

## Combining with Derivatives

Differentiate trigonometric functions:

```python
from xtk.rule_loader import load_rules
from xtk import rewriter

# Load derivative rules (includes trig derivatives)
deriv_rules = load_rules('src/xtk/rules/deriv_rules.py')
simplify = rewriter(deriv_rules)

# d/dx(sin(x)) = cos(x)
expr = ['dd', ['sin', 'x'], 'x']
result = simplify(expr)
print(result)  # ['cos', 'x']

# d/dx(cos(x)) = -sin(x)
expr = ['dd', ['cos', 'x'], 'x']
result = simplify(expr)
print(result)  # ['-', 0, ['sin', 'x']]
```

## Using the REPL

```
$ python -m xtk.cli
xtk> /rules load src/xtk/rules/trig-rules.py
Loaded 16 trig rules

xtk> (sin 0)
xtk> /rw
Rewritten: 0

xtk> (+ (^ (sin x) 2) (^ (cos x) 2))
xtk> /rw
Rewritten: 1

xtk> (tan x)
xtk> /rw
Rewritten: (/ (sin x) (cos x))
```

## Complete Rule Set

Load the built-in trigonometric rules:

```python
from xtk.rule_loader import load_rules
from xtk import rewriter

# Load trig rules
trig_rules = load_rules('src/xtk/rules/trig-rules.py')
simplify = rewriter(trig_rules)

# Now you have all basic trig simplifications
```

## Hyperbolic Functions

XTK also supports hyperbolic function rules:

```python
hyperbolic_rules = [
    # sinh(-x) = -sinh(x)
    [['sinh', ['-', ['?', 'x']]],
     ['-', 0, ['sinh', [':', 'x']]]],

    # cosh(-x) = cosh(x)
    [['cosh', ['-', ['?', 'x']]],
     ['cosh', [':', 'x']]],

    # cosh^2(x) - sinh^2(x) = 1
    [['-', ['^', ['cosh', ['?', 'x']], 2],
           ['^', ['sinh', ['?', 'x']], 2]], 1],
]
```

## Next Steps

- Explore [Integration](integration.md) examples
- Learn about [Symbolic Differentiation](differentiation.md)
- See [Theorem Proving](../advanced/theorem-proving.md) for complex proofs
