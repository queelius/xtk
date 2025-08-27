import unittest
from xtk.rewriter import instantiate, empty_dictionary

class TestInstantiate(unittest.TestCase):

    def test_instantiate_atomic_skeleton(self):
        """Test instantiating an atomic skeleton."""
        skeleton = 'x'
        dictionary = [['x', 42]]
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, 'x', "Atomic skeletons should remain unchanged.")

    def test_instantiate_constant(self):
        """Test instantiating a constant skeleton."""
        skeleton = 42
        dictionary = empty_dictionary()
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, 42, "Constant skeletons should remain unchanged.")

    def test_instantiate_variable(self):
        """Test instantiating a variable."""
        skeleton = [':', 'v']
        dictionary = [['v', 'x']]
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, 'x', "Variable skeleton should be replaced by its value.")

    def test_instantiate_nested_structure(self):
        """Test instantiating a nested skeleton structure."""
        skeleton = ['+', [':', 'x1'], [':', 'x2']]
        dictionary = [['x1', 3], ['x2', 4]]
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, ['+', 3, 4], "Nested structure instantiation failed.")

    def test_instantiate_with_skeleton_evaluation(self):
        """Test instantiating with skeleton evaluation."""
        skeleton = [':', ['+', 'x1', 3]]
        dictionary = [['x1', 2], ['+', lambda a, b: a + b]]
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, 5, "Skeleton evaluation failed.")

    def test_instantiate_with_empty_dictionary(self):
        """Test instantiating with an empty dictionary."""
        skeleton = [':', 'v']
        dictionary = empty_dictionary()
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, 'v', "Skeleton should remain unchanged with an empty dictionary.")

    def test_instantiate_compound_structure(self):
        """Test instantiating a compound structure."""
        skeleton = ['+', ['*', [':', 'x'], [':', 'y']], 5]
        dictionary = [['x', 2], ['y', 3], ['*', lambda a, b: a * b], ['+', lambda a, b: a + b]]
        result = instantiate(skeleton, dictionary)
        expected_result = ['+', ['*', 2, 3], 5]
        self.assertEqual(result, expected_result, "Compound structure instantiation failed.")

    def test_instantiate_with_missing_variable(self):
        """Test instantiating with a missing variable in the dictionary."""
        skeleton = [':', 'v']
        dictionary = [['u', 'missing']]
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, 'v', "Skeleton with missing variable should remain unchanged.")

    def test_instantiate_with_constant_in_evaluation(self):
        """Test instantiating where evaluation involves constants."""
        skeleton = [':', ['+', 3, 5]]
        dictionary = [['+', lambda a, b: a + b]]
        result = instantiate(skeleton, dictionary)
        self.assertEqual(result, 8, "Instantiation with constants failed.")

if __name__ == '__main__':
    unittest.main()
