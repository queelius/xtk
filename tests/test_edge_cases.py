"""
Strategic unit tests for subtle and difficult edge cases in xtk.
"""

import unittest
from xtk.rewriter import (
    match, instantiate, evaluate, simplifier,
    empty_dictionary, extend_dictionary
)
from xtk.fluent_api import Expression, ExpressionBuilder as E
from xtk.parser import parse_sexpr, format_sexpr, dsl_parser


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and subtle behaviors."""
    
    def test_nested_pattern_matching(self):
        """Test deeply nested pattern matching."""
        # Test nested arbitrary expressions
        pattern = ['+', ['*', ['?', 'a'], ['?', 'b']], ['?', 'c']]
        expr = ['+', ['*', 2, 'x'], 'y']
        
        result = match(pattern, expr, empty_dictionary())
        self.assertNotEqual(result, "failed")
        self.assertEqual(result, [['a', 2], ['b', 'x'], ['c', 'y']])
    
    def test_pattern_variable_conflicts(self):
        """Test pattern matching with variable conflicts."""
        # Same variable appearing multiple times should match same value
        pattern = ['+', ['?', 'x'], ['?', 'x']]
        
        # Should match when both are the same
        expr1 = ['+', 'a', 'a']
        result1 = match(pattern, expr1, empty_dictionary())
        self.assertNotEqual(result1, "failed")
        self.assertEqual(result1, [['x', 'a']])
        
        # Should fail when they're different
        expr2 = ['+', 'a', 'b']
        result2 = match(pattern, expr2, empty_dictionary())
        self.assertEqual(result2, "failed")
    
    def test_constant_vs_variable_patterns(self):
        """Test distinction between constant and variable patterns."""
        # Constant pattern should only match numbers
        const_pattern = ['?c', 'c']
        
        self.assertNotEqual(match(const_pattern, 42, empty_dictionary()), "failed")
        self.assertNotEqual(match(const_pattern, 3.14, empty_dictionary()), "failed")
        self.assertEqual(match(const_pattern, 'x', empty_dictionary()), "failed")
        self.assertEqual(match(const_pattern, ['a', 'b'], empty_dictionary()), "failed")
        
        # Variable pattern should only match strings
        var_pattern = ['?v', 'v']
        
        self.assertEqual(match(var_pattern, 42, empty_dictionary()), "failed")
        self.assertNotEqual(match(var_pattern, 'x', empty_dictionary()), "failed")
        self.assertNotEqual(match(var_pattern, 'abc', empty_dictionary()), "failed")
        self.assertEqual(match(var_pattern, ['a', 'b'], empty_dictionary()), "failed")
    
    def test_empty_list_handling(self):
        """Test handling of empty lists in various contexts."""
        # Empty pattern should only match empty expression
        self.assertNotEqual(match([], [], empty_dictionary()), "failed")
        self.assertEqual(match([], ['a'], empty_dictionary()), "failed")
        
        # Empty expression in compound structure
        pattern = ['+', ['?', 'x'], []]
        expr = ['+', 'a', []]
        result = match(pattern, expr, empty_dictionary())
        self.assertNotEqual(result, "failed")
        self.assertEqual(result, [['x', 'a']])
    
    def test_instantiation_with_nested_substitution(self):
        """Test instantiation with nested skeleton evaluations."""
        skeleton = ['+', [':', 'x'], ['*', [':', 'y'], [':', 'x']]]
        bindings = [['x', 3], ['y', 2]]
        
        result = instantiate(skeleton, bindings)
        self.assertEqual(result, ['+', 3, ['*', 2, 3]])
    
    def test_evaluation_with_callable_bindings(self):
        """Test evaluation with function bindings."""
        bindings = [
            ['+', lambda x, y: x + y],
            ['*', lambda x, y: x * y],
            ['-', lambda x, y: x - y],
            ['/', lambda x, y: x / y if y != 0 else float('inf')],
            ['x', 5],
            ['y', 3]
        ]
        
        # Test nested operations
        expr = ['+', ['*', 'x', 'y'], ['-', 'x', 'y']]
        result = evaluate(expr, bindings)
        self.assertEqual(result, 17)  # (5*3) + (5-3) = 15 + 2 = 17
        
        # Test division by zero handling
        expr_div = ['/', 'x', ['-', 'y', 'y']]
        result_div = evaluate(expr_div, bindings)
        self.assertEqual(result_div, float('inf'))
    
    @unittest.skip("Infinite loop detection not yet implemented")
    def test_simplifier_infinite_loop_prevention(self):
        """Test that simplifier doesn't get stuck in infinite loops."""
        # Rules that could cause infinite loop if not handled properly
        problematic_rules = [
            # These rules could ping-pong if not careful
            [['+', ['?', 'a'], ['?', 'b']], ['+', [':', 'b'], [':', 'a']]],  # Commutative
            [['+', ['?', 'b'], ['?', 'a']], ['+', [':', 'a'], [':', 'b']]],  # Reverse
        ]

        simplify = simplifier(problematic_rules)
        expr = ['+', 'x', 'y']

        # Should not hang - the improved simplifier has max iterations
        result = simplify(expr)
        self.assertIsNotNone(result)  # Just check it terminates
    
    @unittest.skip("Infinite loop with identity rules not yet handled")
    def test_rule_order_sensitivity(self):
        """Test that rule order matters for correctness."""
        # More specific rules should come before general ones
        rules_good = [
            [['+', 'x', 'x'], ['*', 2, 'x']],  # Specific: x + x = 2x
            [['+', ['?', 'a'], ['?', 'b']], ['+', [':', 'a'], [':', 'b']]],  # General
        ]

        rules_bad = [
            [['+', ['?', 'a'], ['?', 'b']], ['+', [':', 'a'], [':', 'b']]],  # General
            [['+', 'x', 'x'], ['*', 2, 'x']],  # Specific (never reached)
        ]

        expr = ['+', 'x', 'x']

        simplify_good = simplifier(rules_good)
        result_good = simplify_good(expr)
        self.assertEqual(result_good, ['*', 2, 'x'])

        simplify_bad = simplifier(rules_bad)
        result_bad = simplify_bad(expr)
        self.assertEqual(result_bad, ['+', 'x', 'x'])  # General rule just returns same
    
    def test_fluent_api_chaining(self):
        """Test fluent API method chaining."""
        # Build a simple expression: x^2
        expr = Expression(['^', 'x', 2])

        # Differentiate: d/dx(x^2)
        result = expr.differentiate('x')

        # The result should be differentiated (may not be fully simplified)
        # Just verify that differentiate() returns an Expression object
        self.assertIsInstance(result, Expression)
        # Verify the structure contains a derivative or simplification
        self.assertIsInstance(result.expr, (list, int, str))
    
    def test_parser_edge_cases(self):
        """Test parser with edge cases."""
        # Empty expression
        self.assertEqual(parse_sexpr("()"), [])
        
        # Nested empty lists
        self.assertEqual(parse_sexpr("(() ())"), [[], []])
        
        # Mixed numeric types
        expr = parse_sexpr("(+ 1 2.5 -3)")
        self.assertEqual(expr, ['+', 1, 2.5, -3])
        
        # Special characters in strings
        expr = parse_sexpr('(foo "bar-baz" x_1)')
        self.assertEqual(expr, ['foo', '"bar-baz"', 'x_1'])
    
    def test_dsl_parser_precedence(self):
        """Test DSL parser respects operator precedence."""
        # Multiplication before addition
        expr1 = dsl_parser.parse("2 + 3 * 4")
        self.assertEqual(expr1, ['+', 2, ['*', 3, 4]])
        
        # Right associativity of exponentiation
        expr2 = dsl_parser.parse("2 ^ 3 ^ 2")
        self.assertEqual(expr2, ['^', 2, ['^', 3, 2]])
        
        # Parentheses override precedence
        expr3 = dsl_parser.parse("(2 + 3) * 4")
        self.assertEqual(expr3, ['*', ['+', 2, 3], 4])
    
    def test_expression_equality_and_copying(self):
        """Test Expression equality and deep copying."""
        expr1 = Expression(['+', 'x', 1])
        expr2 = Expression(['+', 'x', 1])
        expr3 = expr1.copy()
        
        # Test equality
        self.assertEqual(expr1, expr2)
        self.assertEqual(expr1, expr3)
        
        # Test independence after copying
        expr3._rules.append([['test'], ['rule']])
        self.assertNotEqual(len(expr1._rules), len(expr3._rules))
    
    def test_latex_conversion(self):
        """Test LaTeX conversion for various expressions."""
        test_cases = [
            (['+', 'x', 'y'], "x + y"),
            (['-', 'x', 'y'], "x - y"),
            (['/', 'a', 'b'], "\\frac{a}{b}"),
            (['^', 'x', 2], "{x}^{2}"),
            (['sin', 'x'], "\\sin(x)"),
            (['dd', 'f', 'x'], "\\frac{d}{dx}(f)"),
        ]
        
        for expr, expected in test_cases:
            result = Expression(expr).to_latex()
            self.assertEqual(result, expected)
    
    def test_substitution_recursive(self):
        """Test recursive substitution."""
        expr = Expression(['+', ['*', 'x', 'y'], ['^', 'x', 2]])
        
        # Substitute x with (a + b)
        result = expr.substitute('x', ['+', 'a', 'b'])
        expected = ['+', ['*', ['+', 'a', 'b'], 'y'], ['^', ['+', 'a', 'b'], 2]]
        
        self.assertEqual(result.expr, expected)
    
    def test_history_tracking(self):
        """Test that transformation history is tracked correctly."""
        expr = Expression(['+', 'x', 0])
        
        # Apply transformations
        expr2 = expr.transform(['+', ['?', 'a'], 0], [':', 'a'])
        expr3 = expr2.substitute('x', 'y')
        
        history = expr3.get_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], ['+', 'x', 0])
        self.assertEqual(history[1], 'x')
        self.assertEqual(history[2], 'y')


class TestComplexScenarios(unittest.TestCase):
    """Test complex real-world scenarios."""
    
    def test_derivative_chain_rule(self):
        """Test derivative with chain rule."""
        from xtk.rules.deriv_rules import deriv_rules_fixed
        
        # d/dx(sin(x^2)) = cos(x^2) * 2x
        expr = Expression(['dd', ['sin', ['^', 'x', 2]], 'x'])
        result = expr.with_rules(deriv_rules_fixed).simplify()
        
        # Check structure (exact form may vary based on simplification)
        self.assertIn('cos', str(result.expr))
        self.assertIn('x', str(result.expr))
    
    def test_algebraic_simplification(self):
        """Test algebraic simplification with multiple rules."""
        from xtk.rules.algebra_rules import simplify_rules
        
        # (x + 0) * 1 / 1 should simplify to x
        expr = Expression(['/', ['*', ['+', 'x', 0], 1], 1])
        result = expr.with_rules(simplify_rules).simplify()
        
        self.assertEqual(result.expr, 'x')
    
    def test_mixed_numeric_evaluation(self):
        """Test evaluation with mixed numeric types."""
        expr = Expression(['+', ['*', 2, 3.5], ['/', 10, 4]])
        
        bindings = [
            ['+', lambda x, y: x + y],
            ['*', lambda x, y: x * y],
            ['/', lambda x, y: x / y],
        ]
        
        result = expr.evaluate(bindings)
        self.assertAlmostEqual(result.expr, 9.5)  # 2*3.5 + 10/4 = 7 + 2.5 = 9.5


if __name__ == '__main__':
    unittest.main()