# Installation

XTK can be installed using pip or from source.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Install from PyPI

The easiest way to install XTK is from PyPI:

```bash
pip install xpression-tk
```

Note: The package is published as `xpression-tk` but imported as `xtk`.

## Install from Source

To get the latest development version:

```bash
git clone https://github.com/queelius/xtk.git
cd xtk
pip install -e .
```

The `-e` flag installs the package in editable mode, which is useful for development.

## Verify Installation

Verify that XTK is installed correctly:

```python
import xtk
print(xtk.__version__)
```

Or launch the interactive REPL:

```bash
python -m xtk.cli
```

You should see the XTK prompt:

```
xtk>
```

## Optional Dependencies

### Development Tools

If you plan to contribute to XTK or run tests:

```bash
pip install xpression-tk[dev]
```

This installs:

- pytest - Testing framework
- pytest-cov - Code coverage
- black - Code formatter
- flake8 - Linter
- mypy - Type checker
- isort - Import sorter

### Documentation Tools

To build the documentation locally:

```bash
pip install mkdocs mkdocs-material pymdown-extensions
```

## System Requirements

XTK is a pure Python package and works on:

- Linux
- macOS
- Windows

Minimum system requirements:

- 100MB disk space
- 256MB RAM (more for complex computations)

## Troubleshooting

### Import Error

If you get `ModuleNotFoundError: No module named 'xtk'`:

1. Ensure you installed `xpression-tk` (not `xtk`)
2. Check your Python environment: `pip list | grep xpression`
3. Verify Python version: `python --version` (must be 3.8+)

### Permission Errors

On Unix systems, you may need to use `pip3` instead of `pip`, or install with `--user`:

```bash
pip3 install --user xpression-tk
```

Or use a virtual environment (recommended):

```bash
python3 -m venv xtk-env
source xtk-env/bin/activate  # On Windows: xtk-env\Scripts\activate
pip install xpression-tk
```

## Next Steps

Now that XTK is installed, check out the [Quick Start Guide](quickstart.md) to begin using it!
