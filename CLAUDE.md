# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`xtk` (Expression Toolkit) is a rules-based expression rewriting toolkit for symbolic computation in Python. It provides pattern matching, rule-based transformations, expression evaluation, and an interactive REPL with rich visualizations.

**Package Name Discrepancy**: The package is installed as `xpression-tk` on PyPI but imported as `xtk` in Python code.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (recommended)
make venv
source .venv/bin/activate

# Install in development mode
make install

# Install with development dependencies (pytest, black, flake8, mypy)
make install-dev

# Alternative: Direct pip install
pip install -e .
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests with pytest
make test
# Or: python -m pytest tests/ -v
# Or: .venv/bin/python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_rewriter_comprehensive.py -v

# Run tests with coverage
make test-cov
# Or: python -m pytest tests/ --cov=xtk --cov-report=term-missing --cov-report=html

# Run a specific test class or method
python -m pytest tests/test_rewriter_comprehensive.py::TestBasicListOperations::test_car_valid_list -v
```

### Code Quality
```bash
# Format code with black
make format
# Or: python -m black src/ tests/ examples/

# Lint with flake8
make lint
# Or: python -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

# Type check with mypy
mypy src/xtk --ignore-missing-imports

# Run all checks (lint + test)
make check
```

### Interactive REPL
```bash
# Start the interactive REPL (recommended for exploration)
make repl
# Or: python -m xtk.cli
# Or: .venv/bin/python -m xtk.cli

# Run demo examples
make demo
```

### Building and Distribution
```bash
# Build distribution packages
make build
# Or: python -m build

# Clean build artifacts
make clean
```

## Architecture Overview

### Core Module Structure
- **`src/xtk/rewriter.py`**: Core symbolic computation engine
  - Pattern matching via `match(pattern, expression, bindings)`
  - Skeleton instantiation via `instantiate(skeleton, bindings)`
  - Expression evaluation via `evaluate(expression, bindings)`
  - List operations: `car()`, `cdr()`, `cons()`
  - Type predicates: `atom()`, `compound()`, `constant()`, `variable()`

- **`src/xtk/parser.py`**: S-expression and DSL parsing
  - `parse_sexpr()`: Converts "(+ 1 2)" to `['+', 1, 2]`
  - `format_sexpr()`: Converts AST back to S-expression string
  - `dsl_parser()`: Handles readable DSL syntax

- **`src/xtk/fluent_api.py`**: Fluent interface for expression manipulation
  - `Expression` class wraps expressions with chainable methods
  - `ExpressionBuilder` (aliased as `E`) for constructing expressions
  - Methods: `rewrite()`, `evaluate()`, `to_latex()`, `simplify()`

- **`src/xtk/cli.py`**: Interactive REPL with rich TUI
  - Tab completion for commands and variables
  - History tracking (`~/.xtk_history`)
  - Tree visualization, LaTeX rendering, step-by-step tracing
  - Commands: `/rewrite`, `/eval`, `/tree`, `/trace`, `/explain`, `/rules`, etc.

- **`src/xtk/rules/`**: Predefined mathematical transformation rules
  - `deriv_rules.py`: Symbolic differentiation (product rule, chain rule, etc.)
  - `algebra_rules.py`: Algebraic identities and simplifications
  - `trig_rules.py`: Trigonometric identities
  - `integral_rules.py`: Integration rules
  - `limit_rules.py`: Limit computation rules
  - Rich variants (`*_rich.py`): Same rules with metadata for explanations

- **`src/xtk/explainer.py`**: LLM-powered rewrite explanations
  - Supports Anthropic, OpenAI, Ollama providers
  - Fallback to rule-based explanations if no API key
  - Configured via `XTK_LLM_PROVIDER` environment variable

- **`src/xtk/rule_loader.py`**: Dynamic rule loading from files
- **`src/xtk/rule_utils.py`**: Rule normalization and `RichRule` class
- **`src/xtk/step_logger.py`**: Step-by-step transformation tracking

### Expression Representation
Expressions use nested list (AST) format:
- `['+', 'x', 3]` represents x + 3
- `['*', ['+', 'x', 3], 4]` represents (x + 3) × 4
- `['dd', ['*', 2, 'x'], 'x']` represents d/dx(2x)

### Pattern Matching Syntax
- **`['?', 'x']`**: Matches any expression, binds to variable `x`
- **`['?c', 'c']`**: Matches any constant, binds to `c`
- **`['?v', 'x']`**: Matches any variable, binds to `x`
- **`[':', 'x']`**: In skeletons, substitutes with bound value of `x`

### Rule Format
Rules are `[pattern, skeleton]` pairs:
```python
# Example: x + 0 => x
[['+', ['?', 'x'], 0], [':', 'x']]

# Example: d/dx(c) = 0 for constant c
[['dd', ['?c', 'c'], ['?v', 'x']], 0]
```

## Testing Architecture

Tests use Python's `unittest` framework (not pytest assertions, though pytest is the runner):
- **`test_rewriter_comprehensive.py`**: Main test suite for core functions
- **`test_matcher.py`**: Pattern matching tests
- **`test_instantiate.py`**: Skeleton instantiation tests
- **`test_evaluate.py`**: Expression evaluation tests
- **`test_parser.py`**: Parser tests for S-expressions and DSL
- **`test_fluent_api.py`**: Fluent interface tests
- **`test_cli.py`**: REPL command tests
- **`test_integration.py`**: End-to-end workflow tests
- **`test_edge_cases.py`**: Corner cases and error handling

All test files import from `xtk.rewriter`, `xtk.parser`, etc., and use `unittest.TestCase` classes.

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):
- Tests across Python 3.8, 3.9, 3.10, 3.11, 3.12
- Linting with flake8 (max line length 100, ignores E203, W503)
- Type checking with mypy
- Coverage reporting to Codecov
- Build verification with `python -m build`

## Important Implementation Notes

1. **Logging**: `rewriter.py` uses Python's logging module - debug logs can be verbose
2. **Pattern Match Failures**: Return special "failed" string, not exceptions (except `MatchFailure` class)
3. **REPL History**: Stored in `~/.xtk_history` with readline support
4. **Virtual Environment**: Makefile assumes `.venv/` for isolation
5. **Entry Points**: Can run via `python -m xtk.cli` or `xtk` command after install
6. **Empty List Handling**: `car()` raises ValueError on empty lists; code guards against this
7. **Callable Rejection**: Pattern matching rejects callable objects in arbitrary expressions

## Common Gotchas

- The package name on PyPI is `xpression-tk`, but you `import xtk`
- Tests use `unittest.TestCase`, not bare pytest assertions
- Pattern matching uses nested lists, not strings: `['+', 'x', 0]` not `"+ x 0"`
- Makefile targets assume virtual environment exists at `.venv/`
- `ExpressionBuilder` static methods (E.add, E.power) return Expression objects - don't nest them as arguments
- Infinite loop detection for identity rules is not yet implemented (see skipped tests)
