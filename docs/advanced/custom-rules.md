# Custom Rules

This guide covers creating custom rewrite rules for your specific domain or application.

## Rule Anatomy

Every rule has two parts:

```python
[pattern, skeleton]
```

- **Pattern**: What to match (using pattern variables)
- **Skeleton**: What to produce (using substitution markers)

## Pattern Syntax

### Pattern Variables

| Syntax | Matches | Example |
|--------|---------|---------|
| `['?', 'x']` | Any expression | `42`, `'a'`, `['+', 1, 2]` |
| `['?c', 'c']` | Constants only | `42`, `3.14`, `-7` |
| `['?v', 'v']` | Variables only | `'x'`, `'foo'` |

### Skeleton Syntax

| Syntax | Meaning |
|--------|---------|
| `[':', 'x']` | Substitute value bound to `x` |
| literal | Use the literal value |

## Creating Rules Step-by-Step

### Step 1: Identify the Transformation

Write the mathematical transformation:

\\[ x + 0 = x \\]

### Step 2: Create the Pattern

Match expressions of the form "something plus zero":

```python
pattern = ['+', ['?', 'x'], 0]
```

### Step 3: Create the Skeleton

Return the matched expression:

```python
skeleton = [':', 'x']
```

### Step 4: Combine into a Rule

```python
rule = [['+', ['?', 'x'], 0], [':', 'x']]
```

## Example Rules

### Arithmetic Simplification

```python
arithmetic_rules = [
    # Additive identity
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['+', 0, ['?', 'x']], [':', 'x']],

    # Multiplicative identity
    [['*', ['?', 'x'], 1], [':', 'x']],
    [['*', 1, ['?', 'x']], [':', 'x']],

    # Multiplication by zero
    [['*', ['?', 'x'], 0], 0],
    [['*', 0, ['?', 'x']], 0],

    # Division by one
    [['/', ['?', 'x'], 1], [':', 'x']],

    # Power rules
    [['^', ['?', 'x'], 0], 1],
    [['^', ['?', 'x'], 1], [':', 'x']],
]
```

### Derivative Rules

```python
derivative_rules = [
    # Constant rule: d/dx(c) = 0
    [['dd', ['?c', 'c'], ['?v', 'x']], 0],

    # Variable rule: d/dx(x) = 1
    [['dd', ['?v', 'x'], ['?v', 'x']], 1],

    # Sum rule: d/dx(f + g) = df/dx + dg/dx
    [['dd', ['+', ['?', 'f'], ['?', 'g']], ['?v', 'x']],
     ['+', ['dd', [':', 'f'], [':', 'x']],
           ['dd', [':', 'g'], [':', 'x']]]],

    # Product rule: d/dx(f * g) = f' * g + f * g'
    [['dd', ['*', ['?', 'f'], ['?', 'g']], ['?v', 'x']],
     ['+', ['*', ['dd', [':', 'f'], [':', 'x']], [':', 'g']],
           ['*', [':', 'f'], ['dd', [':', 'g'], [':', 'x']]]]],

    # Power rule: d/dx(x^n) = n * x^(n-1)
    [['dd', ['^', ['?v', 'x'], ['?c', 'n']], ['?v', 'x']],
     ['*', [':', 'n'], ['^', [':', 'x'], ['-', [':', 'n'], 1]]]],
]
```

### Boolean Logic Rules

```python
logic_rules = [
    # Identity
    [['and', ['?', 'x'], True], [':', 'x']],
    [['or', ['?', 'x'], False], [':', 'x']],

    # Domination
    [['and', ['?', 'x'], False], False],
    [['or', ['?', 'x'], True], True],

    # Idempotence
    [['and', ['?', 'x'], ['?', 'x']], [':', 'x']],
    [['or', ['?', 'x'], ['?', 'x']], [':', 'x']],

    # Double negation
    [['not', ['not', ['?', 'x']]], [':', 'x']],

    # De Morgan's laws
    [['not', ['and', ['?', 'a'], ['?', 'b']]],
     ['or', ['not', [':', 'a']], ['not', [':', 'b']]]],
    [['not', ['or', ['?', 'a'], ['?', 'b']]],
     ['and', ['not', [':', 'a']], ['not', [':', 'b']]]],
]
```

## Multiple Variable Occurrences

The same pattern variable can appear multiple times:

```python
# x + x = 2 * x
[['+', ['?', 'x'], ['?', 'x']], ['*', 2, [':', 'x']]]

# x * x = x^2
[['*', ['?', 'x'], ['?', 'x']], ['^', [':', 'x'], 2]]
```

Both occurrences must match the **same** expression.

## Type-Constrained Rules

Use `?c` and `?v` to restrict what matches:

```python
# Only apply power rule when exponent is a constant
[['dd', ['^', ['?v', 'x'], ['?c', 'n']], ['?v', 'x']],
 ['*', [':', 'n'], ['^', [':', 'x'], ['-', [':', 'n'], 1]]]]

# Different handling for variable exponents would need another rule
```

## Handling Commutativity

Add rules for both orderings:

```python
commutative_rules = [
    # x + 0 = x (both orders)
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['+', 0, ['?', 'x']], [':', 'x']],

    # Normalize to put constants on the right
    [['+', ['?c', 'c'], ['?v', 'x']], ['+', [':', 'x'], [':', 'c']]],
    [['*', ['?c', 'c'], ['?v', 'x']], ['*', [':', 'x'], [':', 'c']]],
]
```

## Rule Organization

### By Category

```python
# rules/my_domain.py

identity_rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
]

simplification_rules = [
    [['*', ['?', 'x'], 0], 0],
    [['^', ['?', 'x'], 0], 1],
]

expansion_rules = [
    [['*', ['?', 'a'], ['+', ['?', 'x'], ['?', 'y']]],
     ['+', ['*', [':', 'a'], [':', 'x']],
           ['*', [':', 'a'], [':', 'y']]]],
]

# Combine in specific order
all_rules = identity_rules + simplification_rules + expansion_rules
```

### Rich Rules with Metadata

```python
from xtk.rule_utils import RichRule

rich_rules = [
    RichRule(
        pattern=['+', ['?', 'x'], 0],
        skeleton=[':', 'x'],
        name="additive_identity",
        description="Adding zero yields the original value",
        category="simplification"
    ),
]
```

## Testing Rules

### Unit Tests

```python
import unittest
from xtk import rewriter

class TestMyRules(unittest.TestCase):
    def setUp(self):
        self.simplify = rewriter(my_rules)

    def test_additive_identity(self):
        result = self.simplify(['+', 'x', 0])
        self.assertEqual(result, 'x')

    def test_multiplicative_identity(self):
        result = self.simplify(['*', 'y', 1])
        self.assertEqual(result, 'y')

    def test_nested(self):
        result = self.simplify(['+', ['*', 'x', 1], 0])
        self.assertEqual(result, 'x')
```

### Interactive Testing

```
$ python -m xtk.cli
xtk> /rules load my_rules.py
Loaded 10 rules

xtk> (+ x 0)
xtk> /rw
Rewritten: x
```

## Common Pitfalls

### Overly General Patterns

```python
# BAD: matches everything
[[['?', 'x']], ['simplified', [':', 'x']]]

# GOOD: specific structure
[[['+', ['?', 'x'], 0]], [':', 'x']]
```

### Infinite Loops

```python
# BAD: creates infinite loop
[['+', ['?', 'x'], ['?', 'y']], ['+', [':', 'y'], [':', 'x']]]

# The above swaps forever: a+b -> b+a -> a+b -> ...
```

### Rule Order Issues

```python
# BAD order: general before specific
rules = [
    [['+', ['?', 'x'], ['?', 'y']], ...],  # Catches everything
    [['+', ['?', 'x'], 0], [':', 'x']],    # Never reached!
]

# GOOD order: specific before general
rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],    # Specific case first
    [['+', ['?', 'x'], ['?', 'y']], ...],  # General case last
]
```

## Loading Custom Rules

### From Python File

```python
from xtk.rule_loader import load_rules

rules = load_rules('path/to/my_rules.py')
```

### From JSON

```json
[
  [["+", ["?", "x"], 0], [":", "x"]],
  [["*", ["?", "x"], 1], [":", "x"]]
]
```

```python
rules = load_rules('my_rules.json')
```

## Next Steps

- Study the [predefined rules](https://github.com/queelius/xtk/tree/master/src/xtk/rules)
- Learn about [Theorem Proving](theorem-proving.md) with rules
- Explore [Language Design](language-design.md) concepts
