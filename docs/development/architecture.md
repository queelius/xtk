# Architecture

This document describes the internal architecture of XTK (Expression Toolkit).

## Overview

XTK is organized into several layers:

```
+------------------+
|      CLI/REPL    |    User interface
+------------------+
|    Fluent API    |    High-level convenience
+------------------+
|     Rewriter     |    Core transformation engine
+------------------+
| Pattern Matching |    Expression matching
+------------------+
|   Expressions    |    AST representation
+------------------+
```

## Module Structure

```
src/xtk/
    __init__.py        # Package exports
    __main__.py        # Entry point for python -m xtk
    rewriter.py        # Core pattern matching and rewriting
    parser.py          # S-expression and DSL parsing
    rule_loader.py     # Rule file loading
    rule_utils.py      # Rule utilities and RichRule class
    step_logger.py     # Transformation tracking
    fluent_api.py      # Chainable expression interface
    cli.py             # Interactive REPL
    explainer.py       # LLM-powered explanations
    rules/             # Predefined rule sets
        deriv_rules.py
        algebra_rules.py
        trig-rules.py
        integral-rules.py
        ...
```

## Core Components

### Expression Representation

Expressions are nested Python lists (Abstract Syntax Trees):

```python
# Atomic expressions
42              # Constant
'x'             # Variable

# Compound expressions
['+', 'x', 3]   # x + 3
['*', ['+', 'x', 1], 2]  # (x + 1) * 2
```

Key type predicates in `rewriter.py`:

```python
def constant(exp) -> bool   # Is it a number?
def variable(exp) -> bool   # Is it a string?
def atom(exp) -> bool       # Is it atomic (constant or variable)?
def compound(exp) -> bool   # Is it a list?
```

### Pattern Matching (`rewriter.py`)

The `match()` function implements pattern matching:

```python
def match(pat, exp, dict_) -> DictType
```

Pattern types:
- `['?', 'x']` - Match any expression
- `['?c', 'c']` - Match constants only
- `['?v', 'v']` - Match variables only

The algorithm:
1. If pattern is atomic, check exact equality
2. If pattern is a pattern variable, extend bindings
3. If both are lists, recursively match elements

### Skeleton Instantiation (`rewriter.py`)

The `instantiate()` function builds expressions from templates:

```python
def instantiate(skeleton, dict_) -> ExprType
```

Skeleton syntax:
- `[':', 'x']` - Substitute value bound to `x`
- Literals remain unchanged

### Simplification Loop

The `rewriter()` function creates a simplifier:

```python
def rewriter(the_rules, step_logger=None, constant_folding=True)
```

Algorithm:
```
while changed:
    for each rule in rules:
        if match(rule.pattern, expr):
            expr = instantiate(rule.skeleton, bindings)
            break

    if constant_folding:
        try_evaluate_constants(expr)

    simplify_subexpressions(expr)
```

### Evaluation (`rewriter.py`)

The `evaluate()` function computes values:

```python
def evaluate(form, dict_) -> ExprType
```

Process:
1. Look up variables in bindings
2. Recursively evaluate sub-expressions
3. Apply operator functions to arguments

## Supporting Components

### Parser (`parser.py`)

Converts string representations to ASTs:

```python
def parse_sexpr(s: str) -> ExprType
def format_sexpr(expr: ExprType) -> str
```

Supports:
- S-expressions: `(+ x 3)`
- Infix notation (DSL)
- JSON format

### Rule Loader (`rule_loader.py`)

Loads rules from various formats:

```python
def load_rules(source) -> List[RuleType]
```

Supports:
- Python files (imports and extracts rule lists)
- JSON files
- Lisp/S-expression files
- Inline strings

### Step Logger (`step_logger.py`)

Tracks transformations for debugging/display:

```python
class StepLogger:
    def log_initial(self, expr)
    def log_rewrite(self, before, after, rule_pattern, rule_skeleton, bindings)
    def log_final(self, expr, metadata)
```

### Fluent API (`fluent_api.py`)

Provides chainable expression manipulation:

```python
from xtk.fluent_api import Expression, E

expr = E('+', 'x', 3)
result = expr.rewrite(rules).simplify().to_latex()
```

### CLI (`cli.py`)

Interactive REPL with features:
- Tab completion
- History (stored in `~/.xtk_history`)
- Commands: `/rules`, `/rewrite`, `/tree`, `/trace`, etc.
- Multiple input formats

## Data Flow

### Simplification Flow

```
Input Expression
       |
       v
+-------------+
|   Parser    |  (if string input)
+-------------+
       |
       v
+-------------+
|   Match     | <--- Rules
+-------------+
       |
       v (bindings)
+-------------+
| Instantiate |
+-------------+
       |
       v
+-------------+
|  Evaluate   | <--- Bindings (for constant folding)
+-------------+
       |
       v
Output Expression
```

### Rule Application

```
Expression: ['+', ['*', 'x', 1], 0]
                |
                v
Rule 1: [['*', ['?', 'x'], 1], [':', 'x']]
        Match: Yes, bindings = [['x', 'x']]
        Result: ['+', 'x', 0]
                |
                v
Rule 2: [['+', ['?', 'x'], 0], [':', 'x']]
        Match: Yes, bindings = [['x', 'x']]
        Result: 'x'
                |
                v
Output: 'x'
```

## Extension Points

### Custom Rules

Add rules by creating Python files:

```python
# my_rules.py
my_rules = [
    [['foo', ['?', 'x']], ['bar', [':', 'x']]],
]
```

### Custom Operators

Define operators in evaluation bindings:

```python
bindings = [
    ['custom_op', lambda a, b: a + b * 2],
]
```

### Custom Pattern Types

The pattern matching system can be extended by modifying the predicates in `rewriter.py`.

## Performance Considerations

### Rule Ordering

Rules are tried in order. Place frequently-matching rules first.

### Iteration Limit

The simplifier has a maximum of 1000 iterations to prevent infinite loops.

### Memoization

Currently, expressions are not memoized. For large expressions, consider caching intermediate results.

## Testing Architecture

Tests are organized by component:

```
tests/
    test_rewriter_comprehensive.py  # Main test suite
    test_matcher.py                 # Pattern matching tests
    test_instantiate.py             # Instantiation tests
    test_evaluate.py                # Evaluation tests
    test_parser.py                  # Parser tests
    test_fluent_api.py              # Fluent API tests
    test_cli.py                     # REPL tests
    test_rule_loader.py             # Rule loading tests
    test_integration.py             # End-to-end tests
    test_edge_cases.py              # Corner cases
```

All tests use `unittest.TestCase` with pytest as the runner.

## Dependencies

### Core (No External Dependencies)

The core rewriter module has no external dependencies beyond Python stdlib.

### Optional Dependencies

- `readline`: History and tab completion in REPL
- LLM providers (Anthropic, OpenAI, Ollama): For AI-powered explanations

### Development Dependencies

- `pytest`: Test runner
- `black`: Code formatting
- `flake8`: Linting
- `mypy`: Type checking
- `pytest-cov`: Coverage reporting

## See Also

- [Testing Guide](testing.md)
- [Contributing Guide](contributing.md)
- [Rewriter API](../api/rewriter.md)
