# Simplifier API Reference

The simplifier functionality is provided by the `rewriter` function in `xtk.rewriter`. The `simplifier` name is an alias for backwards compatibility.

## Overview

The simplifier applies rewrite rules recursively to transform expressions into simplified forms. It works bottom-up, simplifying sub-expressions before their parents.

## Main Function

### simplifier / rewriter

```python
def rewriter(
    the_rules: List[RuleType],
    step_logger: Optional[StepLogger] = None,
    constant_folding: bool = True
) -> Callable[[ExprType], ExprType]

# Alias for backwards compatibility
simplifier = rewriter
```

Create a simplifier function from rules.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `the_rules` | `List[RuleType]` | List of `[pattern, skeleton]` rules |
| `step_logger` | `Optional[StepLogger]` | Logger for tracking transformations |
| `constant_folding` | `bool` | Enable arithmetic evaluation (default: `True`) |

**Returns:**

A callable that takes an expression and returns the simplified expression.

**Example:**

```python
from xtk import rewriter
# Or: from xtk.rewriter import simplifier

rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
    [['*', ['?', 'x'], 0], 0],
]

simplify = rewriter(rules)

# Simple simplification
result = simplify(['+', 'a', 0])
print(result)  # 'a'

# Nested simplification
result = simplify(['*', ['+', 'x', 0], 1])
print(result)  # 'x'
```

## Simplification Process

### Algorithm

1. **Try rules**: Attempt to match and apply each rule to the expression
2. **Constant folding**: If enabled, evaluate constant arithmetic
3. **Recurse**: Simplify sub-expressions
4. **Repeat**: Continue until no changes occur (fixed point)

### Maximum Iterations

The simplifier has a built-in limit of 1000 iterations to prevent infinite loops.

## Constant Folding

When `constant_folding=True` (default), arithmetic operations on constants are evaluated:

```python
simplify = rewriter([], constant_folding=True)

result = simplify(['+', 2, 3])
print(result)  # 5

result = simplify(['*', ['+', 2, 3], 4])
print(result)  # 20
```

Supported operations: `+`, `-`, `*`, `/`, `^`

### Disabling Constant Folding

```python
simplify = rewriter([], constant_folding=False)

result = simplify(['+', 2, 3])
print(result)  # ['+', 2, 3] (unchanged)
```

## Step Logging

Track transformations with `StepLogger`:

```python
from xtk import rewriter
from xtk.step_logger import StepLogger

rules = [[['+', ['?', 'x'], 0], [':', 'x']]]

logger = StepLogger()
simplify = rewriter(rules, step_logger=logger)

result = simplify(['+', ['+', 'a', 0], 0])

# Access logged steps
for step in logger.steps:
    print(f"{step['before']} -> {step['after']}")
    print(f"  Rule: {step['rule_pattern']}")
```

### StepLogger API

```python
class StepLogger:
    def __init__(self):
        self.steps = []

    def log_initial(self, expr):
        """Log the initial expression."""

    def log_rewrite(self, before, after, rule_pattern, rule_skeleton, bindings):
        """Log a single rewrite step."""

    def log_final(self, expr, metadata):
        """Log the final result."""

    def clear(self):
        """Clear all logged steps."""
```

## Usage Patterns

### Combining Rule Sets

```python
from xtk import rewriter
from xtk.rule_loader import load_rules

deriv_rules = load_rules('src/xtk/rules/deriv_rules.py')
algebra_rules = load_rules('src/xtk/rules/algebra_rules.py')

# Order matters: more specific rules first
all_rules = deriv_rules + algebra_rules
simplify = rewriter(all_rules)
```

### Partial Simplification

Create specialized simplifiers:

```python
# Only algebraic simplification
algebra_simplify = rewriter(algebra_rules)

# Only derivative computation
deriv_simplify = rewriter(deriv_rules)

# Chain them
expr = ['dd', ['+', ['*', 'x', 1], 0], 'x']
expr = algebra_simplify(expr)  # Simplify algebra first
expr = deriv_simplify(expr)    # Then compute derivative
```

### Custom Simplification Pipeline

```python
def full_simplify(expr, max_passes=10):
    """Apply simplification in multiple passes."""
    simplify = rewriter(all_rules)

    for _ in range(max_passes):
        new_expr = simplify(expr)
        if new_expr == expr:
            break
        expr = new_expr

    return expr
```

## Error Handling

The simplifier handles errors gracefully:

```python
# Invalid expressions return unchanged
simplify = rewriter([])
result = simplify(None)  # Returns None

# Rules that don't match are skipped
rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
simplify = rewriter(rules)
result = simplify(['*', 'a', 0])  # Returns ['*', 'a', 0]
```

## Performance Considerations

### Rule Ordering

Rules are tried in order. Place frequently-matching rules first:

```python
# Good: common cases first
rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],      # Very common
    [['*', ['?', 'x'], 1], [':', 'x']],      # Common
    # ... more specific rules later
]
```

### Expression Size

Large expressions may require many iterations:

```python
# For very large expressions, consider:
# 1. Breaking into smaller parts
# 2. Increasing iteration limit (not recommended)
# 3. Using targeted rules
```

## Related Functions

| Function | Purpose |
|----------|---------|
| `match()` | Pattern matching |
| `instantiate()` | Skeleton instantiation |
| `evaluate()` | Expression evaluation |
| `load_rules()` | Loading rules from files |

## See Also

- [Rewriter API](rewriter.md)
- [Simplification Guide](../user-guide/simplification.md)
- [Custom Rules](../advanced/custom-rules.md)
