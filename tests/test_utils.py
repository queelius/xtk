import unittest
from xtk.rewriter import (
    car, cdr, variable_name, arbitrary_constant,
    arbitrary_expression, arbitrary_variable,
    constant, compound, atom, variable,
    empty_dictionary, null, cons
)

class TestUtils(unittest.TestCase):

    def test_variable(self):
        self.assertFalse(variable(3))
        self.assertTrue(variable("x"))
        self.assertFalse(variable(["+", 1, 2]))


    def test_car_and_cdr(self):
        lst = ['?c', 'c']
        self.assertEqual(car(lst), '?c')
        self.assertEqual(cdr(lst), ['c'])
        self.assertEqual(car(cdr(lst)), 'c')

    def test_variable_name(self):
        pat = ['?v', 'a']
        self.assertEqual(variable_name(pat), 'a')

    def test_arbitrary_constant(self):
        self.assertTrue(arbitrary_constant(['?c', 'const']))
        self.assertFalse(arbitrary_constant(42))
        self.assertTrue(constant(2))

    def test_arbitrary_variable(self):
        self.assertTrue(arbitrary_variable(['?v', 'var']))
        self.assertFalse(arbitrary_variable(['?', 'expr']))

    def test_arbitrary_expression(self):
        self.assertTrue(arbitrary_expression(['?', 'expr']))
        self.assertFalse(arbitrary_expression(['?c', 'const']))

    def test_constant(self):
        self.assertTrue(constant(3))
        self.assertFalse(constant('x'))
        self.assertFalse(constant(['+', 1, 2]))

    def test_compound(self):
        self.assertFalse(compound(3))
        self.assertFalse(compound('x'))
        self.assertTrue(compound(['+', 1, 2]))

    def test_atom(self):
        self.assertTrue(atom(3))
        self.assertTrue(atom('x'))
        self.assertFalse(atom(['+', 1, 2]))

    def test_empty_dictionary(self):
        self.assertEqual(empty_dictionary(), [])

    def test_null(self):
        self.assertTrue(null([]))
        self.assertFalse(null([1]))

    def test_cons(self):
        self.assertEqual(cons(1, [2, 3]), [1, 2, 3])
        self.assertEqual(cons('a', []), ['a'])

if __name__ == '__main__':
    unittest.main()