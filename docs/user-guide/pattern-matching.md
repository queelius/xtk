# Pattern Matching

Pattern matching is the cornerstone of XTK's expression rewriting system. This guide covers everything you need to know about creating and using patterns effectively.

## What is Pattern Matching?

Pattern matching determines whether an expression has a specific structure and extracts sub-expressions for use in transformations.

### Basic Idea

```python
pattern = ['+', ['?', 'x'], ['?', 'y']]
expression = ['+', 2, 3]

# Does expression match pattern? Yes!
# Bindings: {'x': 2, 'y': 3}
```

## Pattern Variables

XTK provides three types of pattern variables:

### 1. Universal Pattern (`?`)

Matches **any** expression:

```python
from xtk.rewriter import match

pattern = ['?', 'x']

# Matches constants
match(pattern, 42, {})  # {'x': 42}

# Matches variables
match(pattern, 'a', {})  # {'x': 'a'}

# Matches compound expressions
match(pattern, ['+', 2, 3], {})  # {'x': ['+', 2, 3]}
```

### 2. Constant Pattern (`?c`)

Matches only **constants** (numbers):

```python
pattern = ['?c', 'c']

# Matches
match(pattern, 42, {})     # {'c': 42}
match(pattern, 3.14, {})   # {'c': 3.14}
match(pattern, -7, {})     # {'c': -7}

# Does not match
match(pattern, 'x', {})         # "failed"
match(pattern, ['+', 2, 3], {}) # "failed"
```

### 3. Variable Pattern (`?v`)

Matches only **variables** (symbols):

```python
pattern = ['?v', 'v']

# Matches
match(pattern, 'x', {})    # {'v': 'x'}
match(pattern, 'foo', {})  # {'v': 'foo'}

# Does not match
match(pattern, 42, {})          # "failed"
match(pattern, ['+', 2, 3], {}) # "failed"
```

## Pattern Structure

### Exact Matching

Non-pattern elements must match exactly:

```python
pattern = ['+', 'x', 0]
expr = ['+', 'x', 0]   # Matches
expr = ['+', 'x', 1]   # Does not match
expr = ['-', 'x', 0]   # Does not match
```

### List Structure

Lists must have the same structure:

```python
pattern = ['+', ['?', 'x'], ['?', 'y']]

# Matches: same structure
expr = ['+', 2, 3]
expr = ['+', 'a', 'b']
expr = ['+', ['+', 1, 2], 3]

# Does not match: wrong operator
expr = ['*', 2, 3]

# Does not match: wrong arity
expr = ['+', 2]
expr = ['+', 2, 3, 4]
```

### Nested Patterns

Patterns can be nested arbitrarily:

```python
# Match: (f + g) * h
pattern = ['*', ['+', ['?', 'f'], ['?', 'g']], ['?', 'h']]

expr = ['*', ['+', 'x', 'y'], 'z']
# Bindings: {'f': 'x', 'g': 'y', 'h': 'z'}
```

## Advanced Pattern Matching

### Multiple Occurrences

The same pattern variable can appear multiple times:

```python
# Match: x + x (same variable twice)
pattern = ['+', ['?v', 'x'], ['?v', 'x']]

expr = ['+', 'a', 'a']   # Matches: {'x': 'a'}
expr = ['+', 'a', 'b']   # Does not match (different vars)
```

### Deeply Nested Patterns

```python
# Match: d/dx(f(g(x)))
pattern = ['dd', ['f', ['g', ['?v', 'x']]], ['?v', 'x']]

expr = ['dd', ['sin', ['cos', 'x']], 'x']
# Bindings: {'x': 'x'}
```

### Combining Pattern Types

```python
# Match: constant * variable
pattern = ['*', ['?c', 'c'], ['?v', 'x']]

expr = ['*', 2, 'a']      # Matches: {'c': 2, 'x': 'a'}
expr = ['*', 'a', 2]      # Does not match (order matters)
expr = ['*', 2, 3]        # Does not match (3 is not a variable)
```

## Pattern Matching Examples

### Identity Patterns

```python
# x + 0
pattern = ['+', ['?', 'x'], 0]

# x * 1
pattern = ['*', ['?', 'x'], 1]

# x * 0
pattern = ['*', ['?', 'x'], 0]
```

### Commutative Patterns

To handle commutativity, define both orders:

```python
rules = [
    [['*', ['?c', 'c'], ['?v', 'x']], ['*', [':', 'x'], [':', 'c']]],
    [['*', ['?v', 'x'], ['?c', 'c']], ['*', [':', 'x'], [':', 'c']]]
]
```

### Associative Patterns

```python
# Flatten: (x + y) + z => x + (y + z)
pattern = [['+', ['+', ['?', 'x'], ['?', 'y']], ['?', 'z']]]
skeleton = ['+', [':', 'x'], ['+', [':', 'y'], [':', 'z']]]
```

### Derivative Patterns

```python
# Constant: d(c)/dx = 0
[['dd', ['?c', 'c'], ['?v', 'x']], 0]

# Variable: d(x)/dx = 1
[['dd', ['?v', 'x'], ['?v', 'x']], 1]

# Sum rule: d(f+g)/dx = df/dx + dg/dx
[['dd', ['+', ['?', 'f'], ['?', 'g']], ['?v', 'x']],
 ['+', ['dd', [':', 'f'], [':', 'x']], ['dd', [':', 'g'], [':', 'x']]]]

# Product rule: d(fg)/dx = f'g + fg'
[['dd', ['*', ['?', 'f'], ['?', 'g']], ['?v', 'x']],
 ['+', ['*', ['dd', [':', 'f'], [':', 'x']], [':', 'g']],
      ['*', [':', 'f'], ['dd', [':', 'g'], [':', 'x']]]]]
```

## The match() Function

### Function Signature

```python
def match(pattern, expression, bindings):
    """
    Match a pattern against an expression.

    Args:
        pattern: The pattern to match
        expression: The expression to match against
        bindings: Existing variable bindings

    Returns:
        Updated bindings dict if successful, "failed" otherwise
    """
```

### Usage Examples

#### Simple Match

```python
from xtk.rewriter import match

pattern = ['+', ['?', 'x'], ['?', 'y']]
expr = ['+', 2, 3]
result = match(pattern, expr, {})

print(result)  # {'x': 2, 'y': 3}
```

#### Match with Existing Bindings

```python
# Start with some bindings
bindings = {'x': 2}

pattern = ['+', [':', 'x'], ['?', 'y']]
expr = ['+', 2, 3]

result = match(pattern, expr, bindings)
print(result)  # {'x': 2, 'y': 3}
```

#### Match Failure

```python
pattern = ['+', ['?', 'x'], ['?', 'y']]
expr = ['*', 2, 3]  # Wrong operator

result = match(pattern, expr, {})
print(result)  # "failed"
```

## Pattern Matching Strategies

### Specific to General

Order patterns from most specific to most general:

```python
rules = [
    # Most specific: exact pattern
    [['+', 0, 0], 0],

    # More specific: one pattern variable
    [['+', ['?', 'x'], 0], [':', 'x']],

    # Less specific: two pattern variables
    [['+', ['?', 'x'], ['?', 'y']], ['+', [':', 'y'], [':', 'x']]],

    # Most general: anything
    [['?', 'x'], ['generic', [':', 'x']]]
]
```

### Defensive Patterns

Use type constraints to avoid unwanted matches:

```python
# Bad: too general
pattern = ['dd', ['?', 'expr'], ['?', 'var']]

# Good: constrained types
pattern = ['dd', ['?', 'expr'], ['?v', 'var']]
# Now 'var' must be a variable, not an expression
```

### Greedy vs Conservative

```python
# Greedy: matches as much as possible
pattern = ['+', ['?', 'sum']]
# Matches any addition, binds entire tail to 'sum'

# Conservative: explicit structure
pattern = ['+', ['?', 'x'], ['?', 'y']]
# Matches binary addition only
```

## Common Pitfalls

### 1. Variable Shadowing

```python
# Problem: 'x' used twice with different meanings
pattern = ['+', ['?', 'x'], ['?', 'x']]
expr = ['+', 'a', 'b']
# Does not match! Both must be same

# Solution: use different variable names
pattern = ['+', ['?', 'x'], ['?', 'y']]
```

### 2. Overly General Patterns

```python
# Problem: matches everything
pattern = ['?', 'x']

# Solution: be more specific
pattern = ['+', ['?', 'x'], ['?', 'y']]
```

### 3. Order Sensitivity

```python
# Only matches x + 0, not 0 + x
pattern = ['+', ['?', 'x'], 0]

# Solution: add both patterns
patterns = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['+', 0, ['?', 'x']], [':', 'x']]
]
```

### 4. Incomplete Type Constraints

```python
# Problem: might match non-numbers
pattern = ['+', ['?', 'x'], ['?', 'y']]

# Solution: use type constraints if needed
pattern = ['+', ['?c', 'x'], ['?c', 'y']]
```

## Testing Patterns

### Interactive Testing

Use the REPL to test patterns:

```
xtk> /pattern ['+', ['?', 'x'], 0]
Pattern defined

xtk> /test ['+', 'a', 0]
Match: {'x': 'a'}

xtk> /test ['+', 'a', 1]
Failed
```

### Unit Tests

Write tests for your patterns:

```python
import unittest
from xtk.rewriter import match

class TestPatterns(unittest.TestCase):
    def test_identity_pattern(self):
        pattern = ['+', ['?', 'x'], 0]
        expr = ['+', 'a', 0]
        result = match(pattern, expr, {})
        self.assertEqual(result, {'x': 'a'})

    def test_no_match(self):
        pattern = ['+', ['?', 'x'], 0]
        expr = ['+', 'a', 1]
        result = match(pattern, expr, {})
        self.assertEqual(result, "failed")
```

## Performance Considerations

### Pattern Complexity

- Simple patterns match faster
- Deeply nested patterns are slower
- Type constraints (`?c`, `?v`) add overhead

### Optimization Tips

1. **Use specific patterns first**
2. **Minimize pattern depth**
3. **Cache compiled patterns** (if implementing custom matcher)
4. **Limit backtracking** in complex patterns

## Pattern Libraries

### Building Reusable Patterns

```python
# patterns.py
ARITHMETIC_PATTERNS = {
    'identity_add': ['+', ['?', 'x'], 0],
    'identity_mul': ['*', ['?', 'x'], 1],
    'zero_mul': ['*', ['?', 'x'], 0],
}

CALCULUS_PATTERNS = {
    'derivative_const': ['dd', ['?c', 'c'], ['?v', 'x']],
    'derivative_var': ['dd', ['?v', 'x'], ['?v', 'x']],
}
```

### Using Pattern Libraries

```python
from patterns import ARITHMETIC_PATTERNS

rules = [
    [ARITHMETIC_PATTERNS['identity_add'], [':', 'x']],
    [ARITHMETIC_PATTERNS['identity_mul'], [':', 'x']],
]
```

## Next Steps

- Learn about [Rewrite Rules](rules.md) that use these patterns
- Explore [Simplification](simplification.md) strategies
- Try [Advanced Custom Rules](../advanced/custom-rules.md)
