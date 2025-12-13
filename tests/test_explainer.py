"""
Tests for the explainer module - LLM-powered explanations for term rewriting.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from xtk.explainer import (
    LLMProvider,
    AnthropicProvider,
    OpenAIProvider,
    OllamaProvider,
    ExplanationCache,
    RewriteExplainer
)


class TestLLMProviderInterface(unittest.TestCase):
    """Test LLMProvider abstract base class."""

    def test_llm_provider_is_abstract(self):
        """Test that LLMProvider cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            LLMProvider()

    def test_llm_provider_requires_generate(self):
        """Test that subclasses must implement generate."""
        class BadProvider(LLMProvider):
            pass

        with self.assertRaises(TypeError):
            BadProvider()


class TestAnthropicProvider(unittest.TestCase):
    """Test AnthropicProvider class."""

    def test_init_requires_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                AnthropicProvider()
            self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicit API key."""
        provider = AnthropicProvider(api_key="test-key")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "claude-3-5-sonnet-20241022")

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        provider = AnthropicProvider(api_key="test-key", model="claude-3-opus")
        self.assertEqual(provider.model, "claude-3-opus")

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env-test-key'})
    def test_init_from_environment(self):
        """Test initialization from environment variable."""
        provider = AnthropicProvider()
        self.assertEqual(provider.api_key, "env-test-key")

    @unittest.skip("Requires anthropic package - integration test")
    def test_generate_calls_api(self):
        """Test that generate calls the Anthropic API correctly."""
        # This test requires the anthropic package to be installed
        # and proper API mocking. Skip for unit tests.
        pass


class TestOpenAIProvider(unittest.TestCase):
    """Test OpenAIProvider class."""

    def test_init_requires_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                OpenAIProvider()
            self.assertIn("OPENAI_API_KEY", str(ctx.exception))

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicit API key."""
        provider = OpenAIProvider(api_key="test-key")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "gpt-4")

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-3.5-turbo")
        self.assertEqual(provider.model, "gpt-3.5-turbo")

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'env-test-key'})
    def test_init_from_environment(self):
        """Test initialization from environment variable."""
        provider = OpenAIProvider()
        self.assertEqual(provider.api_key, "env-test-key")

    @unittest.skip("Requires openai package - integration test")
    def test_generate_calls_api(self):
        """Test that generate calls the OpenAI API correctly."""
        # This test requires the openai package to be installed
        # and proper API mocking. Skip for unit tests.
        pass


class TestOllamaProvider(unittest.TestCase):
    """Test OllamaProvider class."""

    def test_init_defaults(self):
        """Test initialization with default values."""
        provider = OllamaProvider()
        self.assertEqual(provider.model, "llama2")
        self.assertEqual(provider.base_url, "http://localhost:11434")

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        provider = OllamaProvider(model="mistral", base_url="http://custom:8080")
        self.assertEqual(provider.model, "mistral")
        self.assertEqual(provider.base_url, "http://custom:8080")

    def test_generate_success(self):
        """Test successful generation with local Ollama server."""
        import os
        # Skip if explicitly disabled or no Ollama available
        if os.environ.get('SKIP_OLLAMA_TESTS', '').lower() == 'true':
            self.skipTest("SKIP_OLLAMA_TESTS is set")

        try:
            import requests
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                self.skipTest("Ollama server not running")
        except Exception:
            self.skipTest("Ollama server not available")

        # Use a small, fast model for testing
        provider = OllamaProvider(model="phi4-mini:latest")
        result = provider.generate("Say 'test successful' in exactly two words.")

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_generate_error_bad_model(self):
        """Test generation error with non-existent model."""
        import os
        if os.environ.get('SKIP_OLLAMA_TESTS', '').lower() == 'true':
            self.skipTest("SKIP_OLLAMA_TESTS is set")

        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                self.skipTest("Ollama server not running")
        except Exception:
            self.skipTest("Ollama server not available")

        provider = OllamaProvider(model="nonexistent-model-xyz")
        with self.assertRaises(Exception):
            provider.generate("Test prompt")


class TestExplanationCache(unittest.TestCase):
    """Test ExplanationCache class."""

    def setUp(self):
        """Set up test directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.temp_dir)

    def test_init_creates_cache_dir(self):
        """Test that initialization creates cache directory."""
        cache_dir = self.temp_path / "test_cache"
        self.assertFalse(cache_dir.exists())

        cache = ExplanationCache(cache_dir=cache_dir)
        self.assertTrue(cache_dir.exists())

    def test_init_default_cache_dir(self):
        """Test initialization with default cache directory."""
        cache = ExplanationCache()
        self.assertEqual(cache.cache_dir, Path.home() / ".xtk_cache")

    def test_get_nonexistent_key(self):
        """Test getting a non-existent cache entry."""
        cache = ExplanationCache(cache_dir=self.temp_path / "cache")
        result = cache.get("nonexistent prompt")
        self.assertIsNone(result)

    def test_set_and_get(self):
        """Test setting and getting a cache entry."""
        cache = ExplanationCache(cache_dir=self.temp_path / "cache")

        cache.set("test prompt", "test explanation")
        result = cache.get("test prompt")

        self.assertEqual(result, "test explanation")

    def test_cache_persistence(self):
        """Test that cache persists across instances."""
        cache_dir = self.temp_path / "persistent_cache"

        # First instance sets value
        cache1 = ExplanationCache(cache_dir=cache_dir)
        cache1.set("persistent prompt", "persistent value")

        # Second instance retrieves value
        cache2 = ExplanationCache(cache_dir=cache_dir)
        result = cache2.get("persistent prompt")

        self.assertEqual(result, "persistent value")

    def test_different_prompts_different_keys(self):
        """Test that different prompts get different cache keys."""
        cache = ExplanationCache(cache_dir=self.temp_path / "cache")

        cache.set("prompt 1", "explanation 1")
        cache.set("prompt 2", "explanation 2")

        self.assertEqual(cache.get("prompt 1"), "explanation 1")
        self.assertEqual(cache.get("prompt 2"), "explanation 2")

    def test_make_key_deterministic(self):
        """Test that _make_key produces deterministic results."""
        cache = ExplanationCache(cache_dir=self.temp_path / "cache")

        key1 = cache._make_key("test prompt")
        key2 = cache._make_key("test prompt")

        self.assertEqual(key1, key2)

    def test_make_key_different_for_different_prompts(self):
        """Test that _make_key produces different keys for different prompts."""
        cache = ExplanationCache(cache_dir=self.temp_path / "cache")

        key1 = cache._make_key("prompt 1")
        key2 = cache._make_key("prompt 2")

        self.assertNotEqual(key1, key2)


class TestRewriteExplainer(unittest.TestCase):
    """Test RewriteExplainer class."""

    def setUp(self):
        """Set up test directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.temp_dir)

    def test_init_no_provider(self):
        """Test initialization without provider."""
        explainer = RewriteExplainer(provider=None)
        self.assertIsNone(explainer.provider)
        self.assertIsNotNone(explainer.cache)

    def test_init_no_cache(self):
        """Test initialization without cache."""
        explainer = RewriteExplainer(provider=None, use_cache=False)
        self.assertIsNone(explainer.cache)

    def test_init_with_provider(self):
        """Test initialization with mock provider."""
        mock_provider = Mock(spec=LLMProvider)
        explainer = RewriteExplainer(provider=mock_provider)
        self.assertEqual(explainer.provider, mock_provider)

    def test_from_config_none_provider(self):
        """Test from_config with 'none' provider."""
        explainer = RewriteExplainer.from_config(provider_name="none")
        self.assertIsNone(explainer.provider)

    def test_from_config_unknown_provider(self):
        """Test from_config with unknown provider."""
        with self.assertRaises(ValueError) as ctx:
            RewriteExplainer.from_config(provider_name="unknown")
        self.assertIn("Unknown provider", str(ctx.exception))

    def test_from_config_anthropic(self):
        """Test from_config with Anthropic provider."""
        explainer = RewriteExplainer.from_config(
            provider_name="anthropic",
            api_key="test-key"
        )
        self.assertIsInstance(explainer.provider, AnthropicProvider)

    def test_from_config_openai(self):
        """Test from_config with OpenAI provider."""
        explainer = RewriteExplainer.from_config(
            provider_name="openai",
            api_key="test-key"
        )
        self.assertIsInstance(explainer.provider, OpenAIProvider)

    def test_from_config_ollama(self):
        """Test from_config with Ollama provider."""
        explainer = RewriteExplainer.from_config(provider_name="ollama")
        self.assertIsInstance(explainer.provider, OllamaProvider)

    def test_explain_step_fallback_no_provider(self):
        """Test explain_step falls back when no provider."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        result = explainer.explain_step(
            expression="['+', 'x', 0]",
            result="x",
            rule_name="additive_identity",
            rule_description="Adding zero to any expression yields the expression"
        )

        self.assertIn("additive_identity", result)
        self.assertIn("Adding zero", result)

    def test_explain_step_fallback_minimal(self):
        """Test explain_step fallback with minimal info."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        result = explainer.explain_step(
            expression="x",
            result="y"
        )

        self.assertIn("Rewrote", result)
        self.assertIn("x", result)
        self.assertIn("y", result)

    def test_explain_step_with_provider(self):
        """Test explain_step with mock provider."""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = "LLM generated explanation"

        explainer = RewriteExplainer(provider=mock_provider, use_cache=False)

        result = explainer.explain_step(
            expression="['+', 'x', 0]",
            result="x"
        )

        self.assertEqual(result, "LLM generated explanation")
        mock_provider.generate.assert_called_once()

    def test_explain_step_uses_cache(self):
        """Test that explain_step uses cache."""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = "LLM explanation"

        cache_dir = self.temp_path / "cache"
        cache = ExplanationCache(cache_dir=cache_dir)

        explainer = RewriteExplainer(provider=mock_provider)
        explainer.cache = cache

        # First call should use provider
        result1 = explainer.explain_step(expression="x", result="y")
        self.assertEqual(result1, "LLM explanation")
        self.assertEqual(mock_provider.generate.call_count, 1)

        # Second identical call should use cache
        result2 = explainer.explain_step(expression="x", result="y")
        self.assertEqual(result2, "LLM explanation")
        # Provider should not be called again
        self.assertEqual(mock_provider.generate.call_count, 1)

    def test_build_prompt_basic(self):
        """Test _build_prompt with basic inputs."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        prompt = explainer._build_prompt(
            expression="['+', 'x', 0]",
            result="x",
            rule_name=None,
            rule_description=None,
            bindings=None,
            pattern=None,
            skeleton=None
        )

        self.assertIn("Expression:", prompt)
        self.assertIn("Result:", prompt)
        self.assertIn("['+', 'x', 0]", prompt)

    def test_build_prompt_with_rule_info(self):
        """Test _build_prompt with rule information."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        prompt = explainer._build_prompt(
            expression="['+', 'x', 0]",
            result="x",
            rule_name="additive_identity",
            rule_description="x + 0 = x",
            bindings=None,
            pattern=None,
            skeleton=None
        )

        self.assertIn("Rule Applied:", prompt)
        self.assertIn("additive_identity", prompt)
        self.assertIn("Rule Description:", prompt)
        self.assertIn("x + 0 = x", prompt)

    def test_build_prompt_with_pattern_skeleton(self):
        """Test _build_prompt with pattern and skeleton."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        prompt = explainer._build_prompt(
            expression="['+', 'x', 0]",
            result="x",
            rule_name=None,
            rule_description=None,
            bindings=None,
            pattern="['+', ['?', 'x'], 0]",
            skeleton="[':', 'x']"
        )

        self.assertIn("Pattern:", prompt)
        self.assertIn("Skeleton:", prompt)

    def test_build_prompt_with_bindings(self):
        """Test _build_prompt with bindings."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        prompt = explainer._build_prompt(
            expression="['+', 'y', 0]",
            result="y",
            rule_name=None,
            rule_description=None,
            bindings=[['x', 'y']],
            pattern=None,
            skeleton=None
        )

        self.assertIn("Matched Bindings:", prompt)
        self.assertIn("x: y", prompt)

    def test_fallback_explanation_with_name(self):
        """Test _fallback_explanation with rule name."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        result = explainer._fallback_explanation(
            expression="x",
            result="y",
            rule_name="test_rule",
            rule_description="Test description"
        )

        self.assertIn("Applied test_rule", result)
        self.assertIn("Test description", result)

    def test_fallback_explanation_no_name(self):
        """Test _fallback_explanation without rule name."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        result = explainer._fallback_explanation(
            expression="x",
            result="y",
            rule_name=None,
            rule_description=None
        )

        self.assertIn("Rewrote", result)
        self.assertIn("x", result)
        self.assertIn("y", result)


class TestExplainerIntegration(unittest.TestCase):
    """Integration tests for the explainer module."""

    def setUp(self):
        """Set up test directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.temp_dir)

    def test_full_workflow_no_llm(self):
        """Test complete workflow without LLM provider."""
        explainer = RewriteExplainer(provider=None, use_cache=False)

        # Simulate a differentiation step
        explanation = explainer.explain_step(
            expression="['dd', ['*', 2, 'x'], 'x']",
            result="['*', 2, ['dd', 'x', 'x']]",
            rule_name="constant_multiple_derivative",
            rule_description="d/dx(c*f) = c * d/dx(f) - pull constants out",
            bindings=[['c', '2'], ['f', 'x']],
            pattern="['dd', ['*', ['?c', 'c'], ['?', 'f']], ['?v', 'x']]",
            skeleton="['*', [':', 'c'], ['dd', [':', 'f'], [':', 'x']]]"
        )

        # Should fall back to rule-based explanation
        self.assertIn("constant_multiple_derivative", explanation)
        self.assertIn("d/dx(c*f)", explanation)

    def test_full_workflow_with_mock_llm(self):
        """Test complete workflow with mocked LLM."""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = (
            "This step applies the constant multiple rule. When differentiating "
            "a constant times a function, we can pull the constant out and just "
            "differentiate the function part."
        )

        cache_dir = self.temp_path / "cache"
        explainer = RewriteExplainer(provider=mock_provider)
        explainer.cache = ExplanationCache(cache_dir=cache_dir)

        explanation = explainer.explain_step(
            expression="['dd', ['*', 2, 'x'], 'x']",
            result="['*', 2, ['dd', 'x', 'x']]",
            rule_name="constant_multiple",
            rule_description="d/dx(c*f) = c * d/dx(f)"
        )

        self.assertIn("constant multiple rule", explanation)
        mock_provider.generate.assert_called_once()

    def test_multiple_steps_cached(self):
        """Test that multiple identical steps use cache."""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = "Explanation"

        cache_dir = self.temp_path / "cache"
        explainer = RewriteExplainer(provider=mock_provider)
        explainer.cache = ExplanationCache(cache_dir=cache_dir)

        # Call multiple times with same args
        for _ in range(5):
            explainer.explain_step(expression="x", result="y")

        # Provider should only be called once
        self.assertEqual(mock_provider.generate.call_count, 1)


if __name__ == '__main__':
    unittest.main()
