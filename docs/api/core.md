# Core API Reference

This document describes the core functions in XTK's rewriter module.

## Module: `xtk.rewriter`

The rewriter module provides the fundamental functions for pattern matching, instantiation, and evaluation.

### match()

```python
def match(pattern, expression, bindings) -> Union[Dict, str]
```

Match a pattern against an expression and return updated bindings.

**Parameters:**

- `pattern` (ExprType): The pattern to match
- `expression` (ExprType): The expression to match against
- `bindings` (Dict): Dictionary of existing variable bindings

**Returns:**

- `Dict`: Updated bindings if match successful
- `str`: `"failed"` if match unsuccessful

**Examples:**

```python
from xtk.rewriter import match

# Simple match
pattern = ['+', ['?', 'x'], ['?', 'y']]
expr = ['+', 2, 3]
result = match(pattern, expr, {})
# Returns: {'x': 2, 'y': 3}

# Match with type constraint
pattern = ['*', ['?c', 'c'], ['?v', 'x']]
expr = ['*', 2, 'a']
result = match(pattern, expr, {})
# Returns: {'c': 2, 'x': 'a'}

# Failed match
pattern = ['+', ['?', 'x'], 0]
expr = ['+', 'a', 1]
result = match(pattern, expr, {})
# Returns: "failed"
```

### instantiate()

```python
def instantiate(skeleton, bindings) -> ExprType
```

Create a new expression from a skeleton using variable bindings.

**Parameters:**

- `skeleton` (ExprType): The skeleton template
- `bindings` (Dict): Dictionary mapping variable names to values

**Returns:**

- `ExprType`: The instantiated expression

**Examples:**

```python
from xtk.rewriter import instantiate

# Simple instantiation
skeleton = ['+', [':', 'x'], [':', 'y']]
bindings = {'x': 2, 'y': 3}
result = instantiate(skeleton, bindings)
# Returns: ['+', 2, 3]

# Nested instantiation
skeleton = ['*', [':', 'a'], ['+', [':', 'b'], [':', 'c']]]
bindings = {'a': 2, 'b': 3, 'c': 4}
result = instantiate(skeleton, bindings)
# Returns: ['*', 2, ['+', 3, 4]]

# Direct value
skeleton = 42
result = instantiate(skeleton, {})
# Returns: 42
```

### evaluate()

```python
def evaluate(expression, bindings) -> Any
```

Evaluate an expression using the provided bindings.

**Parameters:**

- `expression` (ExprType): The expression to evaluate
- `bindings` (Dict): Dictionary of operations and variable values

**Returns:**

- `Any`: The computed value

**Examples:**

```python
from xtk.rewriter import evaluate

# Arithmetic evaluation
expr = ['+', 2, 3]
bindings = {'+': lambda x, y: x + y}
result = evaluate(expr, bindings)
# Returns: 5

# With variables
expr = ['*', 'x', 'y']
bindings = {
    '*': lambda x, y: x * y,
    'x': 4,
    'y': 5
}
result = evaluate(expr, bindings)
# Returns: 20

# Nested expression
expr = ['+', ['*', 2, 3], 4]
bindings = {
    '+': lambda x, y: x + y,
    '*': lambda x, y: x * y
}
result = evaluate(expr, bindings)
# Returns: 10
```

### rewriter()

```python
def rewriter(rules) -> Callable
```

Create a rewriting function from a list of rules.

**Parameters:**

- `rules` (List[RuleType]): List of `[pattern, skeleton]` pairs

**Returns:**

- `Callable`: A function that rewrites expressions

**Examples:**

```python
from xtk import rewriter

# Create rewriter with simple rules
rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
]
rewrite = rewriter(rules)

# Use the rewriter
expr = ['+', 'a', 0]
result = rewrite(expr)
# Returns: 'a'

expr = ['*', ['+', 'x', 0], 1]
result = rewrite(expr)
# Returns: ['+', 'x', 0] (only rewrites at top level)
```

## Utility Functions

### car()

```python
def car(lst: List) -> Any
```

Return the first element of a list (head).

**Parameters:**

- `lst` (List): A non-empty list

**Returns:**

- `Any`: The first element

**Raises:**

- `TypeError`: If argument is not a list
- `ValueError`: If list is empty

**Example:**

```python
from xtk.rewriter import car

result = car([1, 2, 3])
# Returns: 1

result = car([['+', 'x', 'y'], 'z'])
# Returns: ['+', 'x', 'y']
```

### cdr()

```python
def cdr(lst: List) -> List
```

Return all but the first element of a list (tail).

**Parameters:**

- `lst` (List): A list

**Returns:**

- `List`: All elements except the first

**Example:**

```python
from xtk.rewriter import cdr

result = cdr([1, 2, 3])
# Returns: [2, 3]

result = cdr([1])
# Returns: []
```

### cons()

```python
def cons(item: Any, lst: List) -> List
```

Construct a new list by prepending an item.

**Parameters:**

- `item` (Any): The item to prepend
- `lst` (List): The list to prepend to

**Returns:**

- `List`: A new list with item as first element

**Example:**

```python
from xtk.rewriter import cons

result = cons(1, [2, 3])
# Returns: [1, 2, 3]

result = cons(['+', 'x'], ['y'])
# Returns: [['+', 'x'], 'y']
```

## Type Predicates

### atom()

```python
def atom(exp: ExprType) -> bool
```

Check if an expression is atomic (not compound).

**Parameters:**

- `exp` (ExprType): The expression to check

**Returns:**

- `bool`: True if atomic, False otherwise

**Example:**

```python
from xtk.rewriter import atom

atom(42)              # True
atom('x')             # True
atom(['+', 2, 3])     # False
```

### compound()

```python
def compound(exp: ExprType) -> bool
```

Check if an expression is compound (a list).

**Parameters:**

- `exp` (ExprType): The expression to check

**Returns:**

- `bool`: True if compound, False otherwise

**Example:**

```python
from xtk.rewriter import compound

compound(['+', 2, 3])  # True
compound(42)           # False
compound('x')          # False
```

### constant()

```python
def constant(exp: ExprType) -> bool
```

Check if an expression is a constant (number).

**Parameters:**

- `exp` (ExprType): The expression to check

**Returns:**

- `bool`: True if constant, False otherwise

**Example:**

```python
from xtk.rewriter import constant

constant(42)           # True
constant(3.14)         # True
constant('x')          # False
constant(['+', 2, 3])  # False
```

### variable()

```python
def variable(exp: ExprType) -> bool
```

Check if an expression is a variable (string).

**Parameters:**

- `exp` (ExprType): The expression to check

**Returns:**

- `bool`: True if variable, False otherwise

**Example:**

```python
from xtk.rewriter import variable

variable('x')          # True
variable('foo')        # True
variable(42)           # False
variable(['+', 2, 3])  # False
```

## Type Definitions

```python
from typing import Any, Dict, List, Union

ExprType = Union[int, float, str, List]
DictType = Union[List[List], str]
RuleType = List[List]
```

### ExprType

Represents any valid expression:
- `int`: Integer constant
- `float`: Floating-point constant
- `str`: Variable or operator name
- `List`: Compound expression

### RuleType

A rule is a list containing:
- `pattern`: First element (List)
- `skeleton`: Second element (List or atomic value)

## Common Patterns

### Creating a Simple Rewriter

```python
from xtk import rewriter

rules = [
    # Identity rules
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['+', 0, ['?', 'x']], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
    [['*', 1, ['?', 'x']], [':', 'x']],

    # Zero rules
    [['*', ['?', 'x'], 0], 0],
    [['*', 0, ['?', 'x']], 0],
]

rewrite = rewriter(rules)

# Use it
expr = ['+', ['*', 'x', 1], 0]
result = rewrite(expr)  # ['*', 'x', 1]
```

### Testing Pattern Matches

```python
from xtk.rewriter import match

def test_pattern(pattern, expressions):
    """Test a pattern against multiple expressions."""
    for expr in expressions:
        result = match(pattern, expr, {})
        if result != "failed":
            print(f"{expr} matches: {result}")
        else:
            print(f"{expr} does not match")

pattern = ['+', ['?c', 'x'], ['?c', 'y']]
test_pattern(pattern, [
    ['+', 2, 3],      # matches
    ['+', 'a', 'b'],  # does not match
    ['+', 2, 'x'],    # does not match
])
```

## Error Handling

### MatchFailure Exception

Some internal functions may raise `MatchFailure`:

```python
class MatchFailure(Exception):
    """Exception raised when pattern matching fails."""
    pass
```

### Handling Match Failures

The public `match()` function returns `"failed"` instead of raising exceptions:

```python
result = match(pattern, expr, {})
if result == "failed":
    print("Match failed")
else:
    print(f"Bindings: {result}")
```

## See Also

- [Simplifier API](simplifier.md) - Recursive simplification
- [Rule Loader API](rule-loader.md) - Loading rules from files
- [Search API](search.md) - Tree search algorithms
