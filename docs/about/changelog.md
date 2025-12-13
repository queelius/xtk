# Changelog

All notable changes to the XTK (Expression Toolkit) project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2024-12-27

### Fixed
- Fixed test suite compatibility issues
- Improved CLAUDE.md documentation for development guidance

## [0.2.0] - 2024-12-26

### Added
- **Fluent API**: Chainable expression operations via `Expression` class
- **Step Logger**: Track expression transformations for debugging and display
- **Comprehensive Parser**: Support for both S-expressions and infix notation
- **Rule Loader**: Load rules from JSON and Lisp-style formats
- **Interactive REPL**: Tab completion, history, and multiple commands
- **Example Collection**: Demonstrations of various features
- **Type Hints**: Throughout the codebase for better IDE support
- **Comprehensive Test Suite**: 93% code coverage

### Changed
- Replaced string-based error handling ("failed") with proper exception handling
- Improved pattern matching algorithm for better performance
- Enhanced simplifier to support step logging
- Updated all imports to use consistent module structure
- Modernized package structure for PyPI distribution

### Fixed
- Fixed infinite recursion issues in derivative rules
- Corrected chain rule implementation
- Fixed various pattern matching edge cases
- Resolved import inconsistencies

### Removed
- Removed legacy rewriter implementation
- Removed conda-specific Makefile targets
- Removed tree-viewer integration (limited value)
- Consolidated duplicate test files
- Consolidated duplicate rule files

## [0.1.0] - 2024-08-27

### Added
- Initial release of XTK
- Core pattern matching and rewriting engine
- Basic mathematical rules (algebra, derivatives)
- Simple CLI interface
- Basic test suite

## [Unreleased]

### Planned
- Performance optimizations for large expressions
- Additional mathematical rule sets (integrals, limits, series)
- Plugin system for custom rule sets
- Documentation improvements
- Web-based playground
- Search algorithms for theorem proving

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.2.1 | 2024-12-27 | Test fixes, documentation improvements |
| 0.2.0 | 2024-12-26 | Major feature release: Fluent API, REPL, step logging |
| 0.1.0 | 2024-08-27 | Initial release |

## Upgrading

### From 0.1.x to 0.2.x

**Breaking Changes:**

1. **Import changes**: Use `from xtk import rewriter` instead of legacy imports
2. **Error handling**: Match failures may raise `MatchFailure` exception in some cases
3. **Module structure**: Some internal modules have been reorganized

**Migration Guide:**

```python
# Old (0.1.x)
from xtk.rewriter import simplifier
s = simplifier(rules)

# New (0.2.x)
from xtk import rewriter
s = rewriter(rules)  # simplifier is now an alias
```

## Contributing

See the [Contributing Guide](../development/contributing.md) for information on how to contribute to XTK.

## Reporting Issues

Please report bugs and feature requests on the [GitHub Issues](https://github.com/queelius/xtk/issues) page.
