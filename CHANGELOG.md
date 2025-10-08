# Changelog

All notable changes to the XTK (Expression Toolkit) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-26

### Added
- Fluent API for chainable expression operations
- Step logger for tracking expression transformations
- Comprehensive parser supporting both S-expressions and infix notation
- Rule loader supporting JSON and Lisp-style rule formats
- Interactive REPL with tab completion and history
- Example collection demonstrating various features
- Type hints throughout the codebase
- Comprehensive test suite with 93% coverage

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