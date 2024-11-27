# Makefile for xtoolkit Python project using conda and unittest

# Variables
CONDA_ENV = xtoolkit
PYTHON = conda run -n $(CONDA_ENV) python
BLACK = conda run -n $(CONDA_ENV) black
FLAKE8 = conda run -n $(CONDA_ENV) flake8
PIP = conda run -n $(CONDA_ENV) pip

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make init         - Install dependencies in the conda environment"
	@echo "  make clean        - Remove temporary files and caches"
	@echo "  make test         - Run tests with unittest"
	@echo "  make lint         - Run code linting with flake8"
	@echo "  make format       - Format code with black"
	@echo "  make all          - Run tests, linting, and formatting"

# Initialize the project
.PHONY: init
init:
	@echo "Installing dependencies in the conda environment..."
	conda activate $(CONDA_ENV) && \
	$(PIP) install -r requirements.txt

# Clean up temporary files
.PHONY: clean
clean:
	@echo "Cleaning up..."
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache

# Run tests
.PHONY: test
test:
	@echo "Running tests with unittest..."
	$(PYTHON) -m unittest discover -s tests -p "*.py"

# Lint code
.PHONY: lint
lint:
	@echo "Running flake8 linting..."
	$(FLAKE8) xtoolkit

# Format code
.PHONY: format
format:
	@echo "Formatting code with black..."
	$(BLACK) xtoolkit

# Run all checks
.PHONY: all
all: test lint format
	@echo "All checks passed!"
