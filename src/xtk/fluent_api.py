"""
Fluent API for xtk - Expressive and simple interface for symbolic computation.
"""

from typing import Any, List, Union, Optional, Callable, Dict
from copy import deepcopy
import logging

from .rewriter import (
    rewriter, match, instantiate, evaluate,
    empty_dictionary, ExprType, DictType, RuleType
)

logger = logging.getLogger(__name__)


class Expression:
    """Fluent interface for working with expressions."""
    
    def __init__(self, expr: ExprType):
        """
        Initialize an Expression.
        
        Args:
            expr: The expression (list, string, or number)
        """
        self.expr = expr
        self._rules = []
        self._bindings = empty_dictionary()
        self._history = []
    
    def __repr__(self):
        return f"Expression({self.expr})"
    
    def __str__(self):
        return self.to_string()
    
    def __eq__(self, other):
        if isinstance(other, Expression):
            return self.expr == other.expr
        return self.expr == other
    
    def to_string(self) -> str:
        """Convert expression to human-readable string."""
        def stringify(e):
            if isinstance(e, list):
                if not e:
                    return "()"
                return f"({' '.join(stringify(x) for x in e)})"
            return str(e)
        return stringify(self.expr)
    
    def to_latex(self) -> str:
        """Convert expression to LaTeX format."""
        def latexify(e):
            if isinstance(e, (int, float)):
                return str(e)
            elif isinstance(e, str):
                return e
            elif isinstance(e, list) and e:
                op = e[0]
                if op == '+':
                    return ' + '.join(latexify(arg) for arg in e[1:])
                elif op == '-':
                    if len(e) == 2:
                        return f"-{latexify(e[1])}"
                    return f"{latexify(e[1])} - {latexify(e[2])}"
                elif op == '*':
                    return ' \\cdot '.join(latexify(arg) for arg in e[1:])
                elif op == '/':
                    return f"\\frac{{{latexify(e[1])}}}{{{latexify(e[2])}}}"
                elif op == '^':
                    return f"{{{latexify(e[1])}}}^{{{latexify(e[2])}}}"
                elif op == 'sin':
                    return f"\\sin({latexify(e[1])})"
                elif op == 'cos':
                    return f"\\cos({latexify(e[1])})"
                elif op == 'dd':
                    return f"\\frac{{d}}{{d{latexify(e[2])}}}({latexify(e[1])})"
                else:
                    return f"{op}({', '.join(latexify(arg) for arg in e[1:])})"
            return str(e)
        
        return latexify(self.expr)
    
    def copy(self) -> 'Expression':
        """Create a deep copy of this expression."""
        new_expr = Expression(deepcopy(self.expr))
        new_expr._rules = deepcopy(self._rules)
        new_expr._bindings = deepcopy(self._bindings)
        new_expr._history = deepcopy(self._history)
        return new_expr
    
    def with_rules(self, rules: List[RuleType]) -> 'Expression':
        """
        Add transformation rules.
        
        Args:
            rules: List of [pattern, skeleton] rules
            
        Returns:
            Self for chaining
        """
        self._rules.extend(rules)
        return self
    
    def with_rule(self, pattern: ExprType, skeleton: ExprType) -> 'Expression':
        """
        Add a single transformation rule.
        
        Args:
            pattern: The pattern to match
            skeleton: The replacement skeleton
            
        Returns:
            Self for chaining
        """
        self._rules.append([pattern, skeleton])
        return self
    
    def bind(self, name: str, value: Any) -> 'Expression':
        """
        Add a binding for evaluation.
        
        Args:
            name: Variable or function name
            value: Value or callable
            
        Returns:
            Self for chaining
        """
        self._bindings.append([name, value])
        return self
    
    def simplify(self, max_steps: Optional[int] = None, constant_folding: bool = True) -> 'Expression':
        """
        Simplify the expression using current rules.

        Even without rules, constant folding will evaluate arithmetic
        on numeric constants (e.g., (+ 2 3) → 5) when enabled.

        Args:
            max_steps: Maximum simplification steps
            constant_folding: Enable constant folding (default: True)

        Returns:
            New Expression with simplified result
        """
        # Always call rewriter - it handles constant folding even without rules
        rewrite_fn = rewriter(self._rules if self._rules else [], constant_folding=constant_folding)
        result = rewrite_fn(self.expr)

        new_expr = Expression(result)
        new_expr._rules = deepcopy(self._rules)
        new_expr._bindings = deepcopy(self._bindings)
        new_expr._history = self._history + [self.expr]
        return new_expr
    
    def evaluate(self, bindings: Optional[DictType] = None) -> 'Expression':
        """
        Evaluate the expression with bindings.
        
        Args:
            bindings: Optional bindings dictionary
            
        Returns:
            New Expression with evaluated result
        """
        bindings = bindings or self._bindings
        result = evaluate(self.expr, bindings)
        
        new_expr = Expression(result)
        new_expr._rules = deepcopy(self._rules)
        new_expr._bindings = deepcopy(bindings)
        new_expr._history = self._history + [self.expr]
        return new_expr
    
    def match_pattern(self, pattern: ExprType) -> Optional[DictType]:
        """
        Match expression against a pattern.
        
        Args:
            pattern: The pattern to match against
            
        Returns:
            Bindings dictionary or None if no match
        """
        result = match(pattern, self.expr, empty_dictionary())
        return result if result != "failed" else None
    
    def transform(self, pattern: ExprType, skeleton: ExprType) -> 'Expression':
        """
        Transform expression if pattern matches.
        
        Args:
            pattern: Pattern to match
            skeleton: Replacement skeleton
            
        Returns:
            Transformed expression or self if no match
        """
        bindings = self.match_pattern(pattern)
        if bindings:
            result = instantiate(skeleton, bindings)
            new_expr = Expression(result)
            new_expr._rules = deepcopy(self._rules)
            new_expr._bindings = deepcopy(self._bindings)
            new_expr._history = self._history + [self.expr]
            return new_expr
        return self
    
    def differentiate(self, var: str) -> 'Expression':
        """
        Differentiate expression with respect to a variable.
        
        Args:
            var: Variable to differentiate with respect to
            
        Returns:
            New Expression representing the derivative
        """
        from .rules.deriv_rules import deriv_rules_fixed
        
        deriv_expr = ['dd', self.expr, var]
        new_expr = Expression(deriv_expr)
        new_expr._rules = deriv_rules_fixed
        new_expr._bindings = deepcopy(self._bindings)
        return new_expr.simplify()
    
    def substitute(self, var: str, value: ExprType) -> 'Expression':
        """
        Substitute a variable with a value.
        
        Args:
            var: Variable to substitute
            value: Value to substitute with
            
        Returns:
            New Expression with substitution applied
        """
        def subst(expr):
            if expr == var:
                return value
            elif isinstance(expr, list):
                return [subst(e) for e in expr]
            return expr
        
        result = subst(self.expr)
        new_expr = Expression(result)
        new_expr._rules = deepcopy(self._rules)
        new_expr._bindings = deepcopy(self._bindings)
        new_expr._history = self._history + [self.expr]
        return new_expr
    
    def expand(self) -> 'Expression':
        """Expand the expression algebraically."""
        from .rules.algebra_rules import expand_rules
        return self.copy().with_rules(expand_rules).simplify()
    
    def factor(self) -> 'Expression':
        """Factor the expression algebraically."""
        from .rules.algebra_rules import factor_rules
        return self.copy().with_rules(factor_rules).simplify()
    
    def get_history(self) -> List[ExprType]:
        """Get transformation history."""
        return self._history + [self.expr]


class ExpressionBuilder:
    """Builder for creating expressions fluently."""
    
    @staticmethod
    def constant(value: Union[int, float]) -> Expression:
        """Create a constant expression."""
        return Expression(value)
    
    @staticmethod
    def variable(name: str) -> Expression:
        """Create a variable expression."""
        return Expression(name)
    
    @staticmethod
    def add(*args) -> Expression:
        """Create an addition expression."""
        return Expression(['+'] + list(args))
    
    @staticmethod
    def subtract(a, b) -> Expression:
        """Create a subtraction expression."""
        return Expression(['-', a, b])
    
    @staticmethod
    def multiply(*args) -> Expression:
        """Create a multiplication expression."""
        return Expression(['*'] + list(args))
    
    @staticmethod
    def divide(a, b) -> Expression:
        """Create a division expression."""
        return Expression(['/', a, b])
    
    @staticmethod
    def power(base, exp) -> Expression:
        """Create a power expression."""
        return Expression(['^', base, exp])
    
    @staticmethod
    def sin(x) -> Expression:
        """Create a sine expression."""
        return Expression(['sin', x])
    
    @staticmethod
    def cos(x) -> Expression:
        """Create a cosine expression."""
        return Expression(['cos', x])
    
    @staticmethod
    def exp(x) -> Expression:
        """Create an exponential expression."""
        return Expression(['exp', x])
    
    @staticmethod
    def log(x) -> Expression:
        """Create a logarithm expression."""
        return Expression(['log', x])
    
    @staticmethod
    def derivative(f, x) -> Expression:
        """Create a derivative expression."""
        return Expression(['dd', f, x])
    
    @staticmethod
    def from_string(s: str) -> Expression:
        """Parse an expression from S-expression string."""
        from .parser import parse_sexpr
        return Expression(parse_sexpr(s))


# Convenience shortcuts
E = ExpressionBuilder
expr = Expression