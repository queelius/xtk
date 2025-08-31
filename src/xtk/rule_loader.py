"""
Elegant rule loading for xtk.

Leverages the existing S-expression parser for all formats.
"""

import json
import re
from pathlib import Path
from typing import List, Union

from .parser import parse_sexpr, format_sexpr
from .rewriter_improved import RuleType


def load_rules(source: Union[str, Path, List]) -> List[RuleType]:
    """
    Load rules from various sources.
    
    Args:
        source: Can be a filepath (.json, .lisp), a list of rules, 
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
            with open(path, 'r') as f:
                content = f.read()
        else:
            # Treat as inline rule string
            content = str(source)
        
        return parse_rules(content)
    
    raise ValueError(f"Cannot load rules from {type(source)}")


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
    """Check if expression is a complete rule [pattern, skeleton]."""
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