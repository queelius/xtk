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

# Rule loading
from .rule_loader import (
    load_rules,
    save_rules,
    parse_rules,
    merge_rules,
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
    
    # Rule loading
    "load_rules",
    "save_rules",
    "parse_rules",
    "merge_rules",
    
    # CLI
    "XTKRepl",
    "cli_main",
    
    # Rules
    "deriv_rules_fixed",
    "simplify_rules",
    "expand_rules",
    "factor_rules",
]