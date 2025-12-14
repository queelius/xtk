"""Tests for the LLM rule inferrer."""

import unittest
from unittest.mock import MagicMock, patch
import os

from xtk.llm_inferrer import (
    LLMRuleInferrer, InferredRule, create_inferrer
)


class TestInferredRule(unittest.TestCase):
    """Test InferredRule dataclass."""

    def test_to_pair(self):
        """Test converting to [pattern, skeleton] pair."""
        rule = InferredRule(
            pattern=['+', ['?', 'x'], 0],
            skeleton=[':', 'x'],
            expression=['+', 'y', 0]
        )
        result = rule.to_pair()
        self.assertEqual(result, [['+', ['?', 'x'], 0], [':', 'x']])


class TestLLMRuleInferrerDisabled(unittest.TestCase):
    """Test LLMRuleInferrer when disabled."""

    def test_disabled_returns_none(self):
        """Test that disabled inferrer returns None."""
        inferrer = LLMRuleInferrer(enabled=False)
        result = inferrer.infer_rule(['+', 'x', 0], [])
        self.assertIsNone(result)

    def test_no_provider_returns_none(self):
        """Test that inferrer without provider returns None."""
        inferrer = LLMRuleInferrer(enabled=True, provider=None)
        result = inferrer.infer_rule(['+', 'x', 0], [])
        self.assertIsNone(result)


class TestLLMRuleInferrerMaxInferences(unittest.TestCase):
    """Test max inference limits."""

    def test_max_inferences_limit(self):
        """Test that inference stops after max_inferences."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True,
            max_inferences=2
        )

        # First two should work
        inferrer.infer_rule(['+', 'a', 0], [])
        inferrer.infer_rule(['+', 'b', 0], [])

        # Third should fail (limit reached)
        result = inferrer.infer_rule(['+', 'c', 0], [])
        self.assertIsNone(result)
        self.assertEqual(inferrer.inference_count, 2)


class TestLLMRuleInferrerCaching(unittest.TestCase):
    """Test caching behavior."""

    def test_cache_hit(self):
        """Test that cache prevents duplicate LLM calls."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True,
            cache_enabled=True
        )

        # First call
        inferrer.infer_rule(['+', 'x', 0], [])

        # Second call with same expression
        inferrer.infer_rule(['+', 'x', 0], [])

        # Provider should only be called once
        self.assertEqual(mock_provider.generate.call_count, 1)

    def test_cache_disabled(self):
        """Test that disabled cache allows duplicate LLM calls."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True,
            cache_enabled=False,
            max_inferences=10
        )

        # Two calls with same expression
        inferrer.infer_rule(['+', 'x', 0], [])
        inferrer.infer_rule(['+', 'x', 0], [])

        # Provider should be called twice
        self.assertEqual(mock_provider.generate.call_count, 2)


class TestLLMRuleInferrerValidation(unittest.TestCase):
    """Test rule validation."""

    def setUp(self):
        """Set up mock provider."""
        self.mock_provider = MagicMock()
        self.inferrer = LLMRuleInferrer(
            provider=self.mock_provider,
            enabled=True
        )

    def test_valid_rule(self):
        """Test that valid rule passes validation."""
        self.mock_provider.generate.return_value = "(+ ?x 0) => :x"

        result = self.inferrer.infer_rule(['+', 'y', 0], [])

        self.assertIsNotNone(result)
        self.assertEqual(result.pattern, ['+', ['?', 'x'], 0])
        self.assertEqual(result.skeleton, [':', 'x'])

    def test_unbound_variable_rejected(self):
        """Test that rule with unbound skeleton variable is rejected."""
        # This rule uses :y in skeleton but only binds x in pattern
        self.mock_provider.generate.return_value = "(+ ?x 0) => :y"

        result = self.inferrer.infer_rule(['+', 'a', 0], [])

        self.assertIsNone(result)

    def test_identity_rule_rejected(self):
        """Test that identity rule is rejected."""
        # This rule would return the same expression
        self.mock_provider.generate.return_value = "(+ ?x ?y) => (+ :x :y)"

        result = self.inferrer.infer_rule(['+', 'a', 'b'], [])

        self.assertIsNone(result)

    def test_non_matching_pattern_rejected(self):
        """Test that rule that doesn't match expression is rejected."""
        # Pattern expects multiplication but expression is addition
        self.mock_provider.generate.return_value = "(* ?x 0) => 0"

        result = self.inferrer.infer_rule(['+', 'a', 0], [])

        self.assertIsNone(result)


class TestLLMRuleInferrerResponseParsing(unittest.TestCase):
    """Test LLM response parsing."""

    def setUp(self):
        """Set up mock provider."""
        self.mock_provider = MagicMock()
        self.inferrer = LLMRuleInferrer(
            provider=self.mock_provider,
            enabled=True
        )

    def test_parse_clean_response(self):
        """Test parsing clean rule response."""
        self.mock_provider.generate.return_value = "(+ ?x 0) => :x"

        result = self.inferrer.infer_rule(['+', 'y', 0], [])

        self.assertIsNotNone(result)

    def test_parse_response_with_explanation(self):
        """Test parsing response with surrounding text."""
        self.mock_provider.generate.return_value = """
        Here's a rule that handles addition with zero:

        (+ ?x 0) => :x

        This implements the identity property.
        """

        result = self.inferrer.infer_rule(['+', 'y', 0], [])

        self.assertIsNotNone(result)
        self.assertEqual(result.pattern, ['+', ['?', 'x'], 0])

    def test_parse_invalid_response(self):
        """Test parsing invalid response."""
        self.mock_provider.generate.return_value = "I don't know how to help"

        result = self.inferrer.infer_rule(['+', 'y', 0], [])

        self.assertIsNone(result)


class TestLLMRuleInferrerCallback(unittest.TestCase):
    """Test inference callback."""

    def test_callback_called(self):
        """Test that callback is called on successful inference."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        callback_calls = []

        def on_inference(rule):
            callback_calls.append(rule)

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True,
            on_inference=on_inference
        )

        inferrer.infer_rule(['+', 'y', 0], [])

        self.assertEqual(len(callback_calls), 1)
        self.assertIsInstance(callback_calls[0], InferredRule)


class TestLLMRuleInferrerReset(unittest.TestCase):
    """Test reset functionality."""

    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True
        )

        # Make some inferences
        inferrer.infer_rule(['+', 'a', 0], [])
        inferrer.infer_rule(['+', 'b', 0], [])

        self.assertEqual(inferrer.inference_count, 2)
        self.assertEqual(len(inferrer.inferred_rules), 2)

        # Reset
        inferrer.reset()

        self.assertEqual(inferrer.inference_count, 0)
        self.assertEqual(len(inferrer.inferred_rules), 0)
        self.assertEqual(len(inferrer.cache), 0)


class TestLLMRuleInferrerGetInferred(unittest.TestCase):
    """Test getting inferred rules."""

    def test_get_inferred_rules(self):
        """Test getting all inferred rules."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True
        )

        inferrer.infer_rule(['+', 'a', 0], [])
        inferrer.infer_rule(['+', 'b', 0], [])

        rules = inferrer.get_inferred_rules()

        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0], [['+', ['?', 'x'], 0], [':', 'x']])


class TestLLMRuleInferrerPrompt(unittest.TestCase):
    """Test prompt building."""

    def test_prompt_includes_expression(self):
        """Test that prompt includes the expression."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True
        )

        inferrer.infer_rule(['+', 'y', 0], [])

        # Check that the prompt was called with something containing the expression
        call_args = mock_provider.generate.call_args[0][0]
        self.assertIn('(+ y 0)', call_args)

    def test_prompt_includes_existing_rules(self):
        """Test that prompt includes existing rules."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "(+ ?x 0) => :x"

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True
        )

        existing_rules = [
            [['*', ['?', 'x'], 1], [':', 'x']],
            [['*', ['?', 'x'], 0], 0]
        ]

        inferrer.infer_rule(['+', 'y', 0], existing_rules)

        call_args = mock_provider.generate.call_args[0][0]
        self.assertIn('(* ?x 1) => :x', call_args)


class TestLLMRuleInferrerProviderError(unittest.TestCase):
    """Test handling provider errors."""

    def test_provider_exception_returns_none(self):
        """Test that provider exception returns None."""
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = Exception("Network error")

        inferrer = LLMRuleInferrer(
            provider=mock_provider,
            enabled=True
        )

        result = inferrer.infer_rule(['+', 'y', 0], [])

        self.assertIsNone(result)


class TestCreateInferrer(unittest.TestCase):
    """Test create_inferrer factory function."""

    def test_create_ollama_inferrer(self):
        """Test creating Ollama inferrer."""
        # Skip if no SKIP_OLLAMA_TESTS is set
        if os.environ.get('SKIP_OLLAMA_TESTS', '').lower() == 'true':
            self.skipTest("SKIP_OLLAMA_TESTS is set")

        inferrer = create_inferrer(
            provider="ollama",
            model="phi4-mini:latest",
            enabled=False  # Don't actually make requests
        )

        self.assertIsInstance(inferrer, LLMRuleInferrer)
        self.assertFalse(inferrer.enabled)

    def test_create_unknown_provider_raises(self):
        """Test that unknown provider raises error."""
        with self.assertRaises(ValueError):
            create_inferrer(provider="unknown")


class TestExtractVariables(unittest.TestCase):
    """Test variable extraction helpers."""

    def setUp(self):
        """Set up inferrer."""
        self.inferrer = LLMRuleInferrer(enabled=False)

    def test_extract_pattern_vars_simple(self):
        """Test extracting variables from simple pattern."""
        pattern = ['+', ['?', 'x'], ['?', 'y']]
        vars_found = self.inferrer._extract_pattern_vars(pattern)
        self.assertEqual(vars_found, {'x', 'y'})

    def test_extract_pattern_vars_typed(self):
        """Test extracting variables from typed pattern."""
        pattern = ['dd', ['?c', 'c'], ['?v', 'v']]
        vars_found = self.inferrer._extract_pattern_vars(pattern)
        self.assertEqual(vars_found, {'c', 'v'})

    def test_extract_skeleton_vars(self):
        """Test extracting variables from skeleton."""
        skeleton = ['+', [':', 'x'], [':', 'y']]
        vars_found = self.inferrer._extract_skeleton_vars(skeleton)
        self.assertEqual(vars_found, {'x', 'y'})

    def test_extract_nested_vars(self):
        """Test extracting variables from nested expression."""
        pattern = ['+', ['*', ['?', 'a'], ['?', 'b']], ['?', 'c']]
        vars_found = self.inferrer._extract_pattern_vars(pattern)
        self.assertEqual(vars_found, {'a', 'b', 'c'})


class TestLLMRuleInferrerIntegration(unittest.TestCase):
    """Integration tests with real LLM (requires Ollama running locally)."""

    def test_infer_real_rule_with_ollama(self):
        """Test real rule inference with local Ollama."""
        # Skip if SKIP_OLLAMA_TESTS is set
        if os.environ.get('SKIP_OLLAMA_TESTS', '').lower() == 'true':
            self.skipTest("SKIP_OLLAMA_TESTS is set")

        # Check if Ollama is available
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                self.skipTest("Ollama server not running")
        except Exception:
            self.skipTest("Ollama server not available")

        # Create inferrer with real Ollama
        inferrer = create_inferrer(
            provider="ollama",
            model="phi4-mini:latest",
            enabled=True,
            max_inferences=1
        )

        # Try to infer a rule for (+ x 0)
        # This is a classic identity rule that LLMs should know
        existing_rules = [
            [['*', ['?', 'y'], 1], [':', 'y']],  # Example: y * 1 => y
        ]

        result = inferrer.infer_rule(['+', 'x', 0], existing_rules)

        # The LLM should infer something like (+ ?x 0) => :x
        if result:
            print(f"\nInferred rule: {result.pattern} => {result.skeleton}")
            # Verify it's a valid rule
            self.assertIsInstance(result.pattern, list)
            self.assertIsInstance(result.skeleton, (list, str, int))


if __name__ == '__main__':
    unittest.main()
