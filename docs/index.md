# XTK - Expression Toolkit

[![CI](https://github.com/queelius/xtk/actions/workflows/ci.yml/badge.svg)](https://github.com/queelius/xtk/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/xpression-tk.svg)](https://badge.fury.io/py/xpression-tk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Welcome to **XTK** (Expression Toolkit), a powerful symbolic expression toolkit for rule-based term rewriting in Python. XTK provides pattern matching, expression transformation, and symbolic computation capabilities with an interactive REPL featuring rich visualizations.

## What is XTK?

XTK is a Python package that enables symbolic computation through expression rewriting. It offers:

- **Pattern Matching**: Powerful and flexible pattern matching for symbolic expressions
- **Rule-Based Transformations**: Define and apply rewrite rules to transform expressions
- **Expression Evaluation**: Evaluate symbolic expressions with custom bindings
- **Theorem Proving**: Use tree search algorithms to prove mathematical theorems
- **Interactive REPL**: Explore and test expressions with rich visualizations
- **Predefined Rules**: Extensive collection of mathematical rules for algebra, calculus, trigonometry, and more

## Key Features

### Expression Rewriting Engine
Transform symbolic expressions using pattern matching and rewrite rules. The system uses a simple yet powerful AST representation based on nested lists.

### Tree Search Algorithms
Explore expression spaces and prove theorems using various search strategies:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Iterative Deepening DFS (IDDFS)
- Best-First Search
- A* Search
- Monte Carlo Tree Search (MCTS)

### Rich Mathematical Library
Comes with predefined rules for:

- Symbolic differentiation
- Integration
- Algebraic manipulation
- Trigonometric identities
- Limits and calculus
- And much more!

### Interactive Development
Work with expressions interactively using the built-in REPL with syntax highlighting, tree visualization, and step-by-step transformation tracking.

## Quick Example

```python
from xtk import rewriter

# Define a rewrite rule: x + 0 => x
rules = [
    [['+', ['?', 'x'], 0], [':', 'x']]
]

# Create a rewriter function
rewrite = rewriter(rules)

# Apply the rule
expr = ['+', 'a', 0]
result = rewrite(expr)
print(result)  # Output: 'a'
```

## Why XTK?

- **Simple and Powerful**: Easy-to-learn AST representation that's also expressive
- **Turing Complete**: The rule system can express any computable function
- **Extensible**: Add your own rules and search strategies
- **Well-Tested**: Comprehensive test suite with high coverage
- **Educational**: Great for learning about symbolic computation and term rewriting

## Get Started

Ready to dive in? Check out our [Quick Start Guide](getting-started/quickstart.md) or [install XTK](getting-started/installation.md) now!

## Applications

XTK is perfect for:

- **Computer Algebra Systems**: Build your own CAS with custom rules
- **Theorem Proving**: Automatically prove mathematical theorems
- **Expression Optimization**: Find simplified or equivalent forms
- **Educational Tools**: Teach symbolic manipulation and mathematics
- **Research**: Experiment with term rewriting and symbolic AI

## Community

- **GitHub**: [github.com/queelius/xtk](https://github.com/queelius/xtk)
- **Issues**: [Report bugs or request features](https://github.com/queelius/xtk/issues)
- **PyPI**: [xpression-tk](https://pypi.org/project/xpression-tk/)

## License

XTK is released under the [MIT License](about/license.md).
