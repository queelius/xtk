import unittest
import logging
from xtk.rewriter import simplifier

# Disable debug logging to prevent recursion issues
logging.basicConfig(level=logging.ERROR)

class TestSimplifierFixed(unittest.TestCase):
    """Fixed test suite for the simplifier function."""

    def test_simplify_no_rules(self):
        """Test simplifier with no rules."""
        rules = []
        expression = ['+', 3, 4]
        simplify = simplifier(rules, constant_folding=False)
        result = simplify(expression)
        self.assertEqual(result, ['+', 3, 4],
                        "Simplifier with no rules and constant folding disabled should return the input unchanged.")

    def test_simplify_identity_rules(self):
        """Test simplifier with identity rules."""
        rules = [
            # x + 0 = x
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['+', 0, ['?', 'x']], [':', 'x']],
            # x * 1 = x
            [['*', ['?', 'x'], 1], [':', 'x']],
            [['*', 1, ['?', 'x']], [':', 'x']],
            # x * 0 = 0
            [['*', ['?', 'x'], 0], 0],
            [['*', 0, ['?', 'x']], 0],
        ]

        # Test x + 0
        expression = ['+', 'x', 0]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 'x', "x + 0 should simplify to x")

        # Test 0 + x
        expression = ['+', 0, 'y']
        result = simplify(expression)
        self.assertEqual(result, 'y', "0 + y should simplify to y")

        # Test x * 1
        expression = ['*', 'z', 1]
        result = simplify(expression)
        self.assertEqual(result, 'z', "z * 1 should simplify to z")

        # Test x * 0
        expression = ['*', 'w', 0]
        result = simplify(expression)
        self.assertEqual(result, 0, "w * 0 should simplify to 0")

    def test_simplify_nested_with_identities(self):
        """Test simplifier with nested expressions using identity rules."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['+', 0, ['?', 'x']], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']],
            [['*', 1, ['?', 'x']], [':', 'x']],
            [['*', ['?', 'x'], 0], 0],
            [['*', 0, ['?', 'x']], 0],
        ]

        # Test nested: (x + 0) * 1
        expression = ['*', ['+', 'x', 0], 1]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 'x', "(x + 0) * 1 should simplify to x")

        # Test nested: (x * 1) + 0
        expression = ['+', ['*', 'x', 1], 0]
        result = simplify(expression)
        self.assertEqual(result, 'x', "(x * 1) + 0 should simplify to x")

    def test_simplify_variable_patterns(self):
        """Test simplifier with variable-specific patterns."""
        rules = [
            # Only match variables, not constants
            [['+', ['?v', 'v1'], 0], [':', 'v1']],
            [['+', 0, ['?v', 'v1']], [':', 'v1']],
        ]

        # Should match - 'x' is a variable
        expression = ['+', 'x', 0]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 'x', "x + 0 should simplify to x")

        # Should NOT match variable pattern - 3 is a constant
        # But constant folding will evaluate it to 3 anyway
        expression = ['+', 3, 0]
        result = simplify(expression)
        self.assertEqual(result, 3, "3 + 0 evaluates to 3 via constant folding")

    def test_simplify_constant_patterns(self):
        """Test simplifier with constant-specific patterns."""
        rules = [
            # Only match constants
            [['*', ['?c', 'c1'], 0], 0],
        ]

        # Should match - 5 is a constant
        expression = ['*', 5, 0]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 0, "5 * 0 should simplify to 0")

        # Should NOT match - 'x' is a variable
        expression = ['*', 'x', 0]
        result = simplify(expression)
        self.assertEqual(result, ['*', 'x', 0], "x * 0 should not match constant pattern")

    def test_simplify_with_multiple_applicable_rules(self):
        """Test that first matching rule is applied."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],  # First rule
            [['+', ['?', 'x'], ['?', 'y']], ['custom', [':', 'x'], [':', 'y']]],  # Second rule
        ]

        # First rule should match
        expression = ['+', 'x', 0]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 'x', "First matching rule should be applied")

    def test_simplify_complex_nested_structure(self):
        """Test simplifier with complex nested structures."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['+', 0, ['?', 'x']], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']],
            [['*', 1, ['?', 'x']], [':', 'x']],
            [['*', ['?', 'x'], 0], 0],
            [['*', 0, ['?', 'x']], 0],
        ]

        # Complex nested: ((x + 0) * 1) + (y * 0)
        expression = ['+', ['*', ['+', 'x', 0], 1], ['*', 'y', 0]]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 'x', "Complex nested expression should simplify to x")

    def test_simplify_with_empty_expression(self):
        """Test simplifier with an empty expression."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
        ]
        expression = []
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, [], "Empty expression should remain empty")

    def test_simplify_double_negative(self):
        """Test simplifier with double negative pattern."""
        rules = [
            # Double negative cancels out
            [['-', 0, ['-', 0, ['?', 'x']]], [':', 'x']],
        ]

        expression = ['-', 0, ['-', 0, 'x']]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 'x', "Double negative should cancel out")

    def test_simplify_power_rules(self):
        """Test simplifier with power rules."""
        rules = [
            # x^0 = 1
            [['^', ['?', 'x'], 0], 1],
            # x^1 = x
            [['^', ['?', 'x'], 1], [':', 'x']],
            # 0^x = 0 (assuming x != 0)
            [['^', 0, ['?', 'x']], 0],
            # 1^x = 1
            [['^', 1, ['?', 'x']], 1],
        ]

        # Test x^0 = 1
        expression = ['^', 'x', 0]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 1, "x^0 should simplify to 1")

        # Test x^1 = x
        expression = ['^', 'y', 1]
        result = simplify(expression)
        self.assertEqual(result, 'y', "y^1 should simplify to y")

        # Test 0^x = 0
        expression = ['^', 0, 'z']
        result = simplify(expression)
        self.assertEqual(result, 0, "0^z should simplify to 0")

        # Test 1^x = 1
        expression = ['^', 1, 'w']
        result = simplify(expression)
        self.assertEqual(result, 1, "1^w should simplify to 1")

    def test_simplify_distributive_property(self):
        """Test simplifier with distributive property pattern."""
        rules = [
            # a * (x + y) = a*x + a*y
            [['*', ['?', 'a'], ['+', ['?', 'x'], ['?', 'y']]],
             ['+', ['*', [':', 'a'], [':', 'x']], ['*', [':', 'a'], [':', 'y']]]],
        ]

        expression = ['*', 'a', ['+', 'x', 'y']]
        simplify = simplifier(rules)
        result = simplify(expression)
        expected = ['+', ['*', 'a', 'x'], ['*', 'a', 'y']]
        self.assertEqual(result, expected, "Distributive property should work")

    def test_simplify_no_infinite_recursion(self):
        """Test that simplifier doesn't cause infinite recursion with circular rules."""
        # These rules are designed to terminate rather than loop infinitely
        rules = [
            # Only apply to nested additions, not to the result
            [['+', ['+', ['?', 'x'], ['?', 'y']], ['?', 'z']],
             ['+', [':', 'x'], ['+', [':', 'y'], [':', 'z']]]],
        ]

        expression = ['+', ['+', 'a', 'b'], 'c']
        simplify = simplifier(rules)
        result = simplify(expression)
        expected = ['+', 'a', ['+', 'b', 'c']]
        self.assertEqual(result, expected, "Associativity rule should work without recursion")

if __name__ == '__main__':
    unittest.main()