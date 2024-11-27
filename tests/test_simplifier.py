import unittest
from xtoolkit.rewriter import simplifier

class TestSimplifier(unittest.TestCase):

    def test_simplify_no_rules(self):
        """Test simplifier with no rules."""
        rules = []
        expression = ['+', 3, 4]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, ['+', 3, 4], "Simplifier with no rules should return the input unchanged.")

    def test_simplify_basic_rule(self):
        """Test simplifier with a basic rule."""
        def adder(a, b):
            return a + b
        

        # enable logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        rules = [
            # Simplification: addition by constants
            [
                ['+', ['?c', 'c1'], ['?c', 'c2']],
                [':', adder]
            ]
        ]
        expression = ['+', 3, 4]
        simplify = simplifier(rules)
        result = simplify(expression)
        result = simplify(result)
        print(f"Result: {result}")
        self.assertEqual(result, 7, "Simplifier should reduce ['+', 3, 4] to 7.")

    def test_simplify_recursive_rule_application(self):
        """Test recursive rule application."""
        rules = [
            [['+', ['?c', 'c1'], ['?c', 'c2']], [':', ['+', 'c1', 'c2']]],
            [['+', 0, ['?', 'x']], ['?', 'x']],
            [['+', ['?', 'x'], 0], ['?', 'x']]
        ]
        expression = ['+', ['+', 3, 4], 0]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 7, "Simplifier should reduce nested additions with rules.")

    def test_simplify_nested_expression(self):
        """Test simplifier with a nested expression."""
        rules = [
            [['+', ['?c', 'c1'], ['?c', 'c2']], [':', ['+', 'c1', 'c2']]],
            [['*', ['?c', 'c1'], ['?c', 'c2']], [':', ['*', 'c1', 'c2']]]
        ]
        expression = ['+', 3, ['*', 2, 5]]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 13, "Simplifier should reduce ['+', 3, ['*', 2, 5]] to 13.")

    def test_simplify_with_variables(self):
        """Test simplifier with variables."""
        rules = [
            [['+', ['?v', 'v1'], 0], ['?', 'v1']],
            [['+', 0, ['?v', 'v1']], ['?', 'v1']],
            [['*', ['?v', 'v1'], 1], ['?', 'v1']],
            [['*', 1, ['?v', 'v1']], ['?', 'v1']],
            [['+', ['?c', 'c1'], ['?c', 'c2']], [':', ['+', 'c1', 'c2']]]
        ]
        expression = ['+', ['+', 'x', 0], 0]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, 'x', "Simplifier should simplify variables and constants together.")

    def test_simplify_with_non_matching_rule(self):
        """Test simplifier with a rule that doesn't match."""
        rules = [
            [['*', ['?c', 'c1'], ['?c', 'c2']], [':', ['*', 'c1', 'c2']]]
        ]
        expression = ['+', 3, 4]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, ['+', 3, 4], "Simplifier should leave expressions unchanged when no rules match.")

    def test_simplify_with_empty_expression(self):
        """Test simplifier with an empty expression."""
        rules = [
            [['+', ['?c', 'c1'], ['?c', 'c2']], [':', ['+', 'c1', 'c2']]]
        ]
        expression = []
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, [], "Simplifier should return an empty expression unchanged.")

    def test_simplify_with_recursive_structure(self):
        """Test simplifier with a complex recursive structure."""
        rules = [
            [['+', ['?v', 'x'], ['?v', 'x']], ['*', 2, ['?', 'x']]],
            [['*', ['?c', 'c1'], ['?c', 'c2']], [':', ['*', 'c1', 'c2']]],
            [['+', ['?c', 'c1'], ['?c', 'c2']], [':', ['+', 'c1', 'c2']]]
        ]
        expression = ['+', ['+', 'x', 'x'], ['*', 2, 5]]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, ['+', ['*', 2, 'x'], 10], "Simplifier should reduce recursive structures correctly.")

    def test_simplify_with_constants_and_variables(self):
        """Test simplifier mixing constants and variables."""
        rules = [
            [['+', ['?c', 'c1'], ['?c', 'c2']], [':', ['+', 'c1', 'c2']]],
            [['+', 0, ['?', 'x']], ['?', 'x']],
            [['*', ['?c', 'c1'], ['?c', 'c2']], [':', ['*', 'c1', 'c2']]],
        ]
        expression = ['+', 0, ['+', 3, ['*', 2, 'x']]]
        simplify = simplifier(rules)
        result = simplify(expression)
        self.assertEqual(result, ['+', 6, 'x'], "Simplifier should simplify constants and variables together.")

if __name__ == '__main__':
    unittest.main()
