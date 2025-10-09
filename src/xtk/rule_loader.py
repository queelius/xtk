"""
Elegant rule loading for xtk.

Leverages the existing S-expression parser for all formats.
"""

import json
import re
import sys
import importlib.util
from pathlib import Path
from typing import List, Union

from .parser import parse_sexpr, format_sexpr
from .rewriter import RuleType


def load_rules(source: Union[str, Path, List]) -> List[RuleType]:
    """
    Load rules from various sources.

    Args:
        source: Can be a filepath (.json, .lisp, .py), a list of rules,
                or a string containing rules

    Returns:
        List of [pattern, skeleton] rules
    """
    # Already a list of rules
    if isinstance(source, list):
        return source

    # File path
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists():
            # Handle Python files specially
            if path.suffix == '.py':
                return load_python_rules(path)

            with open(path, 'r') as f:
                content = f.read()
        else:
            # Treat as inline rule string
            content = str(source)

        return parse_rules(content)

    raise ValueError(f"Cannot load rules from {type(source)}")


def load_python_rules(path: Path) -> List[RuleType]:
    """
    Load rules from a Python file by importing it.

    The Python file should export rules as lists, e.g.:
        deriv_rules_fixed = [[pattern, skeleton], ...]
        simplify_rules = [[pattern, skeleton], ...]

    This function will collect all list variables that look like rule sets.
    """
    # Import the module dynamically
    spec = importlib.util.spec_from_file_location("_xtk_rules_module", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load Python module from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["_xtk_rules_module"] = module
    spec.loader.exec_module(module)

    # Collect all rules from the module
    all_rules = []

    for name in dir(module):
        if name.startswith('_'):
            continue

        obj = getattr(module, name)

        # Check if it looks like a rule set
        if isinstance(obj, list) and obj and is_rule_format(obj[0]):
            all_rules.extend(obj)

    # Clean up
    if "_xtk_rules_module" in sys.modules:
        del sys.modules["_xtk_rules_module"]

    return all_rules


def parse_rules(content: str) -> List[RuleType]:
    """
    Parse rules from a string, auto-detecting format.
    
    Supports:
    - JSON arrays
    - S-expressions (single rules or pattern/skeleton pairs)
    - Comments with ; or //
    """
    content = content.strip()
    
    # Try JSON first
    if content.startswith('['):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
    
    # Otherwise parse as S-expressions
    # Remove comments
    content = re.sub(r';[^\n]*|//[^\n]*', '', content)
    
    # Extract all S-expressions
    sexprs = extract_sexprs(content)
    
    if not sexprs:
        return []
    
    # Parse expressions
    parsed = [parse_sexpr(s) for s in sexprs]
    
    # Determine format and convert to rules
    if is_rule_format(parsed[0]):
        # Each expression is a complete rule: ((pattern) (skeleton))
        return parsed
    else:
        # Alternating pattern/skeleton format
        return list(zip(parsed[::2], parsed[1::2]))


def extract_sexprs(text: str) -> List[str]:
    """Extract all complete S-expressions from text."""
    sexprs = []
    depth = 0
    current = []
    
    for char in text:
        if char == '(':
            if depth == 0:
                current = []
            depth += 1
        
        if depth > 0:
            current.append(char)
        
        if char == ')':
            depth -= 1
            if depth == 0 and current:
                sexprs.append(''.join(current))
    
    return sexprs


def is_rule_format(expr) -> bool:
    """Check if expression is a complete rule [pattern, skeleton] or rich rule dict."""
    # Rich rule dict format
    if isinstance(expr, dict) and 'pattern' in expr and 'skeleton' in expr:
        return True

    # Simple [pattern, skeleton] format
    return (isinstance(expr, list) and
            len(expr) == 2 and
            isinstance(expr[0], (list, str, int, float)) and
            isinstance(expr[1], (list, str, int, float)))


def save_rules(rules: List[RuleType], filepath: Union[str, Path], 
               format: str = None) -> None:
    """
    Save rules to a file.
    
    Args:
        rules: List of rules to save
        filepath: Output path
        format: 'json' or 'lisp' (auto-detected from extension if None)
    """
    filepath = Path(filepath)
    
    if format is None:
        format = 'lisp' if filepath.suffix in ['.lisp', '.lsp', '.sexpr'] else 'json'
    
    with open(filepath, 'w') as f:
        if format == 'json':
            json.dump(rules, f, indent=2)
        else:
            f.write(format_rules_as_lisp(rules))


def format_rules_as_lisp(rules: List[RuleType]) -> str:
    """Format rules as readable Lisp expressions."""
    lines = [";;;; Rules for xtk\n"]
    
    for pattern, skeleton in rules:
        # Format as single rule for compactness
        rule_str = format_sexpr([pattern, skeleton])
        lines.append(rule_str)
    
    return '\n'.join(lines)


# Convenience functions
def merge_rules(*rule_sets) -> List[RuleType]:
    """Merge multiple rule sets, removing duplicates."""
    seen = set()
    merged = []
    
    for rules in rule_sets:
        for rule in rules:
            # Use string representation for comparison
            key = (str(rule[0]), str(rule[1]))
            if key not in seen:
                seen.add(key)
                merged.append(rule)
    
    return merged