"""
LLM-powered rewrite agent for xtk.

The outer loop agent that wraps the rewriter and can:
- Infer missing rules via LLMRuleInferrer
- Correct typos in operator names
- Explain parse errors
- Break infinite loops

This is more powerful than the inner LLMRuleInferrer because
it can iterate and handle multiple error types.
"""

import logging
from typing import List, Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass, field
from difflib import get_close_matches

from .rewriter import match, instantiate, evaluate
from .llm_inferrer import LLMRuleInferrer, InferredRule
from .parser import format_sexpr
from .rule_dsl import format_dsl_rule, format_dsl_expr

logger = logging.getLogger(__name__)


@dataclass
class RewriteResult:
    """Result of a rewrite operation."""
    success: bool
    expression: Any  # The (possibly rewritten) expression
    rules_applied: List[str] = field(default_factory=list)
    steps: int = 0
    message: str = ""


@dataclass
class RewriteError:
    """Structured error from rewriter."""
    error_type: str  # 'no_match', 'unknown_op', 'infinite_loop', 'parse_error'
    expression: Any
    context: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    suggestions: List[str] = field(default_factory=list)


@dataclass
class AgentAction:
    """An action the agent decided to take."""
    action_type: str  # 'infer_rule', 'correct_typo', 'explain', 'give_up'
    details: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class LLMRewriteAgent:
    """
    Outer loop agent that wraps the rewriter with LLM capabilities.

    This agent can:
    1. Infer missing rules when no rule matches
    2. Suggest corrections for typos in operator names
    3. Explain errors and suggest fixes
    4. Break infinite loops

    Example usage:
        from xtk import rewriter
        from xtk.llm_agent import LLMRewriteAgent
        from xtk.explainer import OllamaProvider

        agent = LLMRewriteAgent(
            provider=OllamaProvider(model="phi4-mini:latest"),
            known_operators=['sin', 'cos', 'tan', '+', '-', '*', '/', '^']
        )

        # Rewrite with agent assistance
        result = agent.rewrite(expr, rules)

        # If there were errors, check what the agent did
        for action in agent.actions_taken:
            print(f"{action.action_type}: {action.message}")
    """
    provider: Any = None  # LLMProvider instance
    enabled: bool = True
    max_iterations: int = 5

    # Features to enable
    infer_missing_rules: bool = True
    correct_typos: bool = True
    explain_errors: bool = True

    # Known operators for typo detection
    known_operators: List[str] = field(default_factory=list)

    # Callbacks
    on_action: Optional[Callable[[AgentAction], None]] = None
    on_error: Optional[Callable[[RewriteError], None]] = None

    # Internal state
    rule_inferrer: LLMRuleInferrer = field(init=False)
    actions_taken: List[AgentAction] = field(default_factory=list, init=False)
    inferred_rules: List[List] = field(default_factory=list, init=False)

    def __post_init__(self):
        """Initialize the inner rule inferrer."""
        self.rule_inferrer = LLMRuleInferrer(
            provider=self.provider,
            enabled=self.infer_missing_rules and self.provider is not None
        )
        if not self.known_operators:
            # Default mathematical operators
            self.known_operators = [
                '+', '-', '*', '/', '^',
                'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
                'asin', 'acos', 'atan',
                'sinh', 'cosh', 'tanh',
                'exp', 'log', 'ln', 'sqrt',
                'dd', 'int',  # derivative and integral
                'abs', 'floor', 'ceil', 'round',
            ]

    def rewrite(
        self,
        expr: Any,
        rules: List[List],
        rewriter_func: Optional[Callable] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RewriteResult:
        """
        Rewrite expression with agent assistance.

        Args:
            expr: The expression to rewrite
            rules: List of [pattern, skeleton] rules
            rewriter_func: Optional custom rewriter function
            context: Optional context for LLM (domain hints, etc.)

        Returns:
            RewriteResult with the final expression and metadata
        """
        self.actions_taken = []
        current_expr = expr
        iteration = 0
        rules_used = list(rules)  # Copy to avoid mutating original

        while iteration < self.max_iterations:
            iteration += 1

            # Try to rewrite
            result, error = self._try_rewrite(current_expr, rules_used, rewriter_func)

            if result is not None:
                # Success - check if we're done
                if result == current_expr:
                    # No more rewrites possible
                    return RewriteResult(
                        success=True,
                        expression=result,
                        rules_applied=[r[0] if isinstance(r, list) and len(r) > 0 else str(r)
                                       for r in self.inferred_rules],
                        steps=iteration,
                        message="Rewrite complete"
                    )
                current_expr = result
                continue

            # Error occurred - handle it
            if error:
                if self.on_error:
                    self.on_error(error)

                action = self._handle_error(error, current_expr, rules_used, context)

                if action:
                    self.actions_taken.append(action)
                    if self.on_action:
                        self.on_action(action)

                    if action.action_type == 'infer_rule':
                        # Add the inferred rule and retry
                        new_rule = action.details.get('rule')
                        if new_rule:
                            rules_used.append(new_rule)
                            self.inferred_rules.append(new_rule)
                        continue

                    elif action.action_type == 'correct_typo':
                        # Update expression with correction and retry
                        corrected = action.details.get('corrected_expr')
                        if corrected:
                            current_expr = corrected
                        continue

                    elif action.action_type == 'give_up':
                        break

            # No action taken, break
            break

        return RewriteResult(
            success=False,
            expression=current_expr,
            rules_applied=[str(r) for r in self.inferred_rules],
            steps=iteration,
            message="Max iterations reached or no fix found"
        )

    def _try_rewrite(
        self,
        expr: Any,
        rules: List[List],
        rewriter_func: Optional[Callable]
    ) -> Tuple[Optional[Any], Optional[RewriteError]]:
        """
        Try to rewrite expression, returning result or structured error.
        """
        # Check for unknown operators first
        unknown = self._find_unknown_operators(expr)
        if unknown:
            suggestions = []
            for op in unknown:
                close = get_close_matches(op, self.known_operators, n=1, cutoff=0.6)
                if close:
                    suggestions.append(f"'{op}' -> '{close[0]}'?")

            return None, RewriteError(
                error_type='unknown_op',
                expression=expr,
                context={'unknown_operators': unknown},
                message=f"Unknown operator(s): {', '.join(unknown)}",
                suggestions=suggestions
            )

        # Try the actual rewrite
        try:
            if rewriter_func:
                result = rewriter_func(expr)
            else:
                result = self._simple_rewrite(expr, rules)

            return result, None

        except RecursionError:
            return None, RewriteError(
                error_type='infinite_loop',
                expression=expr,
                message="Infinite loop detected during rewrite"
            )
        except Exception as e:
            return None, RewriteError(
                error_type='rewrite_error',
                expression=expr,
                context={'exception': str(e)},
                message=f"Rewrite error: {e}"
            )

    def _simple_rewrite(self, expr: Any, rules: List[List]) -> Any:
        """Simple one-step rewrite attempt."""
        if not isinstance(expr, list) or not expr:
            return expr

        # Try each rule
        for rule in rules:
            if len(rule) != 2:
                continue
            pattern, skeleton = rule
            bindings = match(pattern, expr, [])
            if bindings != "failed":
                return instantiate(skeleton, bindings)

        # No rule matched - recursively try subexpressions
        new_expr = [expr[0]]  # Keep operator
        changed = False
        for sub in expr[1:]:
            new_sub = self._simple_rewrite(sub, rules)
            if new_sub != sub:
                changed = True
            new_expr.append(new_sub)

        return new_expr if changed else expr

    def _find_unknown_operators(self, expr: Any) -> List[str]:
        """Find operators in expression that are not in known_operators."""
        unknown = []

        def traverse(e):
            if isinstance(e, list) and e:
                op = e[0]
                if isinstance(op, str) and op not in self.known_operators:
                    # Skip pattern matching operators
                    if op not in ('?', '?c', '?v', ':'):
                        unknown.append(op)
                for sub in e[1:]:
                    traverse(sub)

        traverse(expr)
        return list(set(unknown))  # Dedupe

    def _handle_error(
        self,
        error: RewriteError,
        expr: Any,
        rules: List[List],
        context: Optional[Dict[str, Any]]
    ) -> Optional[AgentAction]:
        """
        Handle an error by deciding what action to take.
        """
        if error.error_type == 'unknown_op' and self.correct_typos:
            return self._handle_unknown_operator(error, expr)

        elif error.error_type == 'no_match' and self.infer_missing_rules:
            return self._handle_no_match(error, expr, rules, context)

        elif error.error_type == 'infinite_loop':
            return AgentAction(
                action_type='give_up',
                message="Infinite loop detected - cannot proceed"
            )

        return None

    def _handle_unknown_operator(
        self,
        error: RewriteError,
        expr: Any
    ) -> Optional[AgentAction]:
        """Handle unknown operator by suggesting corrections."""
        unknown_ops = error.context.get('unknown_operators', [])
        if not unknown_ops:
            return None

        corrections = {}
        for op in unknown_ops:
            close = get_close_matches(op, self.known_operators, n=1, cutoff=0.6)
            if close:
                corrections[op] = close[0]

        if not corrections:
            return AgentAction(
                action_type='give_up',
                details={'unknown_operators': unknown_ops},
                message=f"Unknown operators with no close matches: {unknown_ops}"
            )

        # Apply corrections
        def correct_expr(e):
            if isinstance(e, list) and e:
                op = e[0]
                if op in corrections:
                    return [corrections[op]] + [correct_expr(sub) for sub in e[1:]]
                return [op] + [correct_expr(sub) for sub in e[1:]]
            return e

        corrected = correct_expr(expr)

        return AgentAction(
            action_type='correct_typo',
            details={
                'corrections': corrections,
                'original_expr': expr,
                'corrected_expr': corrected
            },
            message=f"Corrected typos: {corrections}"
        )

    def _handle_no_match(
        self,
        error: RewriteError,
        expr: Any,
        rules: List[List],
        context: Optional[Dict[str, Any]]
    ) -> Optional[AgentAction]:
        """Handle no-match error by inferring a rule."""
        if not self.rule_inferrer.enabled:
            return None

        inferred = self.rule_inferrer.infer_rule(expr, rules, context)

        if inferred:
            return AgentAction(
                action_type='infer_rule',
                details={
                    'rule': inferred.to_pair(),
                    'inferred_rule': inferred
                },
                message=f"Inferred rule: {format_dsl_rule(inferred.to_pair())}"
            )

        return AgentAction(
            action_type='give_up',
            message="Could not infer a matching rule"
        )

    def reset(self):
        """Reset agent state."""
        self.actions_taken = []
        self.inferred_rules = []
        self.rule_inferrer.reset()

    def get_inferred_rules(self) -> List[List]:
        """Get all rules inferred during this session."""
        return self.inferred_rules.copy()


def create_agent(
    provider: str = "ollama",
    model: str = "phi4-mini:latest",
    enabled: bool = True,
    **kwargs
) -> LLMRewriteAgent:
    """
    Create an LLMRewriteAgent with the specified provider.

    Args:
        provider: "ollama", "anthropic", or "openai"
        model: Model name/ID
        enabled: Whether agent is enabled
        **kwargs: Additional arguments for LLMRewriteAgent

    Returns:
        Configured LLMRewriteAgent instance
    """
    from .explainer import OllamaProvider, AnthropicProvider, OpenAIProvider

    if provider == "ollama":
        llm_provider = OllamaProvider(model=model)
    elif provider == "anthropic":
        llm_provider = AnthropicProvider(model=model)
    elif provider == "openai":
        llm_provider = OpenAIProvider(model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return LLMRewriteAgent(provider=llm_provider, enabled=enabled, **kwargs)
