"""
Comprehensive tests for the fluent API.
"""

import unittest
from copy import deepcopy

from xtk.fluent_api import (
    Expression, ExpressionBuilder, E, expr
)
from xtk.rewriter import empty_dictionary


class TestExpression(unittest.TestCase):
    """Test the Expression class."""
    
    def test_initialization(self):
        """Test Expression initialization."""
        # From list
        expr1 = Expression(['+', 'x', 1])
        self.assertEqual(expr1.expr, ['+', 'x', 1])
        
        # From string
        expr2 = Expression('x')
        self.assertEqual(expr2.expr, 'x')
        
        # From number
        expr3 = Expression(42)
        self.assertEqual(expr3.expr, 42)
    
    def test_string_representation(self):
        """Test string representations."""
        expr = Expression(['+', 'x', 'y'])
        
        # __repr__
        self.assertEqual(repr(expr), "Expression(['+', 'x', 'y'])")
        
        # __str__ and to_string
        self.assertEqual(str(expr), "(+ x y)")
        self.assertEqual(expr.to_string(), "(+ x y)")
    
    def test_equality(self):
        """Test equality comparison."""
        expr1 = Expression(['+', 'x', 1])
        expr2 = Expression(['+', 'x', 1])
        expr3 = Expression(['+', 'x', 2])
        
        # Expression to Expression
        self.assertEqual(expr1, expr2)
        self.assertNotEqual(expr1, expr3)
        
        # Expression to raw value
        self.assertEqual(expr1, ['+', 'x', 1])
        self.assertNotEqual(expr1, ['+', 'x', 2])
    
    def test_to_latex(self):
        """Test LaTeX conversion."""
        test_cases = [
            (['+', 'x', 'y'], "x + y"),
            (['-', 'x', 'y'], "x - y"),
            (['*', 'x', 'y'], "x \\cdot y"),
            (['/', 'x', 'y'], "\\frac{x}{y}"),
            (['^', 'x', 2], "{x}^{2}"),
            (['sin', 'x'], "\\sin(x)"),
            (['cos', 'x'], "\\cos(x)"),
            (['dd', 'f', 'x'], "\\frac{d}{dx}(f)"),
            (42, "42"),
            ('x', "x"),
        ]
        
        for expr_data, expected in test_cases:
            expr = Expression(expr_data)
            self.assertEqual(expr.to_latex(), expected)
    
    def test_to_latex_nested(self):
        """Test LaTeX conversion for nested expressions."""
        expr = Expression(['+', ['*', 'a', 'b'], ['/', 'c', 'd']])
        latex = expr.to_latex()
        self.assertIn("\\cdot", latex)
        self.assertIn("\\frac", latex)
    
    def test_copy(self):
        """Test deep copying."""
        expr1 = Expression(['+', 'x', 1])
        expr1._rules = [[['+', 'a', 0], 'a']]
        expr1._bindings = [['x', 5]]
        expr1._history = [['x']]
        
        expr2 = expr1.copy()
        
        # Should be equal but independent
        self.assertEqual(expr1.expr, expr2.expr)
        self.assertEqual(expr1._rules, expr2._rules)
        
        # Modify copy shouldn't affect original
        expr2.expr[2] = 2
        expr2._rules.append([['*', 'x', 1], 'x'])
        
        self.assertEqual(expr1.expr[2], 1)
        self.assertEqual(len(expr1._rules), 1)
    
    def test_with_rules(self):
        """Test adding rules."""
        expr = Expression(['+', 'x', 0])
        rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
        
        result = expr.with_rules(rules)
        
        # Should return self for chaining
        self.assertIs(result, expr)
        
        # Rules should be added
        self.assertEqual(expr._rules, rules)
        
        # Test adding more rules
        more_rules = [[['*', ['?', 'x'], 1], [':', 'x']]]
        expr.with_rules(more_rules)
        self.assertEqual(len(expr._rules), 2)
    
    def test_with_rule(self):
        """Test adding single rule."""
        expr = Expression(['+', 'x', 0])
        pattern = ['+', ['?', 'x'], 0]
        skeleton = [':', 'x']
        
        result = expr.with_rule(pattern, skeleton)
        
        self.assertIs(result, expr)
        self.assertEqual(expr._rules, [[pattern, skeleton]])
    
    def test_bind(self):
        """Test binding variables."""
        expr = Expression(['+', 'x', 'y'])
        
        result = expr.bind('x', 3)
        self.assertIs(result, expr)
        self.assertEqual(expr._bindings, [['x', 3]])
        
        # Test binding function
        expr.bind('+', lambda a, b: a + b)
        self.assertEqual(len(expr._bindings), 2)
        self.assertTrue(callable(expr._bindings[1][1]))
    
    def test_simplify(self):
        """Test simplification."""
        expr = Expression(['+', ['*', 'x', 1], 0])
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]
        
        result = expr.with_rules(rules).simplify()
        
        # Should return new Expression
        self.assertIsNot(result, expr)
        
        # Should be simplified
        self.assertEqual(result.expr, 'x')
        
        # Should preserve rules and add to history
        self.assertEqual(result._rules, rules)
        self.assertIn(['+', ['*', 'x', 1], 0], result._history)
    
    def test_simplify_no_rules(self):
        """Test simplification without rules."""
        expr = Expression(['+', 'x', 1])
        result = expr.simplify()
        
        # Should return a copy
        self.assertIsNot(result, expr)
        self.assertEqual(result.expr, expr.expr)
    
    def test_evaluate(self):
        """Test evaluation."""
        expr = Expression(['+', ['*', 'x', 2], 'y'])
        
        result = (expr
            .bind('x', 3)
            .bind('y', 4)
            .bind('+', lambda a, b: a + b)
            .bind('*', lambda a, b: a * b)
            .evaluate())
        
        self.assertEqual(result.expr, 10)  # 3*2 + 4 = 10
    
    def test_evaluate_without_bindings(self):
        """Test evaluation without sufficient bindings."""
        expr = Expression(['+', 'x', 'y'])
        result = expr.evaluate()
        
        # Should return expression unchanged if can't evaluate
        self.assertEqual(result.expr, ['+', 'x', 'y'])
    
    def test_match_pattern(self):
        """Test pattern matching."""
        expr = Expression(['+', 'a', 'a'])
        
        # Matching pattern
        pattern = ['+', ['?', 'x'], ['?', 'x']]
        bindings = expr.match_pattern(pattern)
        self.assertIsNotNone(bindings)
        self.assertEqual(bindings, [['x', 'a']])
        
        # Non-matching pattern
        pattern2 = ['-', ['?', 'x'], ['?', 'y']]
        bindings2 = expr.match_pattern(pattern2)
        self.assertIsNone(bindings2)
    
    def test_transform(self):
        """Test transformation."""
        expr = Expression(['+', 'a', 'a'])
        pattern = ['+', ['?', 'x'], ['?', 'x']]
        skeleton = ['*', 2, [':', 'x']]
        
        result = expr.transform(pattern, skeleton)
        
        # Should return new Expression
        self.assertIsNot(result, expr)
        
        # Should be transformed
        self.assertEqual(result.expr, ['*', 2, 'a'])
        
        # Should add to history
        self.assertIn(['+', 'a', 'a'], result._history)
    
    def test_transform_no_match(self):
        """Test transformation with no match."""
        expr = Expression(['+', 'a', 'b'])
        pattern = ['+', ['?', 'x'], ['?', 'x']]
        skeleton = ['*', 2, [':', 'x']]
        
        result = expr.transform(pattern, skeleton)
        
        # Should return self when no match
        self.assertIs(result, expr)
    
    def test_differentiate(self):
        """Test differentiation."""
        expr = Expression(['^', 'x', 2])

        # Differentiate applies derivative rules and simplifies
        result = expr.differentiate('x')
        self.assertIsInstance(result, Expression)

        # d/dx(x^2) = 2*x^1 which simplifies to 2*x
        # The result should be a multiplication
        self.assertEqual(result.expr[0], '*')
        # Should contain the constant 2
        self.assertIn(2, result.expr)
    
    def test_substitute(self):
        """Test substitution."""
        expr = Expression(['+', 'x', ['^', 'x', 2]])
        
        result = expr.substitute('x', 'y')
        
        # Should return new Expression
        self.assertIsNot(result, expr)
        
        # Should substitute all occurrences
        self.assertEqual(result.expr, ['+', 'y', ['^', 'y', 2]])
    
    def test_substitute_nested(self):
        """Test nested substitution."""
        expr = Expression(['+', ['*', 'x', 'y'], ['-', 'x', 'z']])
        
        result = expr.substitute('x', ['+', 'a', 'b'])
        
        expected = ['+', ['*', ['+', 'a', 'b'], 'y'], ['-', ['+', 'a', 'b'], 'z']]
        self.assertEqual(result.expr, expected)
    
    def test_history_tracking(self):
        """Test that history is tracked correctly."""
        expr = Expression(['+', 'x', 0])
        
        # Apply transformations
        expr2 = expr.transform(['+', ['?', 'a'], 0], [':', 'a'])
        expr3 = expr2.substitute('x', 'y')
        
        history = expr3.get_history()
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], ['+', 'x', 0])
        self.assertEqual(history[1], 'x')
        self.assertEqual(history[2], 'y')
    
    def test_method_chaining(self):
        """Test fluent method chaining."""
        result = (Expression(['+', ['*', 'x', 1], 0])
            .with_rule(['+', ['?', 'x'], 0], [':', 'x'])
            .with_rule(['*', ['?', 'x'], 1], [':', 'x'])
            .simplify()
            .substitute('x', 'y'))
        
        self.assertEqual(result.expr, 'y')


class TestExpressionBuilder(unittest.TestCase):
    """Test the ExpressionBuilder class."""
    
    def test_constant(self):
        """Test constant creation."""
        expr = E.constant(42)
        self.assertIsInstance(expr, Expression)
        self.assertEqual(expr.expr, 42)
        
        expr2 = E.constant(3.14)
        self.assertEqual(expr2.expr, 3.14)
    
    def test_variable(self):
        """Test variable creation."""
        expr = E.variable('x')
        self.assertIsInstance(expr, Expression)
        self.assertEqual(expr.expr, 'x')
    
    def test_add(self):
        """Test addition."""
        expr = E.add('x', 'y', 'z')
        self.assertEqual(expr.expr, ['+', 'x', 'y', 'z'])
    
    def test_subtract(self):
        """Test subtraction."""
        expr = E.subtract('x', 'y')
        self.assertEqual(expr.expr, ['-', 'x', 'y'])
    
    def test_multiply(self):
        """Test multiplication."""
        expr = E.multiply(2, 'x', 'y')
        self.assertEqual(expr.expr, ['*', 2, 'x', 'y'])
    
    def test_divide(self):
        """Test division."""
        expr = E.divide('x', 'y')
        self.assertEqual(expr.expr, ['/', 'x', 'y'])
    
    def test_power(self):
        """Test exponentiation."""
        expr = E.power('x', 2)
        self.assertEqual(expr.expr, ['^', 'x', 2])
    
    def test_sin(self):
        """Test sine function."""
        expr = E.sin('x')
        self.assertEqual(expr.expr, ['sin', 'x'])
    
    def test_cos(self):
        """Test cosine function."""
        expr = E.cos('x')
        self.assertEqual(expr.expr, ['cos', 'x'])
    
    def test_exp(self):
        """Test exponential function."""
        expr = E.exp('x')
        self.assertEqual(expr.expr, ['exp', 'x'])
    
    def test_log(self):
        """Test logarithm function."""
        expr = E.log('x')
        self.assertEqual(expr.expr, ['log', 'x'])
    
    def test_derivative(self):
        """Test derivative creation."""
        expr = E.derivative(['^', 'x', 2], 'x')
        self.assertEqual(expr.expr, ['dd', ['^', 'x', 2], 'x'])
    
    def test_from_string(self):
        """Test parsing from string."""
        expr = E.from_string("(+ x y)")
        self.assertEqual(expr.expr, ['+', 'x', 'y'])
    
    def test_nested_building(self):
        """Test building nested expressions."""
        # (x + 1)^2
        expr = E.power(E.add('x', 1), 2)
        self.assertEqual(expr.expr, ['^', ['+', 'x', 1], 2])
        
        # sin(x*y)
        expr2 = E.sin(E.multiply('x', 'y'))
        self.assertEqual(expr2.expr, ['sin', ['*', 'x', 'y']])
    
    def test_builder_accepts_expressions(self):
        """Test that builder methods accept Expression objects."""
        x = E.variable('x')
        y = E.variable('y')
        
        # Should work with Expression objects
        expr = E.add(x, y)
        self.assertEqual(expr.expr, ['+', 'x', 'y'])


class TestShorthands(unittest.TestCase):
    """Test shorthand aliases."""
    
    def test_E_alias(self):
        """Test that E is an alias for ExpressionBuilder."""
        self.assertIs(E, ExpressionBuilder)
    
    def test_expr_alias(self):
        """Test that expr is an alias for Expression."""
        self.assertIs(expr, Expression)


class TestEdgeCasesFluentAPI(unittest.TestCase):
    """Test edge cases in the fluent API."""
    
    def test_empty_expression(self):
        """Test empty expression handling."""
        expr = Expression([])
        self.assertEqual(expr.to_string(), "()")
        self.assertEqual(expr.to_latex(), "()")
    
    def test_deeply_nested_expression(self):
        """Test deeply nested expression."""
        # Create deeply nested expression
        expr = 'x'
        for _ in range(10):
            expr = ['+', expr, 1]
        
        e = Expression(expr)
        string = e.to_string()
        
        # Should have many nested parentheses
        self.assertEqual(string.count('('), 10)
        self.assertEqual(string.count(')'), 10)
    
    def test_very_long_expression(self):
        """Test very long expression."""
        # Create expression with many terms
        terms = list(range(100))
        expr = Expression(['+'] + terms)
        
        string = expr.to_string()
        self.assertTrue(string.startswith('(+'))
        self.assertTrue(string.endswith(')'))
    
    def test_special_characters_in_variables(self):
        """Test special characters in variable names."""
        expr = Expression(['+', 'x_1', 'α', 'β'])
        string = expr.to_string()
        self.assertIn('x_1', string)
        self.assertIn('α', string)
        self.assertIn('β', string)
    
    def test_transform_with_empty_bindings(self):
        """Test transformation with empty bindings."""
        expr = Expression(['+', 'x', 'y'])
        pattern = ['+', ['?', 'a'], ['?', 'b']]
        skeleton = ['-', [':', 'a'], [':', 'b']]
        
        result = expr.transform(pattern, skeleton)
        self.assertEqual(result.expr, ['-', 'x', 'y'])
    
    def test_evaluate_with_partial_bindings(self):
        """Test evaluation with partial bindings."""
        expr = Expression(['+', ['*', 'x', 2], 'y'])
        
        # Only bind some values
        result = expr.bind('x', 3).bind('*', lambda a, b: a * b).evaluate()
        
        # Should partially evaluate
        # The multiplication should work, but addition shouldn't
        self.assertIsInstance(result.expr, list)
        self.assertEqual(result.expr[0], '+')
    
    def test_circular_substitution(self):
        """Test that substitution doesn't cause infinite recursion."""
        expr = Expression(['+', 'x', 'y'])
        
        # Substitute x with an expression containing x
        # This should just do one level of substitution
        result = expr.substitute('x', ['+', 'x', 1])
        
        self.assertEqual(result.expr, ['+', ['+', 'x', 1], 'y'])
    
    def test_history_limit(self):
        """Test that history doesn't grow unbounded."""
        expr = Expression('x')
        
        # Apply many transformations
        for i in range(1000):
            expr = expr.substitute('x', f'x{i}')
        
        history = expr.get_history()
        
        # History should exist and contain transformations
        self.assertGreater(len(history), 0)
        
        # Last item should be current expression
        self.assertEqual(history[-1], expr.expr)


class TestIntegrationFluentAPI(unittest.TestCase):
    """Integration tests for the fluent API."""
    
    def test_complete_workflow(self):
        """Test a complete symbolic computation workflow."""
        # Create an expression: (x + 1)^2
        expr = Expression(['^', ['+', 'x', 1], 2])

        # Add expansion rule
        expansion_rule = [
            ['^', ['+', ['?', 'a'], ['?', 'b']], 2],
            ['+', ['+', ['^', [':', 'a'], 2],
                       ['*', 2, ['*', [':', 'a'], [':', 'b']]]],
                  ['^', [':', 'b'], 2]]
        ]

        # Apply the workflow
        result = (expr
            .with_rules([expansion_rule])
            .simplify()
            .substitute('x', 'y'))

        # Check that it expanded and substituted
        # Should contain y somewhere in the expression
        self.assertIsInstance(result.expr, list)
        self.assertIn('y', str(result.expr))
    
    def test_algebraic_simplification_workflow(self):
        """Test algebraic simplification workflow."""
        from xtk.rules.algebra_rules import simplify_rules
        
        # Complex expression that should simplify
        expr = Expression(['+', ['*', 'x', 0], ['+', ['*', 'y', 1], 0]])
        
        result = expr.with_rules(simplify_rules).simplify()
        
        # Should simplify to just 'y'
        self.assertEqual(result.expr, 'y')
    
    def test_symbolic_to_numeric_workflow(self):
        """Test symbolic to numeric evaluation."""
        # Create symbolic expression: x*x + 2*x + 1
        expr = Expression(['+', ['*', 'x', 'x'], ['*', 2, 'x'], 1])

        # Evaluate at x = 3
        result = (expr
            .bind('x', 3)
            .bind('+', lambda *args: sum(args))
            .bind('*', lambda a, b: a * b)
            .evaluate())

        # x^2 + 2x + 1 at x=3 should be 9 + 6 + 1 = 16
        self.assertEqual(result.expr, 16)


class TestASCIIRendering(unittest.TestCase):
    """Test ASCII art rendering functionality."""

    def test_simple_fraction(self):
        """Test rendering a simple fraction."""
        expr = Expression(['/', 'x', 'y'])
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 1)  # Should have multiple lines
        # Should contain both x and y
        result_str = '\n'.join(result)
        self.assertIn('x', result_str)
        self.assertIn('y', result_str)
        # Should contain a horizontal line
        self.assertTrue(any('─' in line for line in result))

    def test_numeric_fraction(self):
        """Test rendering a numeric fraction."""
        expr = Expression(['/', 1, 2])
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        result_str = '\n'.join(result)
        self.assertIn('1', result_str)
        self.assertIn('2', result_str)

    def test_power_expression(self):
        """Test rendering power/exponent expressions."""
        expr = Expression(['^', 'x', 2])
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        result_str = '\n'.join(result)
        self.assertIn('x', result_str)
        # Power is rendered as superscript (x²) or contains the exponent
        self.assertTrue('²' in result_str or '2' in result_str)

    def test_derivative_expression(self):
        """Test rendering derivative expressions."""
        expr = Expression(['dd', ['^', 'x', 2], 'x'])
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        result_str = '\n'.join(result)
        # Should contain d/dx notation or similar
        self.assertTrue(len(result_str) > 0)

    def test_complex_fraction(self):
        """Test rendering complex nested fraction."""
        expr = Expression(['/', ['+', 'x', 1], ['-', 'y', 2]])
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 3)  # Numerator, line, denominator
        result_str = '\n'.join(result)
        self.assertIn('x', result_str)
        self.assertIn('y', result_str)

    def test_simple_variable(self):
        """Test rendering simple variable."""
        expr = Expression('x')
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'x')

    def test_simple_number(self):
        """Test rendering simple number."""
        expr = Expression(42)
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], '42')

    def test_addition_expression(self):
        """Test rendering addition expression."""
        expr = Expression(['+', 'x', 'y'])
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        result_str = '\n'.join(result)
        # Should contain x, y, and + in some form
        self.assertIn('x', result_str)
        self.assertIn('y', result_str)

    def test_nested_power(self):
        """Test rendering nested power expression."""
        expr = Expression(['^', ['^', 'x', 2], 3])
        result = expr.to_ascii()

        self.assertIsInstance(result, list)
        result_str = '\n'.join(result)
        self.assertIn('x', result_str)


if __name__ == '__main__':
    unittest.main()