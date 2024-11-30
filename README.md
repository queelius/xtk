# Expression Toolkit: `xtoolkit`

A rules-based expression rewriting toolkit for symbolic computation.

## Introduction

`xtoolkit` is a Python package that provides tools for symbolic computation through expression rewriting. It offers capabilities such as pattern matching, rule-based transformations, expression evaluation, theorem proving via tree search, and data generation for AI and machine learning applications.

## Quick Start

To quickly get started with `xtoolkit`, follow these steps:

1. **Installation**:

   Install `xtoolkit` from PyPI:

   ```sh
   pip install xtoolkit
   ```

2. **Basic Usage**:

   Here's a simple example of how to use `xtoolkit` to simplify an expression:

   ```python
   from xtoolkit import simplifier

   # Define a simplification rule: x + 0 => x
   rules = [
       [['+', ['?', 'x'], 0], [':', 'x']]
   ]

   # Create a simplifier function using the rule
   simplify = simplifier(rules)

   # Simplify an expression
   expr = ['+', 'a', 0]
   result = simplify(expr)
   print(f"Simplified expression: {result}")  # Output: Simplified expression: a
   ```

3. **Exploring More Features**:

   To explore more advanced features like symbolic differentiation, tree search algorithms for theorem proving, and working with predefined mathematical rules, refer to the detailed sections below.

## Table of Contents

- [Expression Toolkit: `xtoolkit`](#expression-toolkit-xtoolkit)
  - [Introduction](#introduction)
  - [Quick Start](#quick-start)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Overview](#overview)
  - [Representation of Rules and Expressions](#representation-of-rules-and-expressions)
    - [Rewrite Rules: Pattern Matching and Skeleton Instantiation](#rewrite-rules-pattern-matching-and-skeleton-instantiation)
      - [Abstract Syntax Tree (AST) Representation](#abstract-syntax-tree-ast-representation)
        - [Examples](#examples)
      - [Simplified Domain-Specific Language (DSL)](#simplified-domain-specific-language-dsl)
      - [Alternative JSON Representation](#alternative-json-representation)
    - [Expressions](#expressions)
  - [Pattern Matching](#pattern-matching)
  - [Skeleton Instantiation](#skeleton-instantiation)
  - [Evaluation](#evaluation)
    - [Example: Evaluating Expressions](#example-evaluating-expressions)
  - [Simplification Process](#simplification-process)
    - [The Simplification Process](#the-simplification-process)
    - [Example: Simplifying Expressions](#example-simplifying-expressions)
      - [Steps:](#steps)
      - [Example with Evaluation](#example-with-evaluation)
  - [Tree Search and Theorem Proving](#tree-search-and-theorem-proving)
    - [Search Algorithms](#search-algorithms)
  - [Modules](#modules)
    - [Core Modules](#core-modules)
    - [Search Modules](#search-modules)
  - [Predefined Rewrite Rules](#predefined-rewrite-rules)
  - [Notebooks and Examples](#notebooks-and-examples)
  - [The Power of Language Design](#the-power-of-language-design)

## Installation

To install the package locally from the source code:

```sh
git clone https://github.com/queelius/xtoolkit
cd xtoolkit
pip install -e .
```

To install it from PyPI:

```sh
pip install xtoolkit
```

## Overview

`xtoolkit` provides a comprehensive set of tools for symbolic computation:

- **Expression Rewriting Engine** (`xtoolkit/rewriter.py`): Functions for pattern matching, expression instantiation, evaluation, and simplification using transformation rules.

- **Simplifier** (`xtoolkit/simplifier.py`): A recursive simplifier that applies rewrite rules to expressions in a bottom-up manner, facilitating expression simplification.

- **Tree Search Algorithms** (`xtoolkit/search/`): Algorithms for theorem proving and exploring expression spaces, including BFS, DFS, IDDFS, Best-First Search, A\* Search, and Monte Carlo Tree Search.

- **Predefined Mathematical Rules** (`xtoolkit/rules/`): A collection of rules for various mathematical domains such as algebra, calculus, trigonometry, limits, and more.

- **Jupyter Notebooks** (`notebooks/`): Examples demonstrating the functionality of the package.

## Representation of Rules and Expressions

`xtoolkit` employs a powerful yet simple representation for rules and expressions, enabling efficient definition and manipulation of symbolic expressions.

### Rewrite Rules: Pattern Matching and Skeleton Instantiation

#### Abstract Syntax Tree (AST) Representation

Rewrite rules are defined using an abstract syntax tree (AST) representation, utilizing nested lists to represent expressions. Each rule consists of:

- **Pattern**: Defines the structure of the expression to match.
- **Skeleton**: A template for the replacement expression.

##### Examples

1. **Simplification Rule**: The sum of a variable `x` and zero simplifies to `x`.

   ```python
   [['+', ['?', 'x'], 0], [':', 'x']]
   ```

   - **Pattern**: `['+', ['?', 'x'], 0]`
   - **Skeleton**: `[':', 'x']`

2. **Derivative of a Constant**: The derivative of a constant `c` with respect to `x` is zero, \( \frac{d}{dx} c = 0 \).

   ```python
   [['dd', ['?c', 'c'], ['?', 'x']], 0]
   ```

   - **Pattern**: `['dd', ['?c', 'c'], ['?', 'x']]`
   - **Skeleton**: `0`

#### Simplified Domain-Specific Language (DSL)

For enhanced readability, `xtoolkit` offers a simplified DSL for writing rules:

```text
# Derivative of a constant: d(c)/dx = 0
dd (?c c) (?v x) = 0

# Derivative of a variable with respect to itself: d(x)/dx = 1
dd (?v x) (?v x) = 1

# Product rule: d(f * g)/dx = f' * g + f * g'
dd (* (? f) (? g)) (?v x) =
    (+ (* (dd (: f) (: x)) (: g))
       (* (: f) (dd (: g) (: x))))
```

In the DSL:

- `?c c`: Matches any constant and binds it to `c`.
- `?v x`: Matches any variable and binds it to `x`.
- `? f`, `? g`: Match any expressions and bind them to `f` and `g`.
- `:` is used in the skeleton to refer to matched variables from the pattern.

#### Alternative JSON Representation

Rules can also be represented as JSON objects, allowing for additional metadata:

```json
{
  "pattern": ["dd", ["?c", "c"], ["?v", "x"]],
  "replacement": 0,
  "name": "derivative_of_constant",
  "description": "The derivative of a constant is zero."
}
```

### Expressions

Expressions are represented in the same AST format as rules:

- `['+', 'x', 3]` represents \( x + 3 \).
- `['*', ['+', 'x', 3], 4]` represents \( (x + 3) \times 4 \).
- `['dd', ['*', 2, 'x'], 'x']` represents \( \frac{d}{dx} (2x) \).

## Pattern Matching

Pattern matching is used to determine if a rule can be applied to an expression. The syntax includes:

- **Exact Match**: An expression `foo` matches exactly `foo`.
- **List Match**: An expression `["f", "a", "b"]` matches a list with first element `"f"` and subsequent elements `"a"`, `"b"`.
- **Pattern Variables**:
  - `['?', 'x']`: Matches any expression and binds it to `x`.
  - `['?c', 'c']`: Matches any constant and binds it to `c`.
  - `['?v', 'x']`: Matches any variable and binds it to `x`.

This pattern-matching system is simple yet powerful, allowing for flexible expression transformations.

## Skeleton Instantiation

After matching, the skeleton is instantiated by replacing pattern variables with the matched expressions:

- **Direct Substitution**: `["f", "a", "b"]` remains unchanged.
- **Variable Substitution**: `[':', 'x']` is replaced with the expression bound to `x`.

For example, if `x` is bound to `3`, then `[':', 'x']` instantiates to `3`.

## Evaluation

The evaluator computes the value of instantiated skeleton expressions using a dictionary of bindings for operations and variables.

### Example: Evaluating Expressions

```python
from xtoolkit import evaluate

# Define the bindings
bindings = {
    '+': lambda x, y: x + y,
    'x': 3,
    'y': 4
}

# Evaluate the expression
expr = ['+', 'x', 'y']
result = evaluate(expr, bindings)
print(f"evaluate({expr}, {bindings}) => {result}")
# Output: evaluate(['+', 'x', 'y'], {'+': <function>, 'x': 3, 'y': 4}) => 7
```

In this example:

- The evaluator replaces `'x'` and `'y'` with their values `3` and `4`.
- It then applies the `+` operation to compute `7`.

## Simplification Process

Simplification involves recursively applying rewrite rules to an expression until it cannot be further reduced. The process works bottom-up, simplifying sub-expressions before moving up the expression tree.

### The Simplification Process

We can visualize the simplification process as follows:

```mermaid
graph TD
    A0(( )) -->|Expression| A
    B0(( )) -->|Pattern| A
    C0(( )) -->|Bindings| A
    D0(( )) -->|Skeleton| B
    A[Matcher] -->|Augmented Bindings| B
    B[Instantiator] -->|Instantiated Skeleton| C[Evaluator]
    C -->|Simplified Expression| A

    style A0 fill:none, stroke:none
    style B0 fill:none, stroke:none
    style C0 fill:none, stroke:none
    style D0 fill:none, stroke:none
```

1. **Matcher**: Matches the pattern against the expression and generates bindings.
2. **Instantiator**: Uses the bindings to instantiate the skeleton.
3. **Evaluator**: Evaluates the instantiated skeleton to produce a simplified expression.
4. **Recursive Application**: The process repeats until no further simplifications can be made.

### Example: Simplifying Expressions

**Simplify** `['+', 'x', 0]` using the rule that adding zero simplifies to the original expression.

- **Rule**: `[['+', ['?', 'x'], 0], [':', 'x']]`

#### Steps:

1. **Match**:

   - Pattern: `['+', ['?', 'x'], 0]`
   - Expression: `['+', 'x', 0]`
   - Binding: `{'x': 'x'}`

2. **Instantiate**:

   - Skeleton: `[':', 'x']`
   - Instantiated Skeleton: `'x'`

3. **Evaluate**:

   - Result: `'x'`

The expression simplifies from `['+', 'x', 0]` to `'x'`.

#### Example with Evaluation

Simplify `['+', 3, 5]` using the addition operation defined in the evaluator.

- **Bindings**: `{'x': 3, 'y': 5, '+': lambda x, y: x + y}`

- **Expression**: `['+', 'x', 'y']`

- **Evaluate**:

  - Replace `'x'` and `'y'` with `3` and `5`.
  - Apply `+` operation: `3 + 5 = 8`.

- **Result**: `8`

## Tree Search and Theorem Proving

Beyond simplification, `xtoolkit` provides tree search algorithms for tasks such as theorem proving, where the goal is to find a sequence of rewrites that transforms an expression into a target form.

### Search Algorithms

- **Breadth-First Search (BFS)**: Explores all nodes at the current depth before moving deeper.
- **Depth-First Search (DFS)**: Explores as far as possible along each branch before backtracking.
- **Iterative Deepening DFS (IDDFS)**: Combines DFS's space efficiency with BFS's completeness.
- **Best-First Search**: Uses a heuristic to explore more promising branches first.
- **A\* Search**: Combines path cost and heuristic information for optimal pathfinding.
- **Monte Carlo Tree Search (MCTS)**: Uses randomness and statistical sampling to explore the search space.

These algorithms can be used to prove equivalence between expressions, find transformations that satisfy certain conditions, or explore the space of possible rewrites.

## Modules

### Core Modules

- **`rewriter.py`**: Contains core functions for pattern matching, instantiation, and evaluation.

  - `match(pattern, expression, bindings)`: Matches a pattern against an expression using the provided bindings.
  - `instantiate(skeleton, bindings)`: Instantiates a skeleton using the bindings.
  - `evaluate(expression, bindings)`: Evaluates an expression using the bindings.

- **`simplifier.py`**:

  - `simplifier(rules)`: Returns a function to simplify expressions using the provided rules.

### Search Modules

Each search algorithm is implemented in its own module under `search/`:

- **`bfs.py`**: Breadth-First Search
- **`dfs.py`**: Depth-First Search
- **`iddfs.py`**: Iterative Deepening DFS
- **`best_first.py`**: Best-First Search
- **`astar.py`**: A\* Search
- **`mcts.py`**: Monte Carlo Tree Search

## Predefined Rewrite Rules

The `rules/` directory contains predefined rules for various mathematical domains:

- **`deriv_rules.py`**: Rules for symbolic differentiation.
- **`trig_rules.py`**: Trigonometric identities.
- **`limit_rules.py`**: Rules for computing limits.
- **`random_var_rules.py`**: Manipulations of random variables.
- **`integral_rules.py`**: Rules for integration.
- **`calculus_rules.py`**: General calculus rules.
- **`algebra_rules.py`**: Algebraic manipulation rules.

Additional rules cover domains such as differential equations, logic, set theory, combinatorics, graph theory, group theory, ring theory, field theory, vector spaces, linear algebra, topology, measure theory, probability theory, and statistics.

## Notebooks and Examples

The `notebooks/` directory contains Jupyter notebooks demonstrating the functionality of `xtoolkit`, including examples of simplification, evaluation, and theorem proving.

## The Power of Language Design

Designing a domain-specific language (DSL) enables expressing complex ideas concisely and readably. In `xtoolkit`, the DSL allows users to define transformation rules effectively, leveraging the power of symbolic computation and rule-based systems.

Our rules-based system is Turing-complete, capable of expressing any computable function. While powerful, such systems are better suited for symbolic computation, theorem proving, and other symbolic tasks rather than general-purpose programming.