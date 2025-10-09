"""Comprehensive test suite for rewriter.py module."""

import unittest
import logging
from xtk.rewriter import (
    car, cdr, match, instantiate, evaluate, simplifier,
    atom, compound, constant, variable, empty_dictionary,
    extend_dictionary, lookup, arbitrary_constant,
    arbitrary_variable, arbitrary_expression, skeleton_evaluation,
    eval_exp, pattern, skeleton, variable_name, null, cons
)

# Disable debug logging for tests
logging.basicConfig(level=logging.ERROR)


class TestBasicListOperations(unittest.TestCase):
    """Test basic list operations: car, cdr, cons, null."""

    def test_car_valid_list(self):
        """Test car with valid non-empty list."""
        self.assertEqual(car([1, 2, 3]), 1)
        self.assertEqual(car(['a', 'b']), 'a')
        self.assertEqual(car([[1, 2], 3]), [1, 2])

    def test_car_empty_list(self):
        """Test car with empty list raises error."""
        with self.assertRaises(ValueError) as cm:
            car([])
        self.assertIn("empty list", str(cm.exception))

    def test_car_non_list(self):
        """Test car with non-list raises error."""
        with self.assertRaises(TypeError) as cm:
            car(42)
        self.assertIn("must be a list", str(cm.exception))

    def test_cdr_valid_list(self):
        """Test cdr with valid list."""
        self.assertEqual(cdr([1, 2, 3]), [2, 3])
        self.assertEqual(cdr(['a']), [])
        self.assertEqual(cdr([[1, 2], 3, 4]), [3, 4])

    def test_cdr_empty_list(self):
        """Test cdr with empty list returns empty list."""
        self.assertEqual(cdr([]), [])

    def test_cdr_non_list(self):
        """Test cdr with non-list raises error."""
        with self.assertRaises(TypeError) as cm:
            cdr("not a list")
        self.assertIn("must be a list", str(cm.exception))

    def test_cons(self):
        """Test cons operation."""
        self.assertEqual(cons(1, [2, 3]), [1, 2, 3])
        self.assertEqual(cons('a', []), ['a'])
        self.assertEqual(cons([1, 2], [[3, 4]]), [[1, 2], [3, 4]])

    def test_null(self):
        """Test null predicate."""
        self.assertTrue(null([]))
        self.assertFalse(null([1]))
        self.assertFalse(null([[]]))
        self.assertFalse(null(0))
        self.assertFalse(null(""))


class TestPredicates(unittest.TestCase):
    """Test predicate functions."""

    def test_atom(self):
        """Test atom predicate."""
        # Constants and variables are atoms
        self.assertTrue(atom(42))
        self.assertTrue(atom(3.14))
        self.assertTrue(atom('x'))
        self.assertTrue(atom('variable'))

        # Lists are not atoms
        self.assertFalse(atom([]))
        self.assertFalse(atom([1, 2]))
        self.assertFalse(atom(['+', 'x', 1]))

    def test_compound(self):
        """Test compound predicate."""
        self.assertTrue(compound([]))
        self.assertTrue(compound([1]))
        self.assertTrue(compound(['+', 'x', 1]))

        self.assertFalse(compound(42))
        self.assertFalse(compound('x'))

    def test_constant(self):
        """Test constant predicate."""
        self.assertTrue(constant(42))
        self.assertTrue(constant(3.14))
        self.assertTrue(constant(0))
        self.assertTrue(constant(-5))

        self.assertFalse(constant('x'))
        self.assertFalse(constant([]))
        self.assertFalse(constant([1, 2]))

    def test_variable(self):
        """Test variable predicate."""
        self.assertTrue(variable('x'))
        self.assertTrue(variable('variable'))
        self.assertTrue(variable('+'))  # Operators are strings too

        self.assertFalse(variable(42))
        self.assertFalse(variable([]))
        self.assertFalse(variable([1, 2]))

    def test_arbitrary_constant(self):
        """Test arbitrary constant pattern predicate."""
        self.assertTrue(arbitrary_constant(['?c', 'c1']))
        self.assertFalse(arbitrary_constant(['?', 'x']))
        self.assertFalse(arbitrary_constant(['?v', 'v']))
        self.assertFalse(arbitrary_constant('x'))
        self.assertFalse(arbitrary_constant(42))

    def test_arbitrary_variable(self):
        """Test arbitrary variable pattern predicate."""
        self.assertTrue(arbitrary_variable(['?v', 'v1']))
        self.assertFalse(arbitrary_variable(['?', 'x']))
        self.assertFalse(arbitrary_variable(['?c', 'c']))
        self.assertFalse(arbitrary_variable('x'))
        self.assertFalse(arbitrary_variable(42))

    def test_arbitrary_expression(self):
        """Test arbitrary expression pattern predicate."""
        self.assertTrue(arbitrary_expression(['?', 'x']))
        self.assertFalse(arbitrary_expression(['?c', 'c']))
        self.assertFalse(arbitrary_expression(['?v', 'v']))
        self.assertFalse(arbitrary_expression('x'))
        self.assertFalse(arbitrary_expression(42))

    def test_skeleton_evaluation(self):
        """Test skeleton evaluation pattern predicate."""
        self.assertTrue(skeleton_evaluation([':', 'x']))
        self.assertTrue(skeleton_evaluation([':', ['+', 'a', 'b']]))
        self.assertFalse(skeleton_evaluation(['?', 'x']))
        self.assertFalse(skeleton_evaluation('x'))
        self.assertFalse(skeleton_evaluation(42))


class TestDictionary(unittest.TestCase):
    """Test dictionary operations."""

    def test_empty_dictionary(self):
        """Test empty dictionary creation."""
        self.assertEqual(empty_dictionary(), [])

    def test_extend_dictionary_new_binding(self):
        """Test extending dictionary with new binding."""
        dict = empty_dictionary()
        result = extend_dictionary(['?', 'x'], 42, dict)
        self.assertEqual(result, [['x', 42]])

        result = extend_dictionary(['?v', 'y'], 'value', result)
        self.assertEqual(result, [['x', 42], ['y', 'value']])

    def test_extend_dictionary_existing_same_value(self):
        """Test extending dictionary with existing binding (same value)."""
        dict = [['x', 42]]
        result = extend_dictionary(['?', 'x'], 42, dict)
        self.assertEqual(result, [['x', 42]])  # No change

    def test_extend_dictionary_existing_different_value(self):
        """Test extending dictionary with conflicting binding."""
        dict = [['x', 42]]
        result = extend_dictionary(['?', 'x'], 43, dict)
        self.assertEqual(result, "failed")

    def test_lookup_existing(self):
        """Test lookup of existing variable."""
        dict = [['x', 42], ['y', 'value']]
        self.assertEqual(lookup('x', dict), 42)
        self.assertEqual(lookup('y', dict), 'value')

    def test_lookup_non_existing(self):
        """Test lookup of non-existing variable."""
        dict = [['x', 42]]
        self.assertEqual(lookup('y', dict), 'y')  # Returns variable itself


class TestPatternMatching(unittest.TestCase):
    """Test pattern matching functionality."""

    def test_match_constants(self):
        """Test matching constants."""
        # Matching same constants
        result = match(42, 42, empty_dictionary())
        self.assertEqual(result, [])

        # Matching different constants
        result = match(42, 43, empty_dictionary())
        self.assertEqual(result, "failed")

    def test_match_variables(self):
        """Test matching variables (treated as literals)."""
        result = match('x', 'x', empty_dictionary())
        self.assertEqual(result, [])

        result = match('x', 'y', empty_dictionary())
        self.assertEqual(result, "failed")

    def test_match_arbitrary_constant(self):
        """Test matching with arbitrary constant pattern."""
        # Match constant
        result = match(['?c', 'c1'], 42, empty_dictionary())
        self.assertEqual(result, [['c1', 42]])

        # Don't match variable
        result = match(['?c', 'c1'], 'x', empty_dictionary())
        self.assertEqual(result, "failed")

    def test_match_arbitrary_variable(self):
        """Test matching with arbitrary variable pattern."""
        # Match variable
        result = match(['?v', 'v1'], 'x', empty_dictionary())
        self.assertEqual(result, [['v1', 'x']])

        # Don't match constant
        result = match(['?v', 'v1'], 42, empty_dictionary())
        self.assertEqual(result, "failed")

    def test_match_arbitrary_expression(self):
        """Test matching with arbitrary expression pattern."""
        # Matches anything
        result = match(['?', 'x'], 42, empty_dictionary())
        self.assertEqual(result, [['x', 42]])

        result = match(['?', 'x'], 'var', empty_dictionary())
        self.assertEqual(result, [['x', 'var']])

        result = match(['?', 'x'], ['+', 1, 2], empty_dictionary())
        self.assertEqual(result, [['x', ['+', 1, 2]]])

    def test_match_compound_expressions(self):
        """Test matching compound expressions."""
        # Exact match
        result = match(['+', 'x', 1], ['+', 'x', 1], empty_dictionary())
        self.assertEqual(result, [])

        # Different structure
        result = match(['+', 'x', 1], ['*', 'x', 1], empty_dictionary())
        self.assertEqual(result, "failed")

        # With pattern variables
        result = match(['+', ['?', 'a'], ['?', 'b']], ['+', 3, 4], empty_dictionary())
        self.assertEqual(result, [['a', 3], ['b', 4]])

    def test_match_nested_patterns(self):
        """Test matching nested patterns."""
        pattern = ['+', ['*', ['?', 'x'], 2], ['?', 'y']]
        expr = ['+', ['*', 5, 2], 3]
        result = match(pattern, expr, empty_dictionary())
        self.assertEqual(result, [['x', 5], ['y', 3]])

    def test_match_with_failed_dict(self):
        """Test that failed dictionary propagates."""
        result = match(['?', 'x'], 42, "failed")
        self.assertEqual(result, "failed")

    def test_match_empty_lists(self):
        """Test matching empty lists."""
        result = match([], [], empty_dictionary())
        self.assertEqual(result, [])

        result = match([], [1], empty_dictionary())
        self.assertEqual(result, "failed")

        result = match([1], [], empty_dictionary())
        self.assertEqual(result, "failed")


class TestInstantiation(unittest.TestCase):
    """Test skeleton instantiation."""

    def test_instantiate_constant(self):
        """Test instantiating a constant."""
        result = instantiate(42, empty_dictionary())
        self.assertEqual(result, 42)

    def test_instantiate_variable(self):
        """Test instantiating a variable (literal)."""
        result = instantiate('x', empty_dictionary())
        self.assertEqual(result, 'x')

    def test_instantiate_skeleton_substitution(self):
        """Test instantiating with skeleton substitution."""
        dict = [['x', 42], ['y', 'value']]

        # Simple substitution
        result = instantiate([':', 'x'], dict)
        self.assertEqual(result, 42)

        result = instantiate([':', 'y'], dict)
        self.assertEqual(result, 'value')

    def test_instantiate_compound_with_substitution(self):
        """Test instantiating compound expression with substitutions."""
        dict = [['a', 3], ['b', 4]]
        skeleton = ['+', [':', 'a'], [':', 'b']]
        result = instantiate(skeleton, dict)
        self.assertEqual(result, ['+', 3, 4])

    def test_instantiate_nested_structure(self):
        """Test instantiating nested structures."""
        dict = [['x', 5], ['y', 2]]
        skeleton = ['*', ['+', [':', 'x'], 1], [':', 'y']]
        result = instantiate(skeleton, dict)
        self.assertEqual(result, ['*', ['+', 5, 1], 2])

    def test_instantiate_empty_list(self):
        """Test instantiating empty list."""
        result = instantiate([], empty_dictionary())
        self.assertEqual(result, [])

    def test_instantiate_mixed_literal_and_substitution(self):
        """Test instantiating with mixed literals and substitutions."""
        dict = [['x', 10]]
        skeleton = ['+', 'literal', [':', 'x'], 5]
        result = instantiate(skeleton, dict)
        self.assertEqual(result, ['+', 'literal', 10, 5])


class TestEvaluation(unittest.TestCase):
    """Test expression evaluation."""

    def setUp(self):
        """Set up arithmetic operators dictionary."""
        self.arithmetic_dict = [
            ['+', lambda a, b: a + b],
            ['-', lambda a, b: a - b],
            ['*', lambda a, b: a * b],
            ['/', lambda a, b: a / b if b != 0 else None],
        ]

    def test_evaluate_constant(self):
        """Test evaluating constants."""
        self.assertEqual(evaluate(42, empty_dictionary()), 42)
        self.assertEqual(evaluate(3.14, empty_dictionary()), 3.14)

    def test_evaluate_variable_lookup(self):
        """Test evaluating variables with lookup."""
        dict = [['x', 42], ['y', 'value']]
        self.assertEqual(evaluate('x', dict), 42)
        self.assertEqual(evaluate('y', dict), 'value')
        self.assertEqual(evaluate('z', dict), 'z')  # Not found

    def test_evaluate_simple_arithmetic(self):
        """Test evaluating simple arithmetic expressions."""
        self.assertEqual(evaluate(['+', 3, 4], self.arithmetic_dict), 7)
        self.assertEqual(evaluate(['*', 5, 6], self.arithmetic_dict), 30)
        self.assertEqual(evaluate(['-', 10, 3], self.arithmetic_dict), 7)

    def test_evaluate_nested_arithmetic(self):
        """Test evaluating nested arithmetic expressions."""
        expr = ['+', ['*', 2, 3], 4]
        self.assertEqual(evaluate(expr, self.arithmetic_dict), 10)

        expr = ['*', ['+', 2, 3], ['-', 7, 2]]
        self.assertEqual(evaluate(expr, self.arithmetic_dict), 25)

    def test_evaluate_with_variables(self):
        """Test evaluating expressions with variables."""
        dict = self.arithmetic_dict + [['x', 5], ['y', 3]]
        expr = ['+', 'x', 'y']
        self.assertEqual(evaluate(expr, dict), 8)

        expr = ['*', ['+', 'x', 1], 'y']
        self.assertEqual(evaluate(expr, dict), 18)

    def test_evaluate_unknown_operator(self):
        """Test evaluating with unknown operator."""
        expr = ['unknown', 3, 4]
        result = evaluate(expr, self.arithmetic_dict)
        self.assertEqual(result, expr)  # Returns unchanged

    def test_evaluate_empty_expression(self):
        """Test evaluating empty expression."""
        self.assertEqual(evaluate([], empty_dictionary()), [])


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_eval_exp(self):
        """Test eval_exp extracts second element."""
        self.assertEqual(eval_exp([':', 'x']), 'x')
        self.assertEqual(eval_exp([':', ['+', 1, 2]]), ['+', 1, 2])

    def test_pattern_extraction(self):
        """Test pattern extraction from rule."""
        rule = [['+', ['?', 'x'], 0], [':', 'x']]
        self.assertEqual(pattern(rule), ['+', ['?', 'x'], 0])

    def test_skeleton_extraction(self):
        """Test skeleton extraction from rule."""
        rule = [['+', ['?', 'x'], 0], [':', 'x']]
        self.assertEqual(skeleton(rule), [':', 'x'])

    def test_variable_name_extraction(self):
        """Test variable name extraction from pattern."""
        self.assertEqual(variable_name(['?', 'x']), 'x')
        self.assertEqual(variable_name(['?c', 'const']), 'const')
        self.assertEqual(variable_name(['?v', 'var']), 'var')


class TestSimplifierEdgeCases(unittest.TestCase):
    """Test edge cases for the simplifier."""

    def test_simplify_with_no_rules(self):
        """Test simplifier with no rules still does constant folding."""
        simplify = simplifier([])

        self.assertEqual(simplify(42), 42)
        self.assertEqual(simplify('x'), 'x')
        # Constant folding is enabled by default, so 1 + 2 evaluates to 3
        self.assertEqual(simplify(['+', 1, 2]), 3)

    def test_simplify_atom(self):
        """Test simplifier with atomic expressions."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']]
        ]
        simplify = simplifier(rules)

        # Atoms should pass through unchanged
        self.assertEqual(simplify(42), 42)
        self.assertEqual(simplify('x'), 'x')

    def test_simplify_preventing_infinite_loops(self):
        """Test that simplifier terminates with potentially recursive rules."""
        # This rule could cause infinite loop if not handled properly
        rules = [
            # Only apply to specific structure, not to result
            [['+', 0, ['?', 'x']], [':', 'x']],
        ]

        simplify = simplifier(rules)
        result = simplify(['+', 0, ['+', 0, 'x']])
        self.assertEqual(result, 'x')

    def test_simplify_rule_order_matters(self):
        """Test that rule order affects simplification."""
        # First rule set - general rule first
        rules1 = [
            [['+', ['?', 'x'], ['?', 'y']], ['add', [':', 'x'], [':', 'y']]],
            [['+', ['?', 'x'], 0], [':', 'x']],
        ]

        # Second rule set - specific rule first
        rules2 = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['+', ['?', 'x'], ['?', 'y']], ['add', [':', 'x'], [':', 'y']]],
        ]

        expr = ['+', 'x', 0]

        simplify1 = simplifier(rules1)
        result1 = simplify1(expr)
        self.assertEqual(result1, ['add', 'x', 0])  # First rule matches

        simplify2 = simplifier(rules2)
        result2 = simplify2(expr)
        self.assertEqual(result2, 'x')  # First rule matches

    def test_simplify_deeply_nested(self):
        """Test simplifier with deeply nested expressions."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']],
        ]

        expr = ['+', ['*', ['+', ['*', 'x', 1], 0], 1], 0]
        simplify = simplifier(rules)
        result = simplify(expr)
        self.assertEqual(result, 'x')


class TestErrorConditions(unittest.TestCase):
    """Test error conditions and edge cases."""

    def test_match_with_callable(self):
        """Test that callables in expressions are handled."""
        def func():
            pass

        # Callable in expression should cause match to fail
        result = match(['?', 'x'], func, empty_dictionary())
        self.assertEqual(result, "failed")

    def test_evaluate_with_non_list_dict(self):
        """Test evaluate with non-list dictionary."""
        # Dictionary should be a list of pairs
        result = evaluate(['+', 1, 2], {})
        # Should return expression unchanged when operator not found
        self.assertEqual(result, ['+', 1, 2])


if __name__ == '__main__':
    unittest.main()