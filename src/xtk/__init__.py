"""
xtk - Expression Toolkit

A rules-based expression rewriting toolkit for symbolic computation.
"""

__version__ = "0.2.3"

# Core rewriter functions
from .rewriter import (
    match,
    instantiate,
    evaluate,
    rewriter,
    empty_dictionary,
    extend_dictionary,
    lookup,
    # Type aliases
    ExprType,
    DictType,
    RuleType,
)

# Backwards compatibility alias
simplifier = rewriter

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

# Rule DSL (clean syntax for defining rules)
from .rule_dsl import (
    rule,
    rules as dsl_rules,  # Renamed to avoid conflict with xtk.rules subpackage
    parse_dsl as parse_rule_dsl,
    format_dsl_rule,
    format_dsl_expr,
    load_dsl_rules,
    ParsedRule,
)

# Rule utilities and explanations
from .rule_utils import (
    RichRule,
    normalize_rules,
    get_rule_metadata,
)

from .explainer import (
    RewriteExplainer,
    LLMProvider,
    AnthropicProvider,
    OpenAIProvider,
    OllamaProvider,
)

# LLM Rule Inference
from .llm_inferrer import (
    LLMRuleInferrer,
    InferredRule,
    create_inferrer,
)

# CLI and REPL
from .cli import (
    XTKRepl,
    main as cli_main,
)

# Commonly used rules
from .rules.deriv_rules import deriv_rules_fixed
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
    "rewriter",
    "simplifier",  # Backwards compatibility
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

    # Rule DSL
    "rule",
    "dsl_rules",
    "parse_rule_dsl",
    "format_dsl_rule",
    "format_dsl_expr",
    "load_dsl_rules",
    "ParsedRule",

    # Rule utilities and explanations
    "RichRule",
    "normalize_rules",
    "get_rule_metadata",
    "RewriteExplainer",
    "LLMProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "OllamaProvider",

    # LLM Rule Inference
    "LLMRuleInferrer",
    "InferredRule",
    "create_inferrer",

    # CLI
    "XTKRepl",
    "cli_main",

    # Rules
    "deriv_rules_fixed",
    "simplify_rules",
    "expand_rules",
    "factor_rules",
]