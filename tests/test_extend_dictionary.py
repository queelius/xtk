import unittest
from xtk.rewriter import extend_dictionary, empty_dictionary

class TestExtendDictionary(unittest.TestCase):

    def test_add_new_entry_to_empty_dict(self):
        dict1 = empty_dictionary()
        result1 = extend_dictionary(['?', 'x1'], 'x', dict1)
        expected = [['x1', 'x']]
        self.assertEqual(result1, expected)

    def test_add_non_conflicting_entry(self):
        dict2 = [['x1', 'x']]
        result2 = extend_dictionary(['?', 'x2'], 'y', dict2)
        expected = [['x1', 'x'], ['x2', 'y']]
        self.assertEqual(result2, expected)

    def test_add_conflicting_entry(self):
        dict3 = [['x1', 'x']]
        result3 = extend_dictionary(['?', 'x1'], 'y', dict3)
        expected = 'failed'
        self.assertEqual(result3, expected)

    def test_add_matching_entry(self):
        dict4 = [['x1', 'x']]
        result4 = extend_dictionary(['?', 'x1'], 'x', dict4)
        expected = [['x1', 'x']]
        self.assertEqual(result4, expected)

    def test_extend_with_multiple_new_variables(self):
        dict5 = [['x1', 'x']]
        result5 = extend_dictionary(['?', 'x2'], 'y', dict5)
        result5 = extend_dictionary(['?', 'x3'], 'z', result5)
        expected = [['x1', 'x'], ['x2', 'y'], ['x3', 'z']]
        self.assertEqual(result5, expected)

if __name__ == '__main__':
    unittest.main()