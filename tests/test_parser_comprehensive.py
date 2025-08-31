"""
Comprehensive tests for the parser module.
"""

import unittest
from xtk.parser import (
    parse_sexpr, format_sexpr, parse_atom, tokenize,
    parse_dsl, dsl_parser, ParseError, DSLParser
)


class TestTokenizer(unittest.TestCase):
    """Test the tokenizer function."""
    
    def test_simple_tokenization(self):
        """Test basic tokenization."""
        self.assertEqual(tokenize("(+ 1 2)"), ['(', '+', '1', '2', ')'])
        self.assertEqual(tokenize("()"), ['(', ')'])
        self.assertEqual(tokenize("(a b c)"), ['(', 'a', 'b', 'c', ')'])
    
    def test_nested_tokenization(self):
        """Test tokenization of nested expressions."""
        self.assertEqual(
            tokenize("(+ (* 2 3) 4)"),
            ['(', '+', '(', '*', '2', '3', ')', '4', ')']
        )
    
    def test_whitespace_handling(self):
        """Test various whitespace scenarios."""
        self.assertEqual(tokenize("(  +   1    2  )"), ['(', '+', '1', '2', ')'])
        self.assertEqual(tokenize("(\n+\n1\n2\n)"), ['(', '+', '1', '2', ')'])
        self.assertEqual(tokenize("(\t+\t1\t2\t)"), ['(', '+', '1', '2', ')'])
    
    def test_empty_input(self):
        """Test empty and whitespace-only input."""
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   "), [])
        self.assertEqual(tokenize("\n\t"), [])


class TestParseAtom(unittest.TestCase):
    """Test atomic value parsing."""
    
    def test_integers(self):
        """Test integer parsing."""
        self.assertEqual(parse_atom("42"), 42)
        self.assertEqual(parse_atom("-42"), -42)
        self.assertEqual(parse_atom("0"), 0)
    
    def test_floats(self):
        """Test float parsing."""
        self.assertEqual(parse_atom("3.14"), 3.14)
        self.assertEqual(parse_atom("-3.14"), -3.14)
        self.assertEqual(parse_atom("0.0"), 0.0)
        self.assertEqual(parse_atom(".5"), 0.5)
        self.assertEqual(parse_atom("1e10"), 1e10)
        self.assertEqual(parse_atom("1.5e-3"), 1.5e-3)
    
    def test_strings(self):
        """Test string/symbol parsing."""
        self.assertEqual(parse_atom("x"), "x")
        self.assertEqual(parse_atom("abc"), "abc")
        self.assertEqual(parse_atom("+"), "+")
        self.assertEqual(parse_atom("x_1"), "x_1")
        self.assertEqual(parse_atom("?"), "?")
        self.assertEqual(parse_atom(":"), ":")


class TestParseSexpr(unittest.TestCase):
    """Test S-expression parsing."""
    
    def test_empty_list(self):
        """Test parsing empty list."""
        self.assertEqual(parse_sexpr("()"), [])
    
    def test_simple_lists(self):
        """Test parsing simple lists."""
        self.assertEqual(parse_sexpr("(+ 1 2)"), ['+', 1, 2])
        self.assertEqual(parse_sexpr("(* x y)"), ['*', 'x', 'y'])
        self.assertEqual(parse_sexpr("(foo)"), ['foo'])
    
    def test_nested_lists(self):
        """Test parsing nested lists."""
        self.assertEqual(
            parse_sexpr("(+ (* 2 3) 4)"),
            ['+', ['*', 2, 3], 4]
        )
        self.assertEqual(
            parse_sexpr("(a (b (c)))"),
            ['a', ['b', ['c']]]
        )
    
    def test_deeply_nested(self):
        """Test deeply nested structures."""
        expr = "((((((x))))))"
        result = parse_sexpr(expr)
        self.assertEqual(result, [[[[[['x']]]]]]])
    
    def test_mixed_types(self):
        """Test expressions with mixed types."""
        self.assertEqual(
            parse_sexpr("(func 1 2.5 x \"string\")"),
            ['func', 1, 2.5, 'x', '"string"']
        )
    
    def test_special_symbols(self):
        """Test special pattern matching symbols."""
        self.assertEqual(parse_sexpr("(? x)"), ['?', 'x'])
        self.assertEqual(parse_sexpr("(?c c)"), ['?c', 'c'])
        self.assertEqual(parse_sexpr("(?v v)"), ['?v', 'v'])
        self.assertEqual(parse_sexpr("(: x)"), [':', 'x'])
    
    def test_parse_errors(self):
        """Test error handling."""
        with self.assertRaises(ParseError):
            parse_sexpr("(")  # Missing closing paren
        
        with self.assertRaises(ParseError):
            parse_sexpr(")")  # Unexpected closing paren
        
        with self.assertRaises(ParseError):
            parse_sexpr("(+ 1 2))")  # Extra closing paren
        
        with self.assertRaises(ParseError):
            parse_sexpr("")  # Empty expression
    
    def test_multiple_expressions(self):
        """Test that only single expressions are parsed."""
        with self.assertRaises(ParseError):
            parse_sexpr("(+ 1 2) (+ 3 4)")  # Multiple expressions


class TestFormatSexpr(unittest.TestCase):
    """Test S-expression formatting."""
    
    def test_format_atoms(self):
        """Test formatting atomic values."""
        self.assertEqual(format_sexpr(42), "42")
        self.assertEqual(format_sexpr(3.14), "3.14")
        self.assertEqual(format_sexpr("x"), "x")
    
    def test_format_empty_list(self):
        """Test formatting empty list."""
        self.assertEqual(format_sexpr([]), "()")
    
    def test_format_simple_lists(self):
        """Test formatting simple lists."""
        self.assertEqual(format_sexpr(['+', 1, 2]), "(+ 1 2)")
        self.assertEqual(format_sexpr(['*', 'x', 'y']), "(* x y)")
    
    def test_format_nested_lists(self):
        """Test formatting nested lists."""
        self.assertEqual(
            format_sexpr(['+', ['*', 2, 3], 4]),
            "(+ (* 2 3) 4)"
        )
    
    def test_format_with_indentation(self):
        """Test formatting with proper indentation for long expressions."""
        # Long expressions should be formatted on multiple lines
        long_expr = ['+', ['*', 'a', 'b'], ['*', 'c', 'd'], ['*', 'e', 'f']]
        formatted = format_sexpr(long_expr)
        self.assertIn('(+', formatted)
        # Should contain the sub-expressions
        self.assertIn('(* a b)', formatted)
    
    def test_roundtrip(self):
        """Test parse -> format -> parse roundtrip."""
        expressions = [
            "(+ 1 2)",
            "(* (+ x y) (- x y))",
            "((lambda x (+ x 1)) 5)",
            "()",
            "(a (b (c (d))))"
        ]
        
        for expr in expressions:
            parsed = parse_sexpr(expr)
            formatted = format_sexpr(parsed)
            reparsed = parse_sexpr(formatted)
            self.assertEqual(parsed, reparsed, f"Roundtrip failed for {expr}")


class TestDSLParser(unittest.TestCase):
    """Test the infix DSL parser."""
    
    def test_simple_arithmetic(self):
        """Test basic arithmetic expressions."""
        self.assertEqual(dsl_parser.parse("1 + 2"), ['+', 1, 2])
        self.assertEqual(dsl_parser.parse("3 - 4"), ['-', 3, 4])
        self.assertEqual(dsl_parser.parse("5 * 6"), ['*', 5, 6])
        self.assertEqual(dsl_parser.parse("7 / 8"), ['/', 7, 8])
        self.assertEqual(dsl_parser.parse("2 ^ 3"), ['^', 2, 3])
    
    def test_precedence(self):
        """Test operator precedence."""
        # Multiplication before addition
        self.assertEqual(
            dsl_parser.parse("1 + 2 * 3"),
            ['+', 1, ['*', 2, 3]]
        )
        
        # Division before subtraction
        self.assertEqual(
            dsl_parser.parse("10 - 6 / 2"),
            ['-', 10, ['/', 6, 2]]
        )
        
        # Exponentiation before multiplication
        self.assertEqual(
            dsl_parser.parse("2 * 3 ^ 4"),
            ['*', 2, ['^', 3, 4]]
        )
    
    def test_associativity(self):
        """Test operator associativity."""
        # Left associative: addition
        self.assertEqual(
            dsl_parser.parse("1 + 2 + 3"),
            ['+', ['+', 1, 2], 3]
        )
        
        # Right associative: exponentiation
        self.assertEqual(
            dsl_parser.parse("2 ^ 3 ^ 4"),
            ['^', 2, ['^', 3, 4]]
        )
    
    def test_parentheses(self):
        """Test parentheses override precedence."""
        self.assertEqual(
            dsl_parser.parse("(1 + 2) * 3"),
            ['*', ['+', 1, 2], 3]
        )
        
        self.assertEqual(
            dsl_parser.parse("2 ^ (3 * 4)"),
            ['^', 2, ['*', 3, 4]]
        )
    
    def test_function_calls(self):
        """Test function call parsing."""
        self.assertEqual(dsl_parser.parse("sin(x)"), ['sin', 'x'])
        self.assertEqual(dsl_parser.parse("cos(0)"), ['cos', 0])
        self.assertEqual(
            dsl_parser.parse("sin(x + y)"),
            ['sin', ['+', 'x', 'y']]
        )
    
    def test_complex_expressions(self):
        """Test complex mixed expressions."""
        self.assertEqual(
            dsl_parser.parse("sin(x) + cos(y) * 2"),
            ['+', ['sin', 'x'], ['*', ['cos', 'y'], 2]]
        )
    
    def test_variables(self):
        """Test variable parsing."""
        self.assertEqual(dsl_parser.parse("x"), 'x')
        self.assertEqual(dsl_parser.parse("x_1"), 'x_1')
        self.assertEqual(dsl_parser.parse("abc"), 'abc')
    
    def test_negative_numbers(self):
        """Test negative number handling."""
        # This is tricky - negative numbers vs subtraction
        result = dsl_parser.parse("-5")
        self.assertTrue(result == -5 or result == ['-', 0, 5])
    
    def test_whitespace_insensitive(self):
        """Test that whitespace doesn't affect parsing."""
        expr1 = dsl_parser.parse("1+2*3")
        expr2 = dsl_parser.parse("1 + 2 * 3")
        expr3 = dsl_parser.parse("  1  +  2  *  3  ")
        self.assertEqual(expr1, expr2)
        self.assertEqual(expr2, expr3)


class TestParseDSL(unittest.TestCase):
    """Test the simplified DSL parser."""
    
    def test_derivative_notation(self):
        """Test derivative notation."""
        result = parse_dsl("d/dx (x^2)")
        self.assertEqual(result, ['dd', ['^', 'x', 2], 'x'])
    
    def test_function_calls(self):
        """Test function call parsing."""
        for func in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']:
            result = parse_dsl(f"{func}(x)")
            self.assertEqual(result, [func, 'x'])
    
    def test_basic_operators(self):
        """Test basic operator parsing."""
        self.assertEqual(parse_dsl("x + y"), ['+', 'x', 'y'])
        self.assertEqual(parse_dsl("x - y"), ['-', 'x', 'y'])
        self.assertEqual(parse_dsl("x * y"), ['*', 'x', 'y'])
        self.assertEqual(parse_dsl("x / y"), ['/', 'x', 'y'])
        self.assertEqual(parse_dsl("x ^ y"), ['^', 'x', 'y'])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        # Greek letters
        self.assertEqual(parse_sexpr("(+ α β)"), ['+', 'α', 'β'])
        
        # Mathematical symbols
        self.assertEqual(parse_sexpr("(∂ f x)"), ['∂', 'f', 'x'])
    
    def test_very_long_expressions(self):
        """Test handling of very long expressions."""
        # Create a deeply nested expression
        depth = 100
        expr = "(" * depth + "x" + ")" * depth
        result = parse_sexpr(expr)
        
        # Verify the nesting depth
        current = result
        for _ in range(depth - 1):
            self.assertIsInstance(current, list)
            self.assertEqual(len(current), 1)
            current = current[0]
        self.assertEqual(current, 'x')
    
    def test_empty_nested_lists(self):
        """Test various empty nested list scenarios."""
        self.assertEqual(parse_sexpr("(() ())"), [[], []])
        self.assertEqual(parse_sexpr("((()))"), [[[]]])
        self.assertEqual(parse_sexpr("(() () ())"), [[], [], []])
    
    def test_special_characters_in_strings(self):
        """Test special characters in identifiers."""
        self.assertEqual(parse_sexpr("(foo-bar)"), ['foo-bar'])
        self.assertEqual(parse_sexpr("(x.y)"), ['x.y'])
        self.assertEqual(parse_sexpr("(a/b)"), ['a/b'])
        self.assertEqual(parse_sexpr("(f?)"), ['f?'])
        self.assertEqual(parse_sexpr("(g!)"), ['g!'])
    
    def test_numeric_edge_cases(self):
        """Test edge cases in numeric parsing."""
        # Very large numbers
        self.assertEqual(parse_atom("999999999999999999"), 999999999999999999)
        
        # Very small numbers
        self.assertAlmostEqual(parse_atom("1e-100"), 1e-100)
        
        # Infinity (if supported)
        # Note: This might need special handling
        
        # Special float values
        self.assertEqual(parse_atom("0.0"), 0.0)
        self.assertEqual(parse_atom("-0.0"), -0.0)


if __name__ == '__main__':
    unittest.main()