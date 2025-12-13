# Integration

This guide demonstrates symbolic integration using XTK's rule-based system.

## Basic Integration Rules

### Constant and Power Rules

```python
from xtk import rewriter

integral_rules = [
    # Integral of a constant: int(c, x) = c*x
    [['int', ['?c', 'c'], ['?v', 'x']],
     ['*', [':', 'c'], [':', 'x']]],

    # Power rule: int(x^n, x) = x^(n+1)/(n+1)
    [['int', ['^', ['?v', 'x'], ['?c', 'n']], ['?v', 'x']],
     ['/', ['^', [':', 'x'], ['+', [':', 'n'], 1]],
           ['+', [':', 'n'], 1]]],

    # Integral of x: int(x, x) = x^2/2
    [['int', ['?v', 'x'], ['?v', 'x']],
     ['/', ['^', [':', 'x'], 2], 2]],
]

integrate = rewriter(integral_rules)

# int(5, x) = 5x
expr = ['int', 5, 'x']
result = integrate(expr)
print(result)  # ['*', 5, 'x']

# int(x^2, x) = x^3/3
expr = ['int', ['^', 'x', 2], 'x']
result = integrate(expr)
print(result)  # ['/', ['^', 'x', 3], 3]
```

## Linearity Rules

```python
linearity_rules = [
    # Sum rule: int(f + g, x) = int(f, x) + int(g, x)
    [['int', ['+', ['?', 'f'], ['?', 'g']], ['?v', 'x']],
     ['+', ['int', [':', 'f'], [':', 'x']],
           ['int', [':', 'g'], [':', 'x']]]],

    # Difference rule: int(f - g, x) = int(f, x) - int(g, x)
    [['int', ['-', ['?', 'f'], ['?', 'g']], ['?v', 'x']],
     ['-', ['int', [':', 'f'], [':', 'x']],
           ['int', [':', 'g'], [':', 'x']]]],

    # Constant multiple: int(c*f, x) = c * int(f, x)
    [['int', ['*', ['?c', 'c'], ['?', 'f']], ['?v', 'x']],
     ['*', [':', 'c'], ['int', [':', 'f'], [':', 'x']]]],
]

integrate = rewriter(integral_rules + linearity_rules)

# int(3*x^2, x) = 3 * (x^3/3) = x^3
expr = ['int', ['*', 3, ['^', 'x', 2]], 'x']
result = integrate(expr)
print(result)
```

## Trigonometric Integrals

```python
trig_integral_rules = [
    # int(sin(x), x) = -cos(x)
    [['int', ['sin', ['?v', 'x']], ['?v', 'x']],
     ['-', 0, ['cos', [':', 'x']]]],

    # int(cos(x), x) = sin(x)
    [['int', ['cos', ['?v', 'x']], ['?v', 'x']],
     ['sin', [':', 'x']]],

    # int(sec^2(x), x) = tan(x)
    [['int', ['^', ['sec', ['?v', 'x']], 2], ['?v', 'x']],
     ['tan', [':', 'x']]],

    # int(csc^2(x), x) = -cot(x)
    [['int', ['^', ['csc', ['?v', 'x']], 2], ['?v', 'x']],
     ['-', 0, ['cot', [':', 'x']]]],
]

integrate = rewriter(trig_integral_rules)

# int(sin(x), x) = -cos(x)
expr = ['int', ['sin', 'x'], 'x']
result = integrate(expr)
print(result)  # ['-', 0, ['cos', 'x']]
```

## Exponential and Logarithmic Integrals

```python
exp_log_rules = [
    # int(e^x, x) = e^x
    [['int', ['exp', ['?v', 'x']], ['?v', 'x']],
     ['exp', [':', 'x']]],

    # int(1/x, x) = ln(x)
    [['int', ['/', 1, ['?v', 'x']], ['?v', 'x']],
     ['log', [':', 'x']]],

    # int(a^x, x) = a^x / ln(a)
    [['int', ['^', ['?c', 'a'], ['?v', 'x']], ['?v', 'x']],
     ['/', ['^', [':', 'a'], [':', 'x']], ['log', [':', 'a']]]],
]

integrate = rewriter(exp_log_rules)

# int(e^x, x) = e^x
expr = ['int', ['exp', 'x'], 'x']
result = integrate(expr)
print(result)  # ['exp', 'x']
```

## Complete Integration Example

Integrate a polynomial:

```python
from xtk import rewriter
from xtk.rule_loader import load_rules

# Combine all integration rules
all_rules = (
    integral_rules +
    linearity_rules +
    trig_integral_rules +
    exp_log_rules
)

integrate = rewriter(all_rules)

# Integrate 3x^2 + 2x + 1
polynomial = ['+', ['+', ['*', 3, ['^', 'x', 2]],
                         ['*', 2, 'x']],
                    1]

expr = ['int', polynomial, 'x']
result = integrate(expr)
print(result)
# Result: x^3 + x^2 + x (approximately, after simplification)
```

## Definite Integrals

For definite integrals, XTK can represent them symbolically:

```python
definite_rules = [
    # Represent definite integral
    # int(f, x, a, b) = F(b) - F(a) where F is antiderivative
    [['defint', ['?', 'f'], ['?v', 'x'], ['?', 'a'], ['?', 'b']],
     ['-', ['eval', ['int', [':', 'f'], [':', 'x']], [':', 'x'], [':', 'b']],
           ['eval', ['int', [':', 'f'], [':', 'x']], [':', 'x'], [':', 'a']]]],
]
```

## Using Built-in Rules

Load the predefined integration rules:

```python
from xtk.rule_loader import load_rules
from xtk import rewriter

# Load integration rules
int_rules = load_rules('src/xtk/rules/integral-rules.py')
integrate = rewriter(int_rules)
```

## Integration Techniques

### Substitution (u-substitution)

For simple cases, create specific rules:

```python
# int(f'(x) * g(f(x)), x) patterns
substitution_rules = [
    # int(2x * (x^2)^n, x) = (x^2)^(n+1)/(n+1)
    [['int', ['*', ['*', 2, ['?v', 'x']],
                   ['^', ['^', [':', 'x'], 2], ['?c', 'n']]],
             ['?v', 'x']],
     ['/', ['^', ['^', [':', 'x'], 2], ['+', [':', 'n'], 1]],
           ['+', [':', 'n'], 1]]],
]
```

### Integration by Parts

```python
# For specific patterns that result from integration by parts
byparts_rules = [
    # int(x * e^x, x) = e^x * (x - 1)
    [['int', ['*', ['?v', 'x'], ['exp', ['?v', 'x']]], ['?v', 'x']],
     ['*', ['exp', [':', 'x']], ['-', [':', 'x'], 1]]],

    # int(x * sin(x), x) = sin(x) - x*cos(x)
    [['int', ['*', ['?v', 'x'], ['sin', ['?v', 'x']]], ['?v', 'x']],
     ['-', ['sin', [':', 'x']], ['*', [':', 'x'], ['cos', [':', 'x']]]]],
]
```

## Verification

Verify integration by differentiating:

```python
from xtk.rule_loader import load_rules
from xtk import rewriter

# Load both derivative and integral rules
deriv_rules = load_rules('src/xtk/rules/deriv_rules.py')
int_rules = load_rules('src/xtk/rules/integral-rules.py')

integrate = rewriter(int_rules)
differentiate = rewriter(deriv_rules)

# Integrate x^2
original = ['^', 'x', 2]
integral = integrate(['int', original, 'x'])
# Result: ['/', ['^', 'x', 3], 3]

# Differentiate the result
derivative = differentiate(['dd', integral, 'x'])
# Should give back x^2
```

## Using the REPL

```
$ python -m xtk.cli
xtk> /rules load src/xtk/rules/integral-rules.py
Loaded integral rules

xtk> (int (^ x 2) x)
xtk> /rw
Rewritten: (/ (^ x 3) 3)

xtk> (int (sin x) x)
xtk> /rw
Rewritten: (- (cos x))
```

## Limitations

XTK's symbolic integration has limitations:

1. **No general algorithm**: Unlike differentiation, integration doesn't have a universal algorithm
2. **Pattern-based**: Only integrals matching defined patterns are computed
3. **No constants of integration**: Results don't include +C
4. **No numerical integration**: Use scipy for numerical integrals

For complex integrals, consider extending the rule set or using numerical methods.

## Next Steps

- Explore [Symbolic Differentiation](differentiation.md)
- Learn about [Algebraic Simplification](algebra.md)
- Create [Custom Rules](../advanced/custom-rules.md) for specific integrals
