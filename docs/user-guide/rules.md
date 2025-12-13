# Rewrite Rules

Rewrite rules are the foundation of XTK's expression transformation system. A rule defines how to transform expressions that match a specific pattern into a new form.

## Rule Structure

Each rule is a pair `[pattern, skeleton]`:

```python
[pattern, skeleton]
```

- **Pattern**: Defines what structure to match
- **Skeleton**: Defines how to build the replacement

## Basic Examples

### Identity Rules

```python
# x + 0 => x
[['+', ['?', 'x'], 0], [':', 'x']]

# x * 1 => x
[['*', ['?', 'x'], 1], [':', 'x']]

# x * 0 => 0
[['*', ['?', 'x'], 0], 0]
```

### Power Rules

```python
# x^1 => x
[['ˆ', ['?', 'x'], 1], [':', 'x']]

# x^0 => 1
[['^', ['?', 'x'], 0], 1]
```

## Creating Rules

### Step-by-Step Process

1. **Identify the transformation**: What input produces what output?
2. **Write the pattern**: What structure should be matched?
3. **Write the skeleton**: How should the result be constructed?

### Example: Derivative of a Constant

Mathematical rule: \\(\frac{d}{dx}(c) = 0\\) where \\(c\\) is a constant.

```python
# Pattern: dd (derivative) of a constant c with respect to variable v
pattern = ['dd', ['?c', 'c'], ['?v', 'v']]

# Skeleton: the result is 0
skeleton = 0

# Complete rule
rule = [['dd', ['?c', 'c'], ['?v', 'v']], 0]
```

## Using Rules

### With the Rewriter

```python
from xtk import rewriter

rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
]

simplify = rewriter(rules)

result = simplify(['+', 'a', 0])
print(result)  # 'a'
```

### Loading Rules from Files

```python
from xtk.rule_loader import load_rules

# Load from Python file
rules = load_rules('src/xtk/rules/deriv_rules.py')

# Load from JSON file
rules = load_rules('my_rules.json')
```

## Rule Ordering

Rules are tried in order; the first matching rule is applied.

### Specific Before General

```python
rules = [
    # More specific: exact value
    [['+', 0, 0], 0],

    # Less specific: one pattern variable
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['+', 0, ['?', 'x']], [':', 'x']],

    # Most general: two variables
    [['+', ['?', 'x'], ['?', 'y']], ['+', [':', 'x'], [':', 'y']]],
]
```

## Rule Categories

### Simplification Rules

Reduce expression complexity:

```python
simplify_rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
    [['*', ['?', 'x'], 0], 0],
    [['^', ['?', 'x'], 1], [':', 'x']],
    [['^', ['?', 'x'], 0], 1],
]
```

### Expansion Rules

Distribute operations:

```python
expand_rules = [
    # a * (x + y) => a*x + a*y
    [['*', ['?', 'a'], ['+', ['?', 'x'], ['?', 'y']]],
     ['+', ['*', [':', 'a'], [':', 'x']],
           ['*', [':', 'a'], [':', 'y']]]],
]
```

### Derivative Rules

Symbolic differentiation:

```python
deriv_rules = [
    # Constant rule
    [['dd', ['?c', 'c'], ['?v', 'v']], 0],

    # Variable rule
    [['dd', ['?v', 'x'], ['?v', 'x']], 1],

    # Sum rule
    [['dd', ['+', ['?', 'f'], ['?', 'g']], ['?v', 'v']],
     ['+', ['dd', [':', 'f'], [':', 'v']],
           ['dd', [':', 'g'], [':', 'v']]]],

    # Product rule
    [['dd', ['*', ['?', 'f'], ['?', 'g']], ['?v', 'v']],
     ['+', ['*', ['dd', [':', 'f'], [':', 'v']], [':', 'g']],
           ['*', [':', 'f'], ['dd', [':', 'g'], [':', 'v']]]]],
]
```

## Combining Rule Sets

```python
from xtk.rule_loader import load_rules, merge_rules

deriv = load_rules('src/xtk/rules/deriv_rules.py')
algebra = load_rules('src/xtk/rules/algebra_rules.py')

# Merge, removing duplicates
all_rules = merge_rules(deriv, algebra)
```

## Predefined Rule Sets

XTK includes rule sets in `src/xtk/rules/`:

| File | Description |
|------|-------------|
| `deriv_rules.py` | Symbolic differentiation |
| `algebra_rules.py` | Algebraic simplification |
| `trig-rules.py` | Trigonometric identities |
| `integral-rules.py` | Integration rules |

## Best Practices

1. **Test rules individually** before combining
2. **Order rules** from specific to general
3. **Document** what each rule transforms
4. **Consider commutativity**: Add rules for both `x + 0` and `0 + x`
5. **Use type constraints** (`?c`, `?v`) to avoid over-matching

## Next Steps

- Learn about [Pattern Matching](pattern-matching.md) in detail
- Explore [Simplification](simplification.md) strategies
- Create [Custom Rules](../advanced/custom-rules.md)
