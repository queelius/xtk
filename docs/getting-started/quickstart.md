# Quick Start Guide

This guide will get you started with XTK in just a few minutes.

## Your First Expression Rewrite

Let's start with a simple example that demonstrates the core concept of XTK:

```python
from xtk import rewriter

# Define a simple rewrite rule: x + 0 => x
rules = [
    [['+', ['?', 'x'], 0], [':', 'x']]
]

# Create a rewriter function
rewrite = rewriter(rules)

# Apply the rule
expr = ['+', 'a', 0]
result = rewrite(expr)
print(f"Rewritten: {result}")  # Output: 'a'
```

## Understanding the Example

Let's break down what's happening:

1. **Rules**: Rules are pairs of `[pattern, skeleton]`
   - Pattern: `['+', ['?', 'x'], 0]` matches any expression of the form "something + 0"
   - Skeleton: `[':', 'x']` means "replace with whatever matched x"

2. **Pattern Variables**:
   - `['?', 'x']` matches any expression and binds it to variable `x`
   - `[':', 'x']` in the skeleton substitutes the value bound to `x`

3. **Expression**: `['+', 'a', 0]` is the AST representation of `a + 0`

## Using the Interactive REPL

The fastest way to explore XTK is through the interactive REPL:

```bash
python -m xtk.cli
```

Try these commands:

```
xtk> (+ 2 3)
Expression: ['+', 2, 3]

xtk> /rewrite
Rewritten: 5

xtk> /help
[Shows available commands]
```

### REPL Commands

- `/rewrite` or `/rw` - Rewrite the current expression
- `/tree` - Display expression as a tree
- `/rules load <file>` - Load rules from a file
- `/eval` - Evaluate the expression
- `/help` - Show all commands

## Pattern Matching Examples

### Match Any Expression

```python
from xtk.rewriter import match

pattern = ['?', 'x']
expr = ['+', 2, 3]
result = match(pattern, expr, {})
print(result)  # {'x': ['+', 2, 3]}
```

### Match Constants

```python
pattern = ['?c', 'c']
expr = 42
result = match(pattern, expr, {})
print(result)  # {'c': 42}
```

### Match Variables

```python
pattern = ['?v', 'x']
expr = 'y'
result = match(pattern, expr, {})
print(result)  # {'x': 'y'}
```

## Common Rewrite Rules

### Identity Rules

```python
# x + 0 = x
[['+', ['?', 'x'], 0], [':', 'x']]

# x * 1 = x
[['*', ['?', 'x'], 1], [':', 'x']]

# x * 0 = 0
[['*', ['?', 'x'], 0], 0]
```

### Commutative Rules

```python
# x + y = y + x
[['+', ['?', 'x'], ['?', 'y']], ['+', [':', 'y'], [':', 'x']]]
```

### Distributive Rule

```python
# x * (y + z) = x*y + x*z
[['*', ['?', 'x'], ['+', ['?', 'y'], ['?', 'z']]],
 ['+', ['*', [':', 'x'], [':', 'y']], ['*', [':', 'x'], [':', 'z']]]]
```

## Using Predefined Rules

XTK comes with many predefined mathematical rules:

```python
from xtk.rule_loader import load_rules

# Load derivative rules
deriv_rules = load_rules('src/xtk/rules/deriv_rules.py')

# Load algebra rules
algebra_rules = load_rules('src/xtk/rules/algebra_rules.py')
```

### Example: Symbolic Differentiation

```python
from xtk import rewriter
from xtk.rule_loader import load_rules

# Load derivative rules
rules = load_rules('src/xtk/rules/deriv_rules.py')
diff = rewriter(rules)

# Differentiate x^2
expr = ['dd', ['^', 'x', 2], 'x']
result = diff(expr)
print(result)  # ['*', 2, ['^', 'x', 1]]
```

## Expression Representation

XTK uses nested lists (AST) to represent expressions:

| Mathematical Notation | XTK Representation |
|-----------------------|-------------------|
| \\(x + 3\\)           | `['+', 'x', 3]`   |
| \\(2 \times x\\)      | `['*', 2, 'x']`   |
| \\(x^2\\)             | `['^', 'x', 2]`   |
| \\(\sin(x)\\)         | `['sin', 'x']`    |
| \\(\frac{d}{dx}(x^2)\\) | `['dd', ['^', 'x', 2], 'x']` |

## Simplification

To simplify expressions recursively:

```python
from xtk.simplifier import simplifier

rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 0], 0],
    [['*', ['?', 'x'], 1], [':', 'x']],
]

simplify = simplifier(rules)

# Simplify nested expression
expr = ['+', ['*', 'x', 1], 0]
result = simplify(expr)
print(result)  # 'x'
```

## Next Steps

Now that you've learned the basics, explore:

- [Core Concepts](../user-guide/concepts.md) - Deeper understanding of XTK's architecture
- [Pattern Matching](../user-guide/pattern-matching.md) - Advanced pattern matching techniques
- [Examples](../examples/differentiation.md) - Real-world examples
- [API Reference](../api/core.md) - Complete API documentation

## Common Patterns

### Chain Multiple Rules

```python
rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],      # x + 0 = x
    [['+', 0, ['?', 'x']], [':', 'x']],      # 0 + x = x
    [['*', ['?', 'x'], 1], [':', 'x']],      # x * 1 = x
    [['*', 1, ['?', 'x']], [':', 'x']],      # 1 * x = x
    [['*', ['?', 'x'], 0], 0],               # x * 0 = 0
    [['*', 0, ['?', 'x']], 0],               # 0 * x = 0
]
```

### Conditional Rules

Use pattern constraints to create conditional rules:

```python
# Only match if x and y are the same
[['dd', ['?v', 'x'], ['?v', 'x']], 1]  # d(x)/dx = 1
```

## Tips

1. **Start Simple**: Begin with simple rules and build up complexity
2. **Use the REPL**: Test rules interactively before coding
3. **Check Order**: Rule order matters - more specific rules should come first
4. **Debug**: Use logging or print bindings to see what matched
5. **Test**: Write tests for your custom rules

Ready to dive deeper? Continue to the [Interactive REPL Guide](repl.md)!
