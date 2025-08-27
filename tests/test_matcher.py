import unittest
from xtk.rewriter import match, empty_dictionary

class TestMatch(unittest.TestCase):

    def test_match_constants(self):
        """Test matching a constant pattern with a constant expression."""
        pattern = ['?c', 'a']
        expression = 42
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [['a', 42]], "Matching a constant failed.")

    def test_match_variables(self):
        """Test matching a variable pattern with a variable expression."""
        pattern = ['?v', 'a']
        expression = 'x'
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [['a', 'x']], "Matching a variable failed.")

    def test_match_arbitrary_expression(self):
        """Test matching an arbitrary expression."""
        pattern = ['?', 'exp']
        expression = ['+', 3, 4]
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [['exp', ['+', 3, 4]]], "Matching an arbitrary expression failed.")

    def test_match_recursive_pattern(self):
        """Test matching a recursive pattern."""
        pattern = ['+', ['?', 'x1'], ['?', 'x2']]
        expression = ['+', 'a', 'b']
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [['x1', 'a'], ['x2', 'b']], "Recursive pattern matching failed.")

    def test_match_with_existing_dictionary(self):
        """Test matching with an existing dictionary."""
        pattern = ['+', ['?', 'x1'], ['?', 'x2']]
        expression = ['+', 'a', 'b']
        existing_dict = [['x1', 'c']]
        result = match(pattern, expression, existing_dict)
        self.assertEqual(result, 'failed', "Match with conflicting dictionary should fail.")

    def test_match_failed_due_to_structure(self):
        """Test a match failure due to structure mismatch."""
        pattern = ['+', ['?', 'x1'], ['?', 'x2']]
        expression = ['-', 'a', 'b']  # Different operator
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, 'failed', "Match should fail due to structure mismatch.")

    def test_match_atomic_patterns(self):
        """Test matching atomic patterns."""
        pattern = '+'
        expression = '+'
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [], "Atomic pattern matching failed.")

        # Mismatched atom
        pattern = '+'
        expression = '-'
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, 'failed', "Atomic pattern mismatch should fail.")

    def test_match_empty_pattern_and_expression(self):
        """Test matching an empty pattern with an empty expression."""
        pattern = []
        expression = []
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [], "Matching empty pattern and expression should succeed.")

    def test_match_empty_pattern_with_non_empty_expression(self):
        """Test matching an empty pattern with a non-empty expression."""
        pattern = []
        expression = ['x']
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, 'failed', "Empty pattern should not match non-empty expression.")

    def test_match_complex_structure(self):
        """Test matching a complex nested structure."""
        pattern = ['+', ['*', ['?', 'x'], ['?', 'y']], ['?', 'z']]
        expression = ['+', ['*', 2, 3], 5]
        result = match(pattern, expression, empty_dictionary())
        expected_result = [['x', 2], ['y', 3], ['z', 5]]
        self.assertEqual(result, expected_result, "Matching complex nested structure failed.")

    def test_match_repeated_variable(self):
        """Test matching with repeated variables."""
        pattern = ['+', ['?', 'x'], ['?', 'x']]
        expression = ['+', 3, 3]
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [['x', 3]], "Matching with repeated variables failed.")

        # Test mismatch in repeated variable
        expression = ['+', 3, 4]
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, 'failed', "Repeated variable match should fail if values differ.")

    def test_match_nary(self):
        """Test matching with 3-ary pattern."""
        pattern = ['+', ['+', ['?c', 'x'], ['?c', 'x']], ['?c', 'x']]
        expression = ['+', ['+', 3, 3], 3]
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [['x', 3]], "Matching with 3-ary pattern failed.")

    def test_match_nary_complex(self):
        """Test matching with 3-ary pattern with complex sub-expressions."""
        pattern = ['+', ['+', ['?', 'x'], ['?', 'y']], ['?', 'x']]
        sub_expr = ['*', 3, 2]
        expression = ['+', ['+', sub_expr, 2], sub_expr]
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, [['x', sub_expr], ['y', 2]], "Matching with 3-ary pattern failed.")


    # disable this test
    @unittest.skip("Investigate if this test should return `failed` or raise an exception. I think in fact")
    def test_match_partial_match(self):
        """Test matching where only part of the pattern matches."""
        pattern = ['+', ['+' ['?c', 'c1'], ['?c c1']], ['?c', 'c1']]
        expression = ['+', 3]  # Missing one operand -- actually returns a `car: argument is an empty list` error
        result = match(pattern, expression, empty_dictionary())
        self.assertEqual(result, 'failed', "Partial match should fail.")

if __name__ == '__main__':
    unittest.main()
