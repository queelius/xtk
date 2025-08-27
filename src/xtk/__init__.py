"""
xtk - Expression Toolkit

A rules-based expression rewriting toolkit for symbolic computation.
"""

__version__ = "0.1.0"

# Core rewriter functions
from .rewriter_improved import (
    match,
    instantiate,
    evaluate,
    simplifier,
    empty_dictionary,
    extend_dictionary,
    lookup,
    # Type aliases
    ExprType,
    DictType,
    RuleType,
)

# Fluent API
from .fluent_api import (
    Expression,
    ExpressionBuilder,
    E,  # Shorthand for ExpressionBuilder
    expr,  # Shorthand for Expression constructor
)

# Parser functions
from .parser import (
    parse_sexpr,
    format_sexpr,
    parse_dsl,
    dsl_parser,
    ParseError,
)

# CLI and REPL
from .cli import (
    XTKRepl,
    main as cli_main,
)

# Commonly used rules
from .rules.deriv_rules_fixed import deriv_rules_fixed
from .rules.algebra_rules import (
    simplify_rules,
    expand_rules,
    factor_rules,
)

__all__ = [
    # Core functions
    "match",
    "instantiate",
    "evaluate",
    "simplifier",
    "empty_dictionary",
    "extend_dictionary",
    "lookup",
    
    # Types
    "ExprType",
    "DictType",
    "RuleType",
    
    # Fluent API
    "Expression",
    "ExpressionBuilder",
    "E",
    "expr",
    
    # Parser
    "parse_sexpr",
    "format_sexpr",
    "parse_dsl",
    "dsl_parser",
    "ParseError",
    
    # CLI
    "XTKRepl",
    "cli_main",
    
    # Rules
    "deriv_rules_fixed",
    "simplify_rules",
    "expand_rules",
    "factor_rules",
]