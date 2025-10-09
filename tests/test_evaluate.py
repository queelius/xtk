import unittest
from xtk.rewriter import evaluate
import logging

# Disable logging for the tests
logging.disable(logging.CRITICAL)

class TestEvaluate(unittest.TestCase):

    def test_evaluate_constant(self):
        # Test evaluating a constant
        expression = 42
        result = evaluate(expression, [])
        self.assertEqual(result, 42, "Evaluating a constant should return the constant itself.")

    def test_1(self):
        arithmetic_dict = [
            ['+', lambda a, b: a + b],
            ['-', lambda a, b: a - b],
            ['*', lambda a, b: a * b],
            ['/', lambda a, b: a / b]
        ]

        expression = ['+', 3, 4]
        result = evaluate(expression, arithmetic_dict)
        # Expected: 7

        nested_expression = ['+', 3, ['*', 2, 3]]
        result = evaluate(nested_expression, arithmetic_dict)
        # Expected: 9        
        self.assertEqual(result, 9, "Evaluating ['+', 3, ['*', 2, 3]] should return 9.")

    def test_evaluate_variable(self):
        # Test evaluating a variable with a given dictionary
        expression = 'x'
        dict = [['x', 10]]
        result = evaluate(expression, dict)
        self.assertEqual(result, 10, "Evaluating a variable should return its value from the dictionary.")

    def test_evaluate_simple_expression(self):
        # Test evaluating a simple arithmetic expression
        expression = ['+', 3, 4]
        operators = [
            ['+', lambda a, b: a + b]
        ]
        result = evaluate(expression, operators)
        self.assertEqual(result, 7, "Evaluating ['+', 3, 4] should return 7.")

    def test_evaluate_nested_expression(self):
        # Test evaluating a nested arithmetic expression
        expression = ['+', 3, ['*', 2, 5]]
        operators = [
            ['+', lambda a, b: a + b],
            ['*', lambda a, b: a * b]
        ]
        result = evaluate(expression, operators)
        self.assertEqual(result, 13, "Evaluating ['+', 3, ['*', 2, 5]] should return 13.")

    def test_evaluate_expression_with_variables(self):
        # Test evaluating an expression with variables
        expression = ['*', 'x', ['+', 'y', 2]]
        dict = [
            ['x', 3],
            ['y', 4],
            ['+', lambda a, b: a + b],
            ['*', lambda a, b: a * b]
        ]
        result = evaluate(expression, dict)
        self.assertEqual(result, 18, "Evaluating ['*', 'x', ['+', 'y', 2]] with x=3, y=4 should return 18.")

    def test_evaluate_expression_with_missing_variable(self):
        # Test evaluating an expression with a missing variable
        # The evaluate function returns the expression unchanged if variables
        # cannot be resolved (partial evaluation)
        expression = ['+', 'x', 5]
        dict = [
            ['+', lambda a, b: a + b]
        ]
        # Evaluation with missing variable returns expression unchanged
        result = evaluate(expression, dict)
        # Since 'x' is not defined, the expression is returned as-is
        self.assertEqual(result, ['+', 'x', 5])

    def test_evaluate_expression_with_non_callable_operator(self):
        # Test evaluating an expression with a non-callable operator
        expression = ['unknown_op', 3, 4]
        dict = []
        result = evaluate(expression, dict)
        self.assertEqual(result, expression, "Evaluating an expression with a non-callable operator should return the expression itself.")

    def test_evaluate_deeply_nested_expression(self):
        # Test evaluating a deeply nested expression
        expression = ['+', ['*', ['-', 10, 2], 3], ['/', 20, 5]]
        dict = [
            ['+', lambda a, b: a + b],
            ['-', lambda a, b: a - b],
            ['*', lambda a, b: a * b],
            ['/', lambda a, b: a / b]
        ]
        result = evaluate(expression, dict)
        expected_result = ((10 - 2) * 3) + (20 / 5)
        self.assertEqual(result, expected_result, "Evaluating a deeply nested expression should return the correct result.")

    def test_evaluate_with_function_in_expression(self):
        # Test evaluating an expression that includes a function
        def square(x):
            return x * x

        expression = ['square', 5]
        dict = [['square', square]]
        result = evaluate(expression, dict)
        self.assertEqual(result, 25, "Evaluating ['square', 5] should return 25.")

    def test_evaluate_expression_with_constants_and_variables(self):
        # Test evaluating an expression that mixes constants and variables
        expression = ['+', ['*', 'x', 2], 5]
        dict = [
            ['x', 4],
            ['+', lambda a, b: a + b],
            ['*', lambda a, b: a * b]
        ]
        result = evaluate(expression, dict)
        self.assertEqual(result, 13, "Evaluating ['+', ['*', 'x', 2], 5] with x=4 should return 13.")

    def test_evaluate_expression_with_no_operators(self):
        # Test evaluating an expression with no operators in the dictionary
        expression = ['+', 3, 4]
        operators = {}
        result = evaluate(expression, operators)
        self.assertEqual(result, expression, "Without operators, the expression should remain unchanged.")

if __name__ == '__main__':
    unittest.main()
