"""Test suite for rule_utils.py - RichRule class and normalize_rules function."""

import unittest
from xtk.rule_utils import RichRule, normalize_rules


class TestRichRule(unittest.TestCase):
    """Test the RichRule class."""

    def test_from_rule_with_dict(self):
        """Test creating RichRule from dict format."""
        rule_dict = {
            'pattern': ['+', ['?', 'x'], 0],
            'skeleton': [':', 'x'],
            'name': 'add_zero',
            'description': 'Adding zero gives the original value',
            'category': 'algebra',
            'examples': [
                {'input': ['+', 'x', 0], 'output': 'x'}
            ]
        }

        rich_rule = RichRule.from_rule(rule_dict)

        self.assertEqual(rich_rule.pattern, ['+', ['?', 'x'], 0])
        self.assertEqual(rich_rule.skeleton, [':', 'x'])
        self.assertEqual(rich_rule.name, 'add_zero')
        self.assertEqual(rich_rule.description, 'Adding zero gives the original value')
        self.assertEqual(rich_rule.category, 'algebra')
        self.assertIsNotNone(rich_rule.examples)
        self.assertEqual(len(rich_rule.examples), 1)

    def test_from_rule_with_list_pair(self):
        """Test creating RichRule from list pair format."""
        rule_pair = [['+', ['?', 'x'], 0], [':', 'x']]

        rich_rule = RichRule.from_rule(rule_pair)

        self.assertEqual(rich_rule.pattern, ['+', ['?', 'x'], 0])
        self.assertEqual(rich_rule.skeleton, [':', 'x'])
        self.assertIsNone(rich_rule.name)
        self.assertIsNone(rich_rule.description)
        self.assertIsNone(rich_rule.category)
        # examples defaults to [] not None
        self.assertEqual(rich_rule.examples, [])

    def test_from_rule_with_tuple_pair_fails(self):
        """Test that tuple pair format is not supported."""
        rule_pair = (['+', ['?', 'x'], 0], [':', 'x'])

        # Tuples are not supported, only lists
        with self.assertRaises(ValueError):
            RichRule.from_rule(rule_pair)

    def test_to_rule_pair(self):
        """Test converting RichRule back to rule pair."""
        rich_rule = RichRule(
            pattern=['+', ['?', 'x'], 0],
            skeleton=[':', 'x'],
            name='add_zero',
            description='Test rule'
        )

        rule_pair = rich_rule.to_rule_pair()

        self.assertEqual(rule_pair, [['+', ['?', 'x'], 0], [':', 'x']])
        self.assertIsInstance(rule_pair, list)
        self.assertEqual(len(rule_pair), 2)

    def test_from_rule_invalid_format(self):
        """Test that invalid formats raise ValueError or KeyError."""
        with self.assertRaises(ValueError):
            RichRule.from_rule("invalid")

        with self.assertRaises(ValueError):
            RichRule.from_rule([1, 2, 3])  # Wrong length list

        with self.assertRaises(KeyError):
            RichRule.from_rule({})  # Empty dict - missing 'pattern' key


class TestNormalizeRules(unittest.TestCase):
    """Test the normalize_rules function."""

    def test_normalize_empty_list(self):
        """Test normalizing empty rule list."""
        rule_pairs, rich_rules = normalize_rules([])
        self.assertEqual(rule_pairs, [])
        self.assertEqual(rich_rules, [])

    def test_normalize_list_pairs(self):
        """Test normalizing rules in list pair format."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]

        rule_pairs, rich_rules = normalize_rules(rules)

        self.assertEqual(len(rule_pairs), 2)
        self.assertEqual(len(rich_rules), 2)
        self.assertEqual(rule_pairs, rules)  # Should remain unchanged
        # Rich rules should have no metadata
        self.assertIsNone(rich_rules[0].name)
        self.assertIsNone(rich_rules[1].name)

    def test_normalize_dict_rules(self):
        """Test normalizing rules in dict format."""
        rules = [
            {
                'pattern': ['+', ['?', 'x'], 0],
                'skeleton': [':', 'x'],
                'name': 'add_zero'
            },
            {
                'pattern': ['*', ['?', 'x'], 1],
                'skeleton': [':', 'x'],
                'name': 'mul_one'
            }
        ]

        rule_pairs, rich_rules = normalize_rules(rules)

        self.assertEqual(len(rule_pairs), 2)
        self.assertEqual(len(rich_rules), 2)
        # Should be converted to rule pairs
        self.assertEqual(rule_pairs[0], [['+', ['?', 'x'], 0], [':', 'x']])
        self.assertEqual(rule_pairs[1], [['*', ['?', 'x'], 1], [':', 'x']])
        # Rich rules should have metadata
        self.assertEqual(rich_rules[0].name, 'add_zero')
        self.assertEqual(rich_rules[1].name, 'mul_one')

    def test_normalize_mixed_formats(self):
        """Test normalizing mixed rule formats."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],  # List pair
            {
                'pattern': ['*', ['?', 'x'], 1],
                'skeleton': [':', 'x'],
                'name': 'mul_one'
            }  # Dict
        ]

        rule_pairs, rich_rules = normalize_rules(rules)

        self.assertEqual(len(rule_pairs), 2)
        self.assertEqual(rule_pairs[0], [['+', ['?', 'x'], 0], [':', 'x']])
        self.assertEqual(rule_pairs[1], [['*', ['?', 'x'], 1], [':', 'x']])
        # First should have no name, second should have name
        self.assertIsNone(rich_rules[0].name)
        self.assertEqual(rich_rules[1].name, 'mul_one')

    def test_normalize_preserves_rule_semantics(self):
        """Test that normalization preserves the rule semantics."""
        original_rules = [
            {
                'pattern': ['+', ['+', ['?', 'a'], ['?', 'b']], ['?', 'c']],
                'skeleton': ['+', [':', 'a'], ['+', [':', 'b'], [':', 'c']]],
                'name': 'associativity',
                'description': 'Addition is associative'
            }
        ]

        rule_pairs, rich_rules = normalize_rules(original_rules)

        self.assertEqual(len(rule_pairs), 1)
        self.assertEqual(rule_pairs[0][0], ['+', ['+', ['?', 'a'], ['?', 'b']], ['?', 'c']])
        self.assertEqual(rule_pairs[0][1], ['+', [':', 'a'], ['+', [':', 'b'], [':', 'c']]])
        self.assertEqual(rich_rules[0].name, 'associativity')
        self.assertEqual(rich_rules[0].description, 'Addition is associative')


class TestRichRuleIntegration(unittest.TestCase):
    """Integration tests for RichRule with actual rule files."""

    def test_load_algebra_rules_rich(self):
        """Test loading algebra_rules_rich.py if it exists."""
        try:
            from xtk.rules import algebra_rules_rich

            # Check that rules are defined
            rules = algebra_rules_rich.algebra_rules_rich
            self.assertIsNotNone(rules)
            self.assertIsInstance(rules, list)

            # Check that at least some rules are dicts with metadata
            has_dict_rule = any(isinstance(r, dict) for r in rules)
            self.assertTrue(has_dict_rule, "Should have at least one dict rule with metadata")

            # Test normalization works
            rule_pairs, rich_rules = normalize_rules(rules)
            self.assertIsInstance(rule_pairs, list)
            self.assertIsInstance(rich_rules, list)
            self.assertTrue(all(isinstance(r, list) and len(r) == 2 for r in rule_pairs))

        except ImportError:
            self.skipTest("algebra_rules_rich module not found")

    def test_load_deriv_rules_rich(self):
        """Test loading deriv_rules_rich.py if it exists."""
        try:
            from xtk.rules import deriv_rules_rich

            # Check that rules are defined - use deriv_rules_rich as the exported name
            rules = deriv_rules_rich.deriv_rules_rich
            self.assertIsNotNone(rules)
            self.assertIsInstance(rules, list)

            # Test normalization works
            rule_pairs, rich_rules = normalize_rules(rules)
            self.assertIsInstance(rule_pairs, list)
            self.assertIsInstance(rich_rules, list)

        except ImportError:
            self.skipTest("deriv_rules_rich module not found")


if __name__ == '__main__':
    unittest.main()
