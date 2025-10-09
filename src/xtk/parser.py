"""
S-expression parser for Lisp-like DSL.

Supports both traditional S-expressions and a more readable format.
"""

import re
from typing import Any, List, Union

ExprType = Union[int, float, str, List]


class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass


def tokenize(s: str) -> List[str]:
    """
    Tokenize an S-expression string.
    
    Args:
        s: String to tokenize
        
    Returns:
        List of tokens
    """
    # Add spaces around parentheses
    s = s.replace('(', ' ( ').replace(')', ' ) ')
    # Split on whitespace
    tokens = s.split()
    return tokens


def parse_sexpr(s: str) -> ExprType:
    """
    Parse an S-expression string into nested lists.
    
    Args:
        s: S-expression string
        
    Returns:
        Parsed expression as nested lists
        
    Examples:
        >>> parse_sexpr("(+ 1 2)")
        ['+', 1, 2]
        >>> parse_sexpr("(* (+ x 1) y)")
        ['*', ['+', 'x', 1], 'y']
    """
    tokens = tokenize(s)
    if not tokens:
        raise ParseError("Empty expression")
    
    def parse_tokens(tokens: List[str], index: int = 0) -> tuple:
        """Parse tokens starting at index."""
        if index >= len(tokens):
            raise ParseError("Unexpected end of expression")
        
        token = tokens[index]
        
        if token == '(':
            # Parse a list
            result = []
            index += 1
            while index < len(tokens) and tokens[index] != ')':
                item, index = parse_tokens(tokens, index)
                result.append(item)
            
            if index >= len(tokens):
                raise ParseError("Missing closing parenthesis")
            
            return result, index + 1
        
        elif token == ')':
            raise ParseError("Unexpected closing parenthesis")
        
        else:
            # Parse an atom
            return parse_atom(token), index + 1
    
    expr, final_index = parse_tokens(tokens, 0)
    
    if final_index < len(tokens):
        raise ParseError(f"Extra tokens after expression: {tokens[final_index:]}")
    
    return expr


def parse_atom(token: str) -> Union[int, float, str]:
    """
    Parse an atomic token.
    
    Args:
        token: Token string
        
    Returns:
        Parsed value (int, float, or string)
    """
    # Try to parse as integer
    try:
        return int(token)
    except ValueError:
        pass
    
    # Try to parse as float
    try:
        return float(token)
    except ValueError:
        pass
    
    # Return as string (variable or operator)
    return token


def format_sexpr(expr: ExprType, indent: int = 0) -> str:
    """
    Format an expression as an S-expression string.
    
    Args:
        expr: Expression to format
        indent: Current indentation level
        
    Returns:
        Formatted S-expression string
    """
    if isinstance(expr, list):
        if not expr:
            return "()"
        
        if len(expr) <= 3 and not any(isinstance(e, list) for e in expr):
            # Short expressions on one line
            return f"({' '.join(format_sexpr(e) for e in expr)})"
        else:
            # Longer expressions with indentation
            lines = []
            lines.append("(")
            for i, item in enumerate(expr):
                item_str = format_sexpr(item, indent + 2)
                if i == 0:
                    lines[-1] += item_str
                else:
                    lines.append("  " * (indent + 1) + item_str)
            lines.append("  " * indent + ")")
            return '\n'.join(lines) if len(lines) > 2 else ''.join(lines)
    else:
        return str(expr)


def parse_dsl(s: str) -> ExprType:
    """
    Parse the human-readable DSL format.
    
    This supports a more natural syntax like:
        "x + 2*y"
        "sin(x) + cos(y)"
        "d/dx (x^2 + 3*x)"
    
    Args:
        s: DSL string
        
    Returns:
        Parsed expression
    """
    # This is a simplified parser - a full implementation would need
    # proper precedence handling and more operators
    
    s = s.strip()
    
    # Handle derivatives
    if s.startswith("d/d"):
        match = re.match(r'd/d(\w+)\s*\((.*)\)', s)
        if match:
            var = match.group(1)
            expr_str = match.group(2)
            return ['dd', parse_dsl(expr_str), var]
    
    # Handle function calls
    for func in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']:
        if s.startswith(func + '('):
            match = re.match(f'{func}\\((.*)\\)', s)
            if match:
                arg = match.group(1)
                return [func, parse_dsl(arg)]
    
    # Handle binary operators (simplified - no precedence)
    # This is a very basic implementation
    for op, symbol in [('+', '+'), ('-', '-'), ('*', '*'), ('/', '/'), ('^', '^')]:
        if symbol in s:
            parts = s.split(symbol, 1)
            if len(parts) == 2:
                left = parse_dsl(parts[0].strip())
                right = parse_dsl(parts[1].strip())
                return [op, left, right]
    
    # Handle parentheses
    if s.startswith('(') and s.endswith(')'):
        return parse_dsl(s[1:-1])
    
    # Handle atoms
    return parse_atom(s)


class DSLParser:
    """
    Advanced DSL parser with proper precedence and associativity.
    """
    
    def __init__(self):
        self.precedence = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '^': 3,
        }
        self.right_assoc = {'^'}
    
    def parse(self, s: str) -> ExprType:
        """
        Parse a DSL expression with proper precedence.
        
        Args:
            s: Expression string
            
        Returns:
            Parsed expression
        """
        tokens = self._tokenize_infix(s)
        return self._parse_expr(tokens, 0)[0]
    
    def _tokenize_infix(self, s: str) -> List[str]:
        """Tokenize an infix expression."""
        # Add spaces around operators and parentheses
        for op in ['+', '-', '*', '/', '^', '(', ')', ',']:
            s = s.replace(op, f' {op} ')

        # Handle special cases like sin(x)
        s = re.sub(r'(\w+)\s+\(', r'\1(', s)

        tokens = []
        current = ''
        i = 0
        while i < len(s):
            c = s[i]
            if c.isspace():
                if current:
                    tokens.append(current)
                    current = ''
            elif c in '()+-*/^,':
                if current:
                    tokens.append(current)
                    current = ''
                tokens.append(c)
            else:
                current += c
            i += 1

        if current:
            tokens.append(current)

        return tokens
    
    def _parse_expr(self, tokens: List[str], pos: int, min_prec: int = 0) -> tuple:
        """Parse expression with precedence climbing."""
        left, pos = self._parse_primary(tokens, pos)
        
        while pos < len(tokens):
            op = tokens[pos]
            if op not in self.precedence:
                break
            
            prec = self.precedence[op]
            if prec < min_prec:
                break
            
            pos += 1
            assoc = 'right' if op in self.right_assoc else 'left'
            next_min_prec = prec + 1 if assoc == 'left' else prec
            
            right, pos = self._parse_expr(tokens, pos, next_min_prec)
            left = [op, left, right]
        
        return left, pos
    
    def _parse_primary(self, tokens: List[str], pos: int) -> tuple:
        """Parse primary expression (atom, function call, or parenthesized)."""
        if pos >= len(tokens):
            raise ParseError("Unexpected end of expression")
        
        token = tokens[pos]
        
        # Handle parentheses
        if token == '(':
            pos += 1
            expr, pos = self._parse_expr(tokens, pos)
            if pos >= len(tokens) or tokens[pos] != ')':
                raise ParseError("Missing closing parenthesis")
            return expr, pos + 1
        
        # Handle function calls
        if pos + 1 < len(tokens) and tokens[pos + 1] == '(':
            func_name = token
            pos += 2  # Skip function name and opening paren
            
            # Parse function arguments
            args = []
            while pos < len(tokens) and tokens[pos] != ')':
                arg, pos = self._parse_expr(tokens, pos)
                args.append(arg)
                
                if pos < len(tokens) and tokens[pos] == ',':
                    pos += 1  # Skip comma
            
            if pos >= len(tokens):
                raise ParseError("Missing closing parenthesis in function call")
            
            return [func_name] + args, pos + 1
        
        # Handle atoms
        return parse_atom(token), pos + 1


# Global parser instance
dsl_parser = DSLParser()