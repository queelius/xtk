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
	@echo "  make install    - Create virtual environment and install package"
	@echo "  make test       - Run all tests"
	@echo "  make demo       - Run demo examples"
	@echo "  make repl       - Start interactive REPL"
	@echo "  make clean      - Remove build artifacts and cache files"
	@echo ""

# Create virtual environment and install package
.PHONY: install
install:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@echo "Installing package in development mode..."
	@$(VENV_PIP) install -e .
	@echo "✓ Installation complete. Activate with: source $(VENV)/bin/activate"

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	@$(VENV_PYTHON) test_runner.py

# Run demo
.PHONY: demo
demo:
	@echo "Running demo..."
	@$(VENV_PYTHON) demo.py
	@echo ""
	@echo "Running simple examples..."
	@$(VENV_PYTHON) example_simple.py

# Start REPL
.PHONY: repl
repl:
	@echo "Starting XTK REPL..."
	@$(VENV_PYTHON) -m src.xtk

# Clean up
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete
	@rm -rf .pytest_cache build dist *.egg-info
	@echo "✓ Cleanup complete"

# Quick test - run a simple expression
.PHONY: quick
quick:
	@$(VENV_PYTHON) -c "import sys; sys.path.insert(0, 'src'); from xtk import Expression; print(Expression(['+', 'x', 'y']).to_string())"
