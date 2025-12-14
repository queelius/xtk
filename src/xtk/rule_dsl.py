"""
Clean DSL for defining rewrite rules.

Syntax:
    ; Comments start with semicolon

    ; Basic rule: pattern => skeleton
    (+ ?x 0) => :x

    ; Named rule (optional)
    @identity-add: (+ ?x 0) => :x

    ; Typed matches (optional)
    ?c:const   - matches constants only (numbers)
    ?v:var     - matches variables only (symbols)
    ?x         - matches anything (shorthand for ?x:any)

    ; Multiple rules
    (+ ?x 0) => :x
    (* ?x 1) => :x
    (* ?x 0) => 0

Examples:
    ; Derivative of constant
    @deriv-const: (dd ?c:const ?v:var) => 0

    ; Sum rule
    @sum-rule: (dd (+ ?f ?g) ?v:var) => (+ (dd :f :v) (dd :g :v))
"""

import re
from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass

from .parser import parse_sexpr, format_sexpr


@dataclass
class ParsedRule:
    """A parsed rule with optional metadata."""
    pattern: Any
    skeleton: Any
    name: Optional[str] = None
    description: Optional[str] = None

    def to_pair(self) -> List:
        """Convert to [pattern, skeleton] format."""
        return [self.pattern, self.skeleton]

    def to_rich(self) -> Dict:
        """Convert to rich rule dict format."""
        return {
            'pattern': self.pattern,
            'skeleton': self.skeleton,
            'name': self.name,
            'description': self.description
        }


def parse_dsl(text: str) -> List[ParsedRule]:
    """
    Parse rules from DSL text.

    Args:
        text: DSL text with rules

    Returns:
        List of ParsedRule objects
    """
    rules = []

    # Remove block comments /* ... */
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

    # Process line by line
    lines = text.split('\n')
    current_comment = None

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            current_comment = None
            continue

        # Line comments (can be used as descriptions)
        if line.startswith(';') or line.startswith('//') or line.startswith('#'):
            # Extract comment text (potential description for next rule)
            comment = line.lstrip(';/#').strip()
            if comment:
                current_comment = comment
            continue

        # Parse rule line
        rule = parse_rule_line(line, current_comment)
        if rule:
            rules.append(rule)
            current_comment = None

    return rules


def parse_rule_line(line: str, description: Optional[str] = None) -> Optional[ParsedRule]:
    """
    Parse a single rule line.

    Formats:
        (+ ?x 0) => :x
        @name: (+ ?x 0) => :x
    """
    name = None

    # Check for named rule: @name: ...
    if line.startswith('@'):
        match = re.match(r'@([\w-]+):\s*(.+)', line)
        if match:
            name = match.group(1)
            line = match.group(2)
        else:
            return None

    # Split on =>
    if '=>' not in line:
        return None

    parts = line.split('=>', 1)
    if len(parts) != 2:
        return None

    pattern_str = parts[0].strip()
    skeleton_str = parts[1].strip()

    # Parse pattern and skeleton
    try:
        pattern = parse_dsl_expr(pattern_str)
        skeleton = parse_dsl_expr(skeleton_str)
    except Exception:
        return None

    return ParsedRule(
        pattern=pattern,
        skeleton=skeleton,
        name=name,
        description=description
    )


def parse_dsl_expr(text: str) -> Any:
    """
    Parse a DSL expression, converting friendly syntax to internal format.

    Conversions:
        ?x      -> ["?", "x"]
        ?c:const -> ["?c", "c"]
        ?v:var  -> ["?v", "v"]
        :x      -> [":", "x"]
    """
    # First, convert DSL syntax to S-expression syntax
    converted = convert_dsl_to_sexpr(text)

    # Then parse as S-expression
    return parse_sexpr(converted)


def convert_dsl_to_sexpr(text: str) -> str:
    """
    Convert DSL syntax to standard S-expression syntax.

    ?x       -> (? x)
    ?c:const -> (?c c)
    ?v:var   -> (?v v)
    :x       -> (: x)
    """
    result = text

    # Handle typed matches FIRST: ?name:type -> (?type name)
    # ?c:const -> (?c c), ?v:var -> (?v v), ?x:any -> (? x)
    def replace_typed_match(m):
        name = m.group(1)
        type_hint = m.group(2)
        if type_hint == 'const':
            return f'(?c {name})'
        elif type_hint == 'var':
            return f'(?v {name})'
        elif type_hint == 'any':
            return f'(? {name})'
        else:
            # Unknown type, treat as any
            return f'(? {name})'

    result = re.sub(r'\?(\w+):(\w+)', replace_typed_match, result)

    # Handle simple matches: ?x -> (? x)
    # Match ?word but NOT if preceded by ( (which means already converted)
    result = re.sub(r'(?<!\()\?(\w+)', r'(? \1)', result)

    # Handle skeleton substitution: :x -> (: x)
    # But not if already inside parentheses
    result = re.sub(r'(?<!\():(\w+)', r'(: \1)', result)

    return result


def format_dsl_rule(rule: Union[ParsedRule, List, Tuple]) -> str:
    """
    Format a rule in DSL syntax.

    Args:
        rule: ParsedRule, [pattern, skeleton], or (pattern, skeleton)

    Returns:
        DSL string like "(+ ?x 0) => :x"
    """
    if isinstance(rule, ParsedRule):
        pattern = rule.pattern
        skeleton = rule.skeleton
        name = rule.name
    else:
        pattern, skeleton = rule[0], rule[1]
        name = None

    pattern_str = format_dsl_expr(pattern)
    skeleton_str = format_dsl_expr(skeleton)

    if name:
        return f"@{name}: {pattern_str} => {skeleton_str}"
    else:
        return f"{pattern_str} => {skeleton_str}"


def format_dsl_expr(expr: Any) -> str:
    """
    Format an expression in DSL syntax.

    Conversions:
        ["?", "x"]  -> ?x
        ["?c", "c"] -> ?c:const
        ["?v", "v"] -> ?v:var
        [":", "x"]  -> :x
    """
    if not isinstance(expr, list):
        return str(expr)

    if len(expr) == 0:
        return "()"

    # Special forms
    if len(expr) == 2:
        op, arg = expr
        if op == "?":
            return f"?{arg}"
        elif op == "?c":
            return f"?{arg}:const"
        elif op == "?v":
            return f"?{arg}:var"
        elif op == ":":
            return f":{arg}"

    # Regular compound expression
    formatted_parts = [format_dsl_expr(part) for part in expr]
    return "(" + " ".join(formatted_parts) + ")"


def load_dsl_rules(source: str) -> List[List]:
    """
    Load rules from DSL source and return as [pattern, skeleton] pairs.

    Args:
        source: DSL text or file path

    Returns:
        List of [pattern, skeleton] rule pairs
    """
    from pathlib import Path

    # Check if source is a file path
    path = Path(source)
    if path.exists() and path.suffix in ['.rules', '.dsl', '.xtk']:
        with open(path, 'r') as f:
            text = f.read()
    else:
        text = source

    parsed = parse_dsl(text)
    return [rule.to_pair() for rule in parsed]


def load_dsl_rules_rich(source: str) -> List[Dict]:
    """
    Load rules from DSL source and return as rich rule dicts.

    Args:
        source: DSL text or file path

    Returns:
        List of rich rule dicts with pattern, skeleton, name, description
    """
    from pathlib import Path

    path = Path(source)
    if path.exists() and path.suffix in ['.rules', '.dsl', '.xtk']:
        with open(path, 'r') as f:
            text = f.read()
    else:
        text = source

    parsed = parse_dsl(text)
    return [rule.to_rich() for rule in parsed]


# Convenience function for inline rule definition
def rule(text: str) -> List:
    """
    Parse a single rule from DSL text.

    Example:
        r = rule("(+ ?x 0) => :x")
        # Returns: [['+', ['?', 'x'], 0], [':', 'x']]
    """
    parsed = parse_rule_line(text.strip())
    if parsed:
        return parsed.to_pair()
    raise ValueError(f"Invalid rule syntax: {text}")


def rules(text: str) -> List[List]:
    """
    Parse multiple rules from DSL text.

    Example:
        rs = rules('''
            (+ ?x 0) => :x
            (* ?x 1) => :x
        ''')
    """
    return load_dsl_rules(text)
