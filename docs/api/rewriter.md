# Rewriter API Reference

The `rewriter` module (`xtk.rewriter`) contains the core functions for pattern matching, skeleton instantiation, evaluation, and expression rewriting.

## Main Functions

### rewriter

```python
def rewriter(
    the_rules: List[RuleType],
    step_logger: Optional[StepLogger] = None,
    constant_folding: bool = True
) -> Callable[[ExprType], ExprType]
```

Create a rewriter function that applies rules to expressions.

**Parameters:**

- `the_rules`: List of `[pattern, skeleton]` rules
- `step_logger`: Optional `StepLogger` for tracking transformations
- `constant_folding`: Enable automatic arithmetic evaluation (default: `True`)

**Returns:**

A function that takes an expression and returns the simplified expression.

**Example:**

```python
from xtk import rewriter

rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
]

simplify = rewriter(rules)
result = simplify(['+', 'a', 0])  # 'a'
```

---

### match

```python
def match(
    pat: ExprType,
    exp: ExprType,
    dict_: DictType
) -> DictType
```

Match a pattern against an expression.

**Parameters:**

- `pat`: The pattern to match
- `exp`: The expression to match against
- `dict_`: Current bindings dictionary (list of `[name, value]` pairs)

**Returns:**

Updated bindings dictionary on success, `"failed"` string on failure.

**Example:**

```python
from xtk.rewriter import match

pattern = ['+', ['?', 'x'], ['?', 'y']]
expression = ['+', 2, 3]
bindings = match(pattern, expression, [])
# Result: [['x', 2], ['y', 3]]
```

---

### instantiate

```python
def instantiate(
    skeleton: ExprType,
    dict_: DictType
) -> ExprType
```

Instantiate a skeleton using variable bindings.

**Parameters:**

- `skeleton`: The skeleton template
- `dict_`: Bindings dictionary from matching

**Returns:**

The instantiated expression.

**Example:**

```python
from xtk.rewriter import instantiate

skeleton = ['+', [':', 'y'], [':', 'x']]
bindings = [['x', 2], ['y', 3]]
result = instantiate(skeleton, bindings)
# Result: ['+', 3, 2]
```

---

### evaluate

```python
def evaluate(
    form: ExprType,
    dict_: DictType
) -> ExprType
```

Evaluate an expression with variable bindings.

**Parameters:**

- `form`: The expression to evaluate
- `dict_`: Bindings dictionary mapping names to values/functions

**Returns:**

The evaluated result.

**Example:**

```python
from xtk.rewriter import evaluate

bindings = [
    ['+', lambda a, b: a + b],
    ['x', 5],
]
result = evaluate(['+', 'x', 3], bindings)
# Result: 8
```

## Type Predicates

### constant

```python
def constant(exp: ExprType) -> bool
```

Check if expression is a numeric constant (int or float).

```python
constant(42)       # True
constant(3.14)     # True
constant('x')      # False
```

---

### variable

```python
def variable(exp: ExprType) -> bool
```

Check if expression is a variable (string).

```python
variable('x')      # True
variable(42)       # False
```

---

### atom

```python
def atom(exp: ExprType) -> bool
```

Check if expression is atomic (constant or variable).

```python
atom(42)           # True
atom('x')          # True
atom(['+', 1, 2])  # False
```

---

### compound

```python
def compound(exp: ExprType) -> bool
```

Check if expression is compound (a list).

```python
compound(['+', 1, 2])  # True
compound(42)           # False
```

## List Operations

### car

```python
def car(lst: List) -> Any
```

Return the first element of a list (head).

```python
car(['+', 1, 2])  # '+'
```

**Raises:**

- `TypeError`: If argument is not a list
- `ValueError`: If list is empty

---

### cdr

```python
def cdr(lst: List) -> List
```

Return all but the first element (tail).

```python
cdr(['+', 1, 2])  # [1, 2]
cdr([])           # []
```

---

### cons

```python
def cons(item: Any, lst: List) -> List
```

Construct a new list by prepending an item.

```python
cons('+', [1, 2])  # ['+', 1, 2]
```

## Pattern Predicates

### arbitrary_expression

```python
def arbitrary_expression(pat: ExprType) -> bool
```

Check if pattern is a universal matcher `['?', name]`.

```python
arbitrary_expression(['?', 'x'])  # True
```

---

### arbitrary_constant

```python
def arbitrary_constant(pat: ExprType) -> bool
```

Check if pattern is a constant matcher `['?c', name]`.

```python
arbitrary_constant(['?c', 'c'])  # True
```

---

### arbitrary_variable

```python
def arbitrary_variable(pat: ExprType) -> bool
```

Check if pattern is a variable matcher `['?v', name]`.

```python
arbitrary_variable(['?v', 'x'])  # True
```

## Dictionary Operations

### empty_dictionary

```python
def empty_dictionary() -> List
```

Create an empty bindings dictionary.

```python
bindings = empty_dictionary()  # []
```

---

### extend_dictionary

```python
def extend_dictionary(
    pat: List,
    dat: ExprType,
    dict_: DictType
) -> DictType
```

Add a new binding to the dictionary.

```python
from xtk.rewriter import extend_dictionary

bindings = []
pat = ['?', 'x']
bindings = extend_dictionary(pat, 42, bindings)
# Result: [['x', 42]]
```

---

### lookup

```python
def lookup(var: str, dict_: DictType) -> Any
```

Look up a variable in the bindings dictionary.

```python
from xtk.rewriter import lookup

bindings = [['x', 42], ['y', 3]]
lookup('x', bindings)  # 42
lookup('z', bindings)  # 'z' (returns var if not found)
```

## Rule Helpers

### pattern

```python
def pattern(rule: RuleType) -> ExprType
```

Extract the pattern from a rule.

```python
rule = [['+', ['?', 'x'], 0], [':', 'x']]
pattern(rule)  # ['+', ['?', 'x'], 0]
```

---

### skeleton

```python
def skeleton(rule: RuleType) -> ExprType
```

Extract the skeleton from a rule.

```python
rule = [['+', ['?', 'x'], 0], [':', 'x']]
skeleton(rule)  # [':', 'x']
```

## Type Definitions

```python
ExprType = Union[int, float, str, List]
DictType = Union[List[List], str]  # List of bindings or "failed"
RuleType = List[List]  # [pattern, skeleton]
```

## Exceptions

### MatchFailure

```python
class MatchFailure(Exception):
    """Exception raised when pattern matching fails."""
    pass
```

## Aliases

```python
simplifier = rewriter  # Backwards compatibility alias
```

## See Also

- [Simplifier API](simplifier.md)
- [Rule Loader API](rule-loader.md)
- [Rewrite Rules Guide](../user-guide/rules.md)
