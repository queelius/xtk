# Testing

This guide covers testing practices for XTK development.

## Running Tests

### Basic Test Execution

```bash
# Run all tests
make test
# Or: python -m pytest tests/ -v

# Run with virtual environment
.venv/bin/python -m pytest tests/ -v
```

### Running Specific Tests

```bash
# Run a specific test file
python -m pytest tests/test_rewriter_comprehensive.py -v

# Run a specific test class
python -m pytest tests/test_rewriter_comprehensive.py::TestBasicListOperations -v

# Run a specific test method
python -m pytest tests/test_rewriter_comprehensive.py::TestBasicListOperations::test_car_valid_list -v
```

### Test Coverage

```bash
# Run with coverage report
make test-cov
# Or: python -m pytest tests/ --cov=xtk --cov-report=term-missing --cov-report=html

# View HTML report
open htmlcov/index.html
```

## Test Structure

### Test Organization

```
tests/
    test_rewriter_comprehensive.py  # Core functionality
    test_matcher.py                 # Pattern matching
    test_instantiate.py             # Skeleton instantiation
    test_evaluate.py                # Expression evaluation
    test_parser.py                  # S-expression parsing
    test_fluent_api.py              # Fluent interface
    test_cli.py                     # REPL commands
    test_rule_loader.py             # Rule loading
    test_rule_utils.py              # Rule utilities
    test_simplifier.py              # Simplification
    test_integration.py             # End-to-end tests
    test_edge_cases.py              # Corner cases
```

### Test Framework

Tests use Python's `unittest.TestCase` with pytest as the runner:

```python
import unittest
from xtk.rewriter import match, instantiate, evaluate

class TestPatternMatching(unittest.TestCase):
    def test_match_constant(self):
        pattern = ['?c', 'c']
        result = match(pattern, 42, [])
        self.assertEqual(result, [['c', 42]])

    def test_match_variable(self):
        pattern = ['?v', 'x']
        result = match(pattern, 'a', [])
        self.assertEqual(result, [['x', 'a']])
```

## Writing Tests

### Test Categories

#### Unit Tests

Test individual functions in isolation:

```python
class TestCarFunction(unittest.TestCase):
    def test_car_returns_first_element(self):
        result = car([1, 2, 3])
        self.assertEqual(result, 1)

    def test_car_with_nested_list(self):
        result = car([[1, 2], 3])
        self.assertEqual(result, [1, 2])

    def test_car_raises_on_empty_list(self):
        with self.assertRaises(ValueError):
            car([])

    def test_car_raises_on_non_list(self):
        with self.assertRaises(TypeError):
            car("not a list")
```

#### Integration Tests

Test components working together:

```python
class TestSimplificationIntegration(unittest.TestCase):
    def test_derivative_simplification(self):
        from xtk import rewriter
        from xtk.rule_loader import load_rules

        rules = load_rules('src/xtk/rules/deriv_rules.py')
        simplify = rewriter(rules)

        # d/dx(x^2) = 2x
        expr = ['dd', ['^', 'x', 2], 'x']
        result = simplify(expr)

        self.assertEqual(result, ['*', 2, 'x'])
```

#### Edge Case Tests

Test boundary conditions:

```python
class TestEdgeCases(unittest.TestCase):
    def test_empty_expression(self):
        simplify = rewriter([])
        result = simplify([])
        self.assertEqual(result, [])

    def test_deeply_nested_expression(self):
        # Create deeply nested expression
        expr = 'x'
        for _ in range(100):
            expr = ['+', expr, 0]

        simplify = rewriter([[['+', ['?', 'x'], 0], [':', 'x']]])
        result = simplify(expr)
        self.assertEqual(result, 'x')
```

### Test Patterns

#### Parameterized Tests

Test multiple cases with the same logic:

```python
class TestIdentityRules(unittest.TestCase):
    def setUp(self):
        self.simplify = rewriter([
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']],
        ])

    def test_additive_identity_cases(self):
        cases = [
            (['+', 'a', 0], 'a'),
            (['+', 'x', 0], 'x'),
            (['+', ['+', 'a', 'b'], 0], ['+', 'a', 'b']),
        ]
        for expr, expected in cases:
            with self.subTest(expr=expr):
                result = self.simplify(expr)
                self.assertEqual(result, expected)
```

#### Setup and Teardown

```python
class TestWithSetup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run once before all tests in class."""
        cls.rules = load_rules('src/xtk/rules/deriv_rules.py')

    def setUp(self):
        """Run before each test method."""
        self.simplify = rewriter(self.rules)

    def tearDown(self):
        """Run after each test method."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests in class."""
        pass
```

## Testing Specific Components

### Pattern Matching Tests

```python
class TestPatternMatching(unittest.TestCase):
    def test_universal_pattern(self):
        pattern = ['?', 'x']
        self.assertNotEqual(match(pattern, 42, []), "failed")
        self.assertNotEqual(match(pattern, 'a', []), "failed")
        self.assertNotEqual(match(pattern, ['+', 1, 2], []), "failed")

    def test_constant_pattern(self):
        pattern = ['?c', 'c']
        self.assertNotEqual(match(pattern, 42, []), "failed")
        self.assertEqual(match(pattern, 'x', []), "failed")

    def test_variable_pattern(self):
        pattern = ['?v', 'v']
        self.assertNotEqual(match(pattern, 'x', []), "failed")
        self.assertEqual(match(pattern, 42, []), "failed")
```

### Rule Tests

```python
class TestRules(unittest.TestCase):
    def test_rule_application(self):
        rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
        simplify = rewriter(rules)

        result = simplify(['+', 'a', 0])
        self.assertEqual(result, 'a')

    def test_rule_not_applicable(self):
        rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
        simplify = rewriter(rules)

        result = simplify(['*', 'a', 0])
        # Rule doesn't match, but constant folding might apply
        self.assertEqual(result, 0)
```

### Parser Tests

```python
class TestParser(unittest.TestCase):
    def test_parse_simple(self):
        result = parse_sexpr('(+ 1 2)')
        self.assertEqual(result, ['+', 1, 2])

    def test_parse_nested(self):
        result = parse_sexpr('(+ (* 2 x) 3)')
        self.assertEqual(result, ['+', ['*', 2, 'x'], 3])

    def test_format_round_trip(self):
        expr = ['+', ['*', 2, 'x'], 3]
        string = format_sexpr(expr)
        result = parse_sexpr(string)
        self.assertEqual(result, expr)
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
python -m pytest tests/ -v -s

# Show local variables on failure
python -m pytest tests/ -v --tb=long
```

### Debugging with pdb

```python
class TestDebugging(unittest.TestCase):
    def test_with_breakpoint(self):
        import pdb; pdb.set_trace()  # Debugger stops here
        result = match(pattern, expr, [])
        self.assertEqual(result, expected)
```

### Logging

Enable debug logging in tests:

```python
import logging

class TestWithLogging(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('xtk.rewriter')
        self.logger.setLevel(logging.DEBUG)
```

## Continuous Integration

Tests run automatically via GitHub Actions on:
- Push to any branch
- Pull requests to master

### CI Configuration

`.github/workflows/ci.yml` runs:
- Tests across Python 3.8, 3.9, 3.10, 3.11, 3.12
- Linting with flake8
- Type checking with mypy
- Build verification

## Best Practices

1. **Write tests first**: TDD helps design better APIs
2. **Test edge cases**: Empty inputs, large inputs, invalid inputs
3. **Use descriptive names**: `test_match_fails_when_constant_pattern_receives_variable`
4. **Keep tests independent**: Each test should work in isolation
5. **Use fixtures**: Avoid duplicating setup code
6. **Test error handling**: Verify exceptions are raised correctly
7. **Maintain coverage**: Aim for high coverage on core modules

## Common Test Commands

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific file
python -m pytest tests/test_rewriter_comprehensive.py -v

# Run matching tests
python -m pytest tests/ -k "match" -v

# Run failed tests only
python -m pytest tests/ --lf

# Run tests in parallel
python -m pytest tests/ -n auto
```

## See Also

- [Architecture](architecture.md)
- [Contributing Guide](contributing.md)
- [CI/CD Pipeline](https://github.com/queelius/xtk/actions)
