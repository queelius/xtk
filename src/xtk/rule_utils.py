"""
Utilities for working with rules, including metadata support.
"""

from typing import Union, Dict, List, Any, Optional, Tuple
from .rewriter import RuleType


class RichRule:
    """A rule with optional metadata for better explanations."""

    def __init__(
        self,
        pattern: Any,
        skeleton: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        examples: Optional[List[str]] = None
    ):
        self.pattern = pattern
        self.skeleton = skeleton
        self.name = name
        self.description = description
        self.category = category
        self.examples = examples or []

    def to_rule_pair(self) -> RuleType:
        """Convert to [pattern, skeleton] format for rewriter."""
        return [self.pattern, self.skeleton]

    @classmethod
    def from_rule(cls, rule: Union[List, Dict]) -> 'RichRule':
        """
        Create RichRule from either list or dict format.

        Args:
            rule: Either [pattern, skeleton] or dict with pattern/skeleton/metadata

        Returns:
            RichRule instance
        """
        if isinstance(rule, dict):
            return cls(
                pattern=rule['pattern'],
                skeleton=rule['skeleton'],
                name=rule.get('name'),
                description=rule.get('description'),
                category=rule.get('category'),
                examples=rule.get('examples', [])
            )
        elif isinstance(rule, list) and len(rule) == 2:
            # Simple [pattern, skeleton] format
            return cls(pattern=rule[0], skeleton=rule[1])
        else:
            raise ValueError(f"Invalid rule format: {rule}")

    def __repr__(self):
        if self.name:
            return f"RichRule({self.name})"
        return f"RichRule({self.pattern} → {self.skeleton})"


def normalize_rules(rules: List[Union[List, Dict]]) -> Tuple[List[RuleType], List[RichRule]]:
    """
    Normalize a list of rules to both formats.

    Args:
        rules: List of rules in any format

    Returns:
        Tuple of (rule_pairs, rich_rules) for use in rewriter and explanations
    """
    rich_rules = [RichRule.from_rule(r) for r in rules]
    rule_pairs = [r.to_rule_pair() for r in rich_rules]
    return rule_pairs, rich_rules


def get_rule_metadata(rule: Union[List, Dict]) -> Dict[str, Any]:
    """
    Extract metadata from a rule if available.

    Args:
        rule: Rule in any format

    Returns:
        Dictionary with available metadata
    """
    if isinstance(rule, dict):
        return {
            'name': rule.get('name'),
            'description': rule.get('description'),
            'category': rule.get('category'),
            'examples': rule.get('examples', [])
        }
    return {'name': None, 'description': None, 'category': None, 'examples': []}
