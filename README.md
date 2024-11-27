# Expression Toolkit: `xtoolkit`

Note: Broke some of the logic, will fix soon.

## Overview

This project is a Python package that provides tools for expression rewriting,
including pattern matching, rule-based transformations (which may sometimes
be considered simplifications, but it depends on the rules), and evaluation of
expressions.

The package includes:

- An expression rewriting engine in `xtoolkit/rewriter.py`, which provides functions for matching patterns, instantiating expressions, evaluating forms, and simplifying expressions using transformation rules.
- A set of predefined mathematical rules in `xtoolkit/rules/` for basic algebra, calculus, trigonometry, etc.
- Jupyter notebooks in `notebooks/` that demonstrate and test the functionality of the package.

## Installation

To install the package locally, navigate to the root directory and run:

```sh
pip install -e .
```

## Usage

Here are some examples of how to use the package.

### Simplifier

You can use the `simplifier` function from `xtoolkit/rewriter.py` to simplify mathematical expressions based on a set of transformation rules.

#### Example: Simplifying Derivatives

Consider the rule for the derivative of a constant, $d/dx c = 0$ where $c$ is
a constant with respect to $x$. This rule can be represented as:

```python
[['dd', ['?c', 'c'], ['?v', 'v']], 0]
```

Using this rule, we can simplify the derivative of a constant expression:

```python
from exprtoolkit.rewriter import simplifier

# Define the rule
rules = [
    [['dd', ['?c', 'c'], ['?v', 'v']], 0]
]

# Create the simplifier function
simplify = simplifier(rules)

# Simplify the expression
expr = ['dd', 3, 'x']
result = simplify(expr)
print(f"{expr} =>, {result}")
# Output: ['dd', 3, 'x'] => 0
```

Note that `['dd, ['?c', 'a'], ['?v', 'x']]` is a pattern that matches the
derivative of a constant `a` with respect to variable `x`,

$$
dc/dv = 0
$$

where `?c` and `?v` respectively match constants and variables.
Additionally, `?` matfches any expression. Thus, `[?c, 'a']` matches arbitrary
constants, which we name `a`, `[?v, 'x']` matches arbitrary variables, which we
name `x`, and `[? , 'e']` matches any expression that we name `e`.

This is the AST representation of the rule. The rule itself is a list with two
elements: the pattern and the skeleton replacement. The pattern is a list with the first
element being the operator and the rest being the operands. The skeleton is
a template for the replacement expression. More details later.

A rule can also be a JSON object, which allows for attaching metadata
to the rule. Here is the same rule as a JSON object:

```json
{
    "pattern": ["dd", ["?c", "a"], ["?v", "x"]],
    "replacement": 0,
    "name": "derivative_of_constant",
    "description": "The derivative of a constant is zero."
}
```

Furthermore, we provide a DSL for writing rules in a more human-readable format.
Here are three rules in the DSL:

```text
# d(c)/dx = 0 # dc/dx = 0
(dd (?c a) (?v x)) = 0 # da/dx = 0

# d(x)/dx = 1 # dx/dx = 1
(dd (?v x) (?v x)) = 1 # dx/dx = 1

# d(f*g)/dx = f'g + fg'
(dd (*
    ((? f) (? g)) (?v x))
    =
(+ 
    (* (dd (: f) (: x)) (: g))
    (* (: f) (dd (: g) (: x))
)
```

The LHS of `=` represents the pattern annd the RHS represents the replacement.
`?c a`, `?v x`, and `? f` respectively map to `['?c', 'a']` and `['?v', 'x']`.
In the last rule, we see replacement expressions that use `: f` and `: x` to
refer to the matched expressions in the pattern. We substitute into the
skeleton the matched expressions in the pattern,  e.g., if we have an expression
`(* x (+ y x))`, then `? f` would match `x` and `? g` would match `(+ y x)`.
In the skeleton, `: f` would be replaced by `x` and `: g` would be replaced by
`(+ y x)`. The *instantiated* skeleton is thus `(+ (* (dd x x) (+ y x)) (* x (dd (+ y x) x)))`.

The DSL is more concise and easier to read than the AST representation, and it
is converted to the AST representation before being used by the simplifier.
You may want to use the AST (even the JSON version) if you need to
programmatically generate or manipulate rules. The AST is also easier to
serialize and deserialize for storage or transmission.

### Evaluator

The `evaluate` function can evaluate expressions given a dictionary of values and operations.
This is typically not used standalone, but as part of a larger system that uses the rewriter engine.
However, it can be useful for simple evaluations.

#### Example: Evaluating Expressions

```python
from xtoolkit import evaluate

# Define the dictionary
dict1 = [
    ['+', lambda x, y: x + y],
    ['x', 3],
    ['y', 4]
]

# Evaluate the expression
form1 = ['+', 'x', 'y']
result = evaluate(form1, dict1)
print(f"evaluate({form1}, {dict1}) => {result}")
# Output: evaluate(['+', 'x', 'y'], [['+', <function <lambda>...>], ['x', 3], ['y', 4]]) => 7
```

## AST Representation

The Abstract Syntax Tree (AST) in this project represents expressions as nested lists. Here are some examples:

- `['+', 'x', 3]` represents the expression \( x + 3 \).
- `['*', ['+', 'x', 0], 1]` represents \( (x + 0) \times 1 \).
- `['dd', 'x', 'x']` represents the derivative \( \frac{d}{dx} x \).

## Modules

### `rewriter.py`

This module contains the core functions:

- `match(pat, exp, dict)`

: Matches a pattern `pat` against an expression `exp` using a dictionary `dict`.

- `instantiate(skeleton, dict)`

: Instantiates a `skeleton` expression using the dictionary `dict`.

- `evaluate(form, dict)`

: Evaluates an expression `form` using the dictionary `dict`.

- `simplifier(the_rules)`

: Returns a function to simplify expressions using `the_rules`


### `xtoolkit/rules/`

This directory contains predefined rules for various mathematical operations:

- `basic-algebra.py` have rules for basic algebraic operations.
- `deriv-rules.py` have rules for symbolically taking derivatives.
- `trig-rules.py` have rules for trigonometric functions.
- etc.

## Testing

The `notebooks` directory contains Jupyter notebooks that demonstrate and test
the functionality:

## License

This project is licensed under the MIT License.
