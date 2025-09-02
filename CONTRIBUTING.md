# Contributing to XTK

Thank you for your interest in contributing to XTK! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/xtk.git
   cd xtk
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   make venv
   source .venv/bin/activate
   make install-dev
   ```

## Development Workflow

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure tests pass:
   ```bash
   make check  # Runs linting and tests
   ```

3. Format your code:
   ```bash
   make format
   ```

4. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

5. Push to your fork and create a Pull Request

## Code Style

- We use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length is 100 characters
- Follow PEP 8 guidelines
- Add type hints to all new functions
- Write descriptive docstrings for all public functions

## Testing

- Write tests for all new functionality
- Place tests in the `tests/` directory
- Run tests with `make test`
- Check coverage with `make test-cov`
- Aim for at least 80% test coverage for new code

## Documentation

- Update docstrings for any modified functions
- Update README.md if adding new features
- Add examples in the `examples/` directory for new functionality
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/) format

## Pull Request Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what changes you made and why
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update relevant documentation
5. **Commits**: Keep commits focused and atomic

## Adding New Rules

When adding new rule sets:

1. Create a new file in `src/xtk/rules/`
2. Follow the existing pattern from other rule files
3. Add comprehensive tests in `tests/test_rules_<name>.py`
4. Document the rules in the file's docstring
5. Add examples demonstrating the rules

## Reporting Issues

- Use GitHub Issues to report bugs or request features
- Provide a clear description and minimal reproducible example
- Include your Python version and platform information

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## Questions?

Feel free to open an issue for any questions about contributing!

## License

By contributing to XTK, you agree that your contributions will be licensed under the MIT License.