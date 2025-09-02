# Simple Makefile for xtk Python project

# Python command - use python3 by default
PYTHON := python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

# Default target - show help
.PHONY: help
help:
	@echo "xtk Development Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make venv          - Create virtual environment"
	@echo "  make install       - Install package in development mode"
	@echo "  make install-dev   - Install with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Check code style"
	@echo "  make check         - Run all checks (lint + test)"
	@echo ""
	@echo "Usage:"
	@echo "  make repl          - Start interactive REPL"
	@echo "  make demo          - Run demo examples"
	@echo ""
	@echo "Build:"
	@echo "  make build         - Build distribution packages"
	@echo "  make clean         - Remove build artifacts"
	@echo ""

# Create virtual environment
.PHONY: venv
venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@echo "✓ Virtual environment created. Activate with: source $(VENV)/bin/activate"

# Install package in development mode
.PHONY: install
install:
	@echo "Installing package in development mode..."
	@$(VENV_PIP) install -e .
	@echo "✓ Package installed"

# Install with development dependencies
.PHONY: install-dev
install-dev:
	@echo "Installing package with development dependencies..."
	@$(VENV_PIP) install -e ".[dev]"
	@echo "✓ Development dependencies installed"

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	@$(VENV_PYTHON) -m pytest tests/ -v

# Run tests with coverage
.PHONY: test-cov
test-cov:
	@echo "Running tests with coverage..."
	@$(VENV_PYTHON) -m pytest tests/ --cov=xtk --cov-report=term-missing --cov-report=html
	@echo "✓ Coverage report generated in htmlcov/"

# Format code
.PHONY: format
format:
	@echo "Formatting code with black..."
	@$(VENV_PYTHON) -m black src/ tests/ examples/ 2>/dev/null || echo "Install black with: make install-dev"
	@echo "✓ Code formatted"

# Lint code
.PHONY: lint
lint:
	@echo "Checking code style..."
	@$(VENV_PYTHON) -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503 2>/dev/null || echo "Install flake8 with: make install-dev"
	@echo "✓ Linting complete"

# Run all checks
.PHONY: check
check: lint test
	@echo "✓ All checks passed!"

# Run demo examples
.PHONY: demo
demo:
	@echo "Running demo examples..."
	@$(VENV_PYTHON) examples/simple_step_logging.py 2>/dev/null || echo "First run: make install"
	@echo "✓ Demo complete"

# Start REPL
.PHONY: repl
repl:
	@echo "Starting XTK REPL..."
	@$(VENV_PYTHON) -m xtk.cli

# Build distribution packages
.PHONY: build
build: clean
	@echo "Building distribution packages..."
	@$(PYTHON) -m build 2>/dev/null || (echo "Installing build tools..." && pip install build && $(PYTHON) -m build)
	@echo "✓ Packages built in dist/"

# Clean up
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete
	@rm -rf .pytest_cache build dist *.egg-info .coverage htmlcov/
	@echo "✓ Cleanup complete"
