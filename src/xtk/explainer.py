"""
LLM-powered explanations for term rewriting steps.

This module provides natural language explanations for rewrite steps,
using structured rule metadata as context for better LLM outputs.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

    def generate(self, prompt: str, max_tokens: int = 300, **kwargs) -> str:
        """Generate explanation using Claude API."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        client = anthropic.Anthropic(api_key=self.api_key)

        message = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

    def generate(self, prompt: str, max_tokens: int = 300, **kwargs) -> str:
        """Generate explanation using OpenAI API."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

        client = openai.OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )

        return response.choices[0].message.content


class OllamaProvider(LLMProvider):
    """Local Ollama provider."""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate explanation using Ollama."""
        try:
            import requests
        except ImportError:
            raise ImportError("requests package not installed. Run: pip install requests")

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False}
        )

        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama error: {response.text}")


class ExplanationCache:
    """Simple file-based cache for explanations."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".xtk_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_key(self, prompt: str) -> str:
        """Create cache key from prompt."""
        return hashlib.sha256(prompt.encode()).hexdigest()

    def get(self, prompt: str) -> Optional[str]:
        """Get cached explanation."""
        key = self._make_key(prompt)
        cache_file = self.cache_dir / f"{key}.txt"

        if cache_file.exists():
            return cache_file.read_text()
        return None

    def set(self, prompt: str, explanation: str):
        """Cache an explanation."""
        key = self._make_key(prompt)
        cache_file = self.cache_dir / f"{key}.txt"
        cache_file.write_text(explanation)


class RewriteExplainer:
    """
    Generates natural language explanations for rewrite steps.

    Uses structured metadata as context for LLM prompts, with caching
    to avoid redundant API calls.
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        use_cache: bool = True
    ):
        self.provider = provider
        self.cache = ExplanationCache() if use_cache else None

    @classmethod
    def from_config(cls, provider_name: str = "anthropic", **kwargs) -> 'RewriteExplainer':
        """
        Create explainer from configuration.

        Args:
            provider_name: "anthropic", "openai", "ollama", or "none"
            **kwargs: Provider-specific configuration

        Returns:
            RewriteExplainer instance
        """
        if provider_name == "none":
            return cls(provider=None)
        elif provider_name == "anthropic":
            provider = AnthropicProvider(**kwargs)
        elif provider_name == "openai":
            provider = OpenAIProvider(**kwargs)
        elif provider_name == "ollama":
            provider = OllamaProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

        return cls(provider=provider)

    def explain_step(
        self,
        expression: str,
        result: str,
        rule_name: Optional[str] = None,
        rule_description: Optional[str] = None,
        bindings: Optional[List] = None,
        pattern: Optional[str] = None,
        skeleton: Optional[str] = None
    ) -> str:
        """
        Generate explanation for a rewrite step.

        Args:
            expression: Original expression
            result: Rewritten expression
            rule_name: Name of the rule applied
            rule_description: Description of the rule
            bindings: Variable bindings from pattern matching
            pattern: Rule pattern
            skeleton: Rule skeleton

        Returns:
            Natural language explanation
        """
        # Build prompt
        prompt = self._build_prompt(
            expression=expression,
            result=result,
            rule_name=rule_name,
            rule_description=rule_description,
            bindings=bindings,
            pattern=pattern,
            skeleton=skeleton
        )

        # Check cache first
        if self.cache:
            cached = self.cache.get(prompt)
            if cached:
                return cached

        # Generate explanation
        if self.provider:
            explanation = self.provider.generate(prompt)
        else:
            # Fallback: use structured description
            explanation = self._fallback_explanation(
                expression, result, rule_name, rule_description
            )

        # Cache result
        if self.cache:
            self.cache.set(prompt, explanation)

        return explanation

    def _build_prompt(
        self,
        expression: str,
        result: str,
        rule_name: Optional[str],
        rule_description: Optional[str],
        bindings: Optional[List],
        pattern: Optional[str],
        skeleton: Optional[str]
    ) -> str:
        """Build LLM prompt from step information."""
        parts = [
            "You are explaining a symbolic computation step to a student learning mathematics and computer algebra.",
            "",
            f"Expression: {expression}",
            f"Result: {result}",
        ]

        if rule_name:
            parts.append(f"Rule Applied: {rule_name}")

        if rule_description:
            parts.append(f"Rule Description: {rule_description}")

        if pattern and skeleton:
            parts.extend([
                "",
                f"Pattern: {pattern}",
                f"Skeleton: {skeleton}"
            ])

        if bindings:
            parts.append("")
            parts.append("Matched Bindings:")
            for binding in bindings:
                if len(binding) == 2:
                    parts.append(f"  - {binding[0]}: {binding[1]}")

        parts.extend([
            "",
            "Explain this transformation step in 2-3 clear sentences.",
            "Focus on:",
            "1. Why this rule applies",
            "2. What the mathematical meaning is",
            "3. How the transformation works",
            "",
            "Be concise and pedagogical. Do not repeat the expressions."
        ])

        return "\n".join(parts)

    def _fallback_explanation(
        self,
        expression: str,
        result: str,
        rule_name: Optional[str],
        rule_description: Optional[str]
    ) -> str:
        """Generate basic explanation without LLM."""
        parts = []

        if rule_name:
            parts.append(f"Applied {rule_name}:")

        if rule_description:
            parts.append(rule_description)
        else:
            parts.append(f"Rewrote {expression} to {result}")

        return " ".join(parts)
