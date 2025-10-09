# Contributing to XTK

Thank you for your interest in contributing to XTK! This guide will help you get started.

## Ways to Contribute

There are many ways to contribute to XTK:

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Documentation**: Improve or add to the documentation
- **Code**: Fix bugs or implement new features
- **Examples**: Add examples or tutorials
- **Rules**: Contribute new mathematical rule sets

## Getting Started

### 1. Fork and Clone

Fork the repository on GitHub and clone it locally:

```bash
git clone https://github.com/YOUR-USERNAME/xtk.git
cd xtk
```

### 2. Set Up Development Environment

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

This installs XTK in editable mode with development dependencies.

### 3. Create a Branch

Create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Running Tests

Run the full test suite:

```bash
python -m unittest discover -s tests -p "*.py"
```

Run a specific test file:

```bash
python -m unittest tests.test_rewriter
```

### Test Coverage

Check test coverage:

```bash
pytest --cov=xtk tests/
```

Aim for high coverage (90%+) for new code.

### Code Style

XTK follows PEP 8 style guidelines. Format your code with black:

```bash
black src/xtk tests
```

Check with flake8:

```bash
flake8 src/xtk tests
```

### Type Checking

Run mypy for type checking:

```bash
mypy src/xtk
```

## Making Changes

### Code Changes

1. **Keep changes focused**: One feature or fix per PR
2. **Write tests**: Add tests for new functionality
3. **Update docs**: Update documentation if needed
4. **Follow style**: Use black, follow PEP 8
5. **Type hints**: Add type annotations

### Example: Adding a New Function

```python
def new_function(expr: ExprType, param: int) -> ExprType:
    """
    Brief description of what the function does.

    Args:
        expr: Description of expr parameter
        param: Description of param parameter

    Returns:
        Description of return value

    Example:
        >>> new_function(['+', 'x', 3], 2)
        ['+', 'x', 5]
    """
    # Implementation here
    pass
```

### Adding Rules

To contribute new rule sets:

1. Create a new file in `src/xtk/rules/`
2. Follow the existing rule format
3. Add documentation comments
4. Add tests in `tests/`

Example:

```python
"""
Hyperbolic trig rules for XTK.

This module provides rewrite rules for hyperbolic trigonometric functions.
"""

rules = [
    # sinh(x) = (e^x - e^(-x))/2
    [['sinh', ['?', 'x']],
     ['/', ['-', ['^', 'e', [':', 'x']],
                 ['^', 'e', ['-', 0, [':', 'x']]]], 2]],

    # Add more rules...
]
```

### Documentation Changes

Documentation is in markdown format in the `docs/` directory. To contribute:

1. Edit or create `.md` files
2. Follow existing structure
3. Use clear, concise language
4. Include code examples
5. Build locally to verify

Build docs with MkDocs:

```bash
mkdocs serve
```

Then visit http://127.0.0.1:8000

## Pull Request Process

### 1. Before Submitting

- [ ] Tests pass locally
- [ ] Code is formatted (black)
- [ ] No linting errors (flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] Commit messages are clear

### 2. Submit PR

Push your branch and create a pull request:

```bash
git push origin feature/your-feature-name
```

Then open a PR on GitHub.

### 3. PR Description

Write a clear description:

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- List of specific changes
- Another change

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted
- [ ] Type hints added
```

### 4. Review Process

- Maintainers will review your PR
- Address any feedback
- Update your branch if needed
- Once approved, it will be merged

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Keep functions focused and small
- Prefer functional style where appropriate

### Testing Standards

- Write unit tests for all new code
- Use descriptive test names
- Test edge cases
- Aim for high coverage

Example test:

```python
class TestNewFunction(unittest.TestCase):
    def test_basic_case(self):
        """Test basic functionality."""
        result = new_function(['+', 'x', 3], 2)
        self.assertEqual(result, ['+', 'x', 5])

    def test_edge_case(self):
        """Test edge case with zero."""
        result = new_function(['+', 'x', 0], 0)
        self.assertEqual(result, ['+', 'x', 0])
```

### Documentation Standards

- Write clear, concise documentation
- Include examples in docstrings
- Update user guides for new features
- Use proper markdown formatting

## Bug Reports

When reporting bugs, include:

1. **Description**: What's the problem?
2. **Reproduction**: Steps to reproduce
3. **Expected**: What should happen?
4. **Actual**: What actually happens?
5. **Environment**: Python version, OS, XTK version

Example:

```markdown
**Bug Description**
Pattern matching fails for nested lists

**To Reproduce**
```python
pattern = ['+', ['?', 'x'], ['?', 'y']]
expr = ['+', ['+', 'a', 'b'], 'c']
result = match(pattern, expr, {})
# Returns "failed" but should succeed
```

**Expected Behavior**
Should return {'x': ['+', 'a', 'b'], 'y': 'c'}

**Actual Behavior**
Returns "failed"

**Environment**
- Python 3.9
- XTK 0.2.0
- Ubuntu 20.04
```

## Feature Requests

When requesting features:

1. **Use case**: Why is this needed?
2. **Description**: What should it do?
3. **Example**: Show example usage
4. **Alternatives**: What are workarounds?

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on the code, not the person

### Communication

- **Issues**: For bugs and features
- **Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

## Recognition

Contributors will be:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation (for major contributions)

## Questions?

If you have questions:

1. Check the [documentation](https://github.com/queelius/xtk)
2. Search existing [issues](https://github.com/queelius/xtk/issues)
3. Open a new issue with your question

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to XTK!
