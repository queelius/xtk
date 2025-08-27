# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`xtk` (Expression Toolkit) is a rules-based expression rewriting toolkit for symbolic computation in Python. It provides pattern matching, rule-based transformations, expression evaluation, and theorem proving capabilities via tree search algorithms.

## Key Architecture

### Core Module Structure
- **Source Code**: Located in `src/xtk/`
- **Main Module**: `src/xtk/rewriter.py` - Contains core functions for pattern matching, instantiation, and evaluation
- **Rules Directory**: `src/xtk/rules/` - Contains predefined mathematical rules for various domains
- **Tests**: Located in `tests/` using unittest framework

### Expression Representation
Expressions use nested list (AST) format:
- `['+', 'x', 3]` represents x + 3
- `['*', ['+', 'x', 3], 4]` represents (x + 3) × 4

### Pattern Matching Syntax
- `['?', 'x']`: Matches any expression, binds to variable x
- `['?c', 'c']`: Matches any constant, binds to c
- `['?v', 'x']`: Matches any variable, binds to x
- `[':', 'x']`: In skeletons, substitutes with bound value of x

## Development Commands

### Build and Installation
```bash
# Install package in development mode
pip install -e .

# Install from PyPI
pip install xtk
```

### Testing
```bash
# Run all tests using unittest
python -m unittest discover -s tests -p "*.py"

# Run a specific test file
python -m unittest tests.test_rewriter
```

### Code Quality
```bash
# Format code with black (if using Makefile with conda)
make format

# Lint with flake8 (if using Makefile with conda)
make lint
```

Note: The Makefile assumes a conda environment named "xtoolkit". For standard Python development, use the pip commands directly.

## Important Implementation Notes

1. **Module Imports**: The package is installed as `xpression-tk` but imported as `xtk`
2. **Logging**: The rewriter module has debug logging enabled - be aware of verbose output during development
3. **Error Handling**: Pattern matching returns "failed" string on failure, not exceptions
4. **Rules Format**: Rules are lists of [pattern, skeleton] pairs where patterns match expressions and skeletons define replacements

## Common Development Tasks

When implementing new features:
1. Add new rule files to `src/xtk/rules/` following existing patterns
2. Write corresponding tests in `tests/` using unittest framework
3. Update the README.md if adding new capabilities or changing API

When debugging:
- Check logging output from rewriter.py for detailed pattern matching traces
- Use the test files as examples for proper API usage