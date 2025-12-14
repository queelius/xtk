"""
LLM-based rule inference for xtk.

When no existing rule matches an expression, optionally ask an LLM
to infer a rewrite rule that could handle it.
"""

import logging
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field

from .rule_dsl import parse_rule_line, format_dsl_rule, format_dsl_expr
from .rewriter import match, instantiate
from .parser import format_sexpr

logger = logging.getLogger(__name__)


@dataclass
class InferredRule:
    """A rule inferred by the LLM with metadata."""
    pattern: Any
    skeleton: Any
    expression: Any  # The expression that triggered inference
    explanation: Optional[str] = None
    confidence: Optional[float] = None

    def to_pair(self) -> List:
        """Convert to [pattern, skeleton] format."""
        return [self.pattern, self.skeleton]


@dataclass
class LLMRuleInferrer:
    """
    Infer missing rewrite rules via LLM.

    This is an optional feature that can be enabled to automatically
    generate rules when no existing rule matches an expression.

    Example usage:
        from xtk import rewriter
        from xtk.llm_inferrer import LLMRuleInferrer
        from xtk.explainer import OllamaProvider

        inferrer = LLMRuleInferrer(
            provider=OllamaProvider(model="phi4-mini:latest"),
            enabled=True
        )

        # Use with rewriter
        rules = [...]
        simplify = rewriter(rules)
        result = simplify(expr)

        # If no rule matched and you want to try inference:
        if result == expr:
            new_rule = inferrer.infer_rule(expr, rules)
            if new_rule:
                rules.append(new_rule.to_pair())
                result = simplify(expr)
    """
    provider: Any = None  # LLMProvider instance
    enabled: bool = False
    max_inferences: int = 10
    cache_enabled: bool = True
    require_approval: bool = False  # If True, return rule for user approval
    on_inference: Optional[Callable[[InferredRule], None]] = None  # Callback

    # Internal state
    inference_count: int = field(default=0, init=False)
    cache: Dict[str, Optional[InferredRule]] = field(default_factory=dict, init=False)
    inferred_rules: List[InferredRule] = field(default_factory=list, init=False)

    def infer_rule(
        self,
        expr: Any,
        existing_rules: List[List],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[InferredRule]:
        """
        Attempt to infer a rule for the given expression.

        Args:
            expr: The expression that didn't match any rule
            existing_rules: Current rule set (used as few-shot examples)
            context: Optional additional context (domain hints, etc.)

        Returns:
            InferredRule if successful, None otherwise
        """
        if not self.enabled or self.provider is None:
            return None

        if self.inference_count >= self.max_inferences:
            logger.warning(f"Max inferences ({self.max_inferences}) reached")
            return None

        # Check cache
        expr_key = str(expr)
        if self.cache_enabled and expr_key in self.cache:
            logger.debug(f"Cache hit for {expr_key}")
            return self.cache[expr_key]

        # Build prompt
        prompt = self._build_prompt(expr, existing_rules, context)

        # Get response from LLM
        try:
            response = self.provider.generate(prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            if self.cache_enabled:
                self.cache[expr_key] = None
            return None

        # Parse and validate
        rule = self._parse_response(response, expr)

        if rule and self._validate_rule(rule, expr):
            self.inference_count += 1
            self.inferred_rules.append(rule)

            if self.cache_enabled:
                self.cache[expr_key] = rule

            # Call callback if provided
            if self.on_inference:
                self.on_inference(rule)

            logger.info(f"Inferred rule: {format_dsl_rule(rule.to_pair())}")
            return rule

        if self.cache_enabled:
            self.cache[expr_key] = None

        return None

    def _build_prompt(
        self,
        expr: Any,
        existing_rules: List[List],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for the LLM."""
        # Format existing rules as examples (limit to avoid token overflow)
        example_rules = existing_rules[:10] if len(existing_rules) > 10 else existing_rules
        rules_text = "\n".join(
            format_dsl_rule(r) for r in example_rules
        ) if example_rules else "(no rules loaded)"

        # Format the expression
        expr_text = format_dsl_expr(expr) if isinstance(expr, list) else str(expr)

        # Build context hints
        context_text = ""
        if context:
            if "domain" in context:
                context_text += f"\nDomain: {context['domain']}"
            if "hints" in context:
                context_text += f"\nHints: {context['hints']}"

        prompt = f"""You are a symbolic math expert. Write a rewrite rule for the expression below.

RULE SYNTAX:
- ?x matches anything
- :x substitutes the matched value
- Format: (operator ?arg1 ?arg2) => result

EXISTING RULES:
{rules_text}

EXPRESSION: {expr_text}
{context_text}
Write ONE rule. Output ONLY the rule, nothing else.
Example: (* ?x 0) => 0

RULE:"""

        return prompt

    def _parse_response(self, response: str, expr: Any) -> Optional[InferredRule]:
        """Parse the LLM response into a rule."""
        # Clean up response
        response = response.strip()

        # Try to extract rule from response
        # Look for pattern => skeleton format
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if '=>' in line and '(' in line:
                # Try to parse this line as a rule
                parsed = parse_rule_line(line)
                if parsed:
                    return InferredRule(
                        pattern=parsed.pattern,
                        skeleton=parsed.skeleton,
                        expression=expr,
                        explanation=parsed.description
                    )

        # If no rule found in lines, try the whole response
        if '=>' in response:
            # Find the rule part
            import re
            match_obj = re.search(r'\([^)]*\?\w+[^)]*\)\s*=>\s*\S+', response)
            if match_obj:
                parsed = parse_rule_line(match_obj.group())
                if parsed:
                    return InferredRule(
                        pattern=parsed.pattern,
                        skeleton=parsed.skeleton,
                        expression=expr
                    )

        logger.warning(f"Could not parse LLM response: {response[:200]}")
        return None

    def _validate_rule(self, rule: InferredRule, original_expr: Any) -> bool:
        """Validate an inferred rule."""
        pattern = rule.pattern
        skeleton = rule.skeleton

        # 1. Pattern must be a compound expression (list)
        if not isinstance(pattern, list) or len(pattern) == 0:
            logger.debug("Pattern must be non-empty list")
            return False

        # 2. Extract variables from pattern
        pattern_vars = self._extract_pattern_vars(pattern)

        # 3. Extract variables from skeleton
        skeleton_vars = self._extract_skeleton_vars(skeleton)

        # 4. All skeleton vars must be bound in pattern
        if not skeleton_vars.issubset(pattern_vars):
            unbound = skeleton_vars - pattern_vars
            logger.debug(f"Skeleton uses unbound variables: {unbound}")
            return False

        # 5. Pattern should match the original expression
        bindings = match(pattern, original_expr, [])  # Use empty assoc list, not dict
        if bindings == "failed":
            logger.debug("Pattern doesn't match original expression")
            return False

        # 6. Rule shouldn't be an identity (would cause infinite loop)
        result = instantiate(skeleton, bindings)
        if result == original_expr:
            logger.debug("Rule is an identity (no transformation)")
            return False

        return True

    def _extract_pattern_vars(self, expr: Any) -> set:
        """Extract variable names from a pattern."""
        vars_found = set()

        if isinstance(expr, list):
            if len(expr) == 2 and expr[0] in ('?', '?c', '?v'):
                vars_found.add(expr[1])
            else:
                for item in expr:
                    vars_found.update(self._extract_pattern_vars(item))

        return vars_found

    def _extract_skeleton_vars(self, expr: Any) -> set:
        """Extract variable names from a skeleton."""
        vars_found = set()

        if isinstance(expr, list):
            if len(expr) == 2 and expr[0] == ':':
                vars_found.add(expr[1])
            else:
                for item in expr:
                    vars_found.update(self._extract_skeleton_vars(item))

        return vars_found

    def reset(self):
        """Reset inference state."""
        self.inference_count = 0
        self.cache.clear()
        self.inferred_rules.clear()

    def get_inferred_rules(self) -> List[List]:
        """Get all inferred rules as [pattern, skeleton] pairs."""
        return [rule.to_pair() for rule in self.inferred_rules]


def create_inferrer(
    provider: str = "ollama",
    model: str = "phi4-mini:latest",
    enabled: bool = True,
    **kwargs
) -> LLMRuleInferrer:
    """
    Create an LLMRuleInferrer with the specified provider.

    Args:
        provider: "ollama", "anthropic", or "openai"
        model: Model name/ID
        enabled: Whether inference is enabled
        **kwargs: Additional arguments for LLMRuleInferrer

    Returns:
        Configured LLMRuleInferrer instance
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

    return LLMRuleInferrer(provider=llm_provider, enabled=enabled, **kwargs)
