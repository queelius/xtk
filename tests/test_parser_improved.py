"""Comprehensive test suite for parser.py module to improve coverage."""

import unittest
from xtk.parser import (
    parse_sexpr, format_sexpr, tokenize, DSLParser, InfixParser,
    optimize_expression, validate_expression, ExpressionError
)


class TestTokenize(unittest.TestCase):
    """Test the tokenize function."""

    def test_tokenize_simple_expression(self):
        """Test tokenizing simple S-expression."""
        result = tokenize("(+ 1 2)")
        self.assertEqual(result, ['(', '+', '1', '2', ')'])

    def test_tokenize_nested_expression(self):
        """Test tokenizing nested S-expression."""
        result = tokenize("(+ (* 2 3) 4)")
        self.assertEqual(result, ['(', '+', '(', '*', '2', '3', ')', '4', ')'])

    def test_tokenize_with_whitespace(self):
        """Test tokenizing with various whitespace."""
        result = tokenize("( +   1    2  )")
        self.assertEqual(result, ['(', '+', '1', '2', ')'])

    def test_tokenize_with_strings(self):
        """Test tokenizing with string literals."""
        result = tokenize('(concat "hello" "world")')
        self.assertEqual(result, ['(', 'concat', '"hello"', '"world"', ')'])

    def test_tokenize_with_symbols(self):
        """Test tokenizing with various symbols."""
        result = tokenize("(? x)")
        self.assertEqual(result, ['(', '?', 'x', ')'])

        result = tokenize("(?c const)")
        self.assertEqual(result, ['(', '?c', 'const', ')'])

    def test_tokenize_empty_expression(self):
        """Test tokenizing empty expression."""
        result = tokenize("()")
        self.assertEqual(result, ['(', ')'])

    def test_tokenize_complex_expression(self):
        """Test tokenizing complex expression."""
        result = tokenize("(lambda (x y) (+ (* x x) (* y y)))")
        self.assertEqual(result, ['(', 'lambda', '(', 'x', 'y', ')',
                                 '(', '+', '(', '*', 'x', 'x', ')',
                                 '(', '*', 'y', 'y', ')', ')', ')'])


class TestParseSexpr(unittest.TestCase):
    """Test S-expression parsing."""

    def test_parse_number(self):
        """Test parsing numbers."""
        self.assertEqual(parse_sexpr("42"), 42)
        self.assertEqual(parse_sexpr("3.14"), 3.14)
        self.assertEqual(parse_sexpr("-5"), -5)
        self.assertEqual(parse_sexpr("-2.5"), -2.5)

    def test_parse_symbol(self):
        """Test parsing symbols."""
        self.assertEqual(parse_sexpr("x"), "x")
        self.assertEqual(parse_sexpr("+"), "+")
        self.assertEqual(parse_sexpr("foo-bar"), "foo-bar")

    def test_parse_simple_list(self):
        """Test parsing simple lists."""
        self.assertEqual(parse_sexpr("(+ 1 2)"), ['+', 1, 2])
        self.assertEqual(parse_sexpr("(* x y)"), ['*', 'x', 'y'])

    def test_parse_nested_list(self):
        """Test parsing nested lists."""
        result = parse_sexpr("(+ (* 2 3) 4)")
        self.assertEqual(result, ['+', ['*', 2, 3], 4])

    def test_parse_empty_list(self):
        """Test parsing empty list."""
        self.assertEqual(parse_sexpr("()"), [])

    def test_parse_complex_expression(self):
        """Test parsing complex expression."""
        result = parse_sexpr("(define (square x) (* x x))")
        self.assertEqual(result, ['define', ['square', 'x'], ['*', 'x', 'x']])

    def test_parse_with_patterns(self):
        """Test parsing with pattern syntax."""
        result = parse_sexpr("(? x)")
        self.assertEqual(result, ['?', 'x'])

        result = parse_sexpr("(?c const)")
        self.assertEqual(result, ['?c', 'const'])

        result = parse_sexpr("(: var)")
        self.assertEqual(result, [':', 'var'])

    def test_parse_quoted_expression(self):
        """Test parsing quoted expressions."""
        result = parse_sexpr("'(+ 1 2)")
        self.assertEqual(result, ['quote', ['+', 1, 2]])

    def test_parse_quasiquote(self):
        """Test parsing quasiquoted expressions."""
        result = parse_sexpr("`(+ ,x 2)")
        self.assertEqual(result, ['quasiquote', ['+', ['unquote', 'x'], 2]])

    def test_parse_error_unmatched_paren(self):
        """Test parse error on unmatched parenthesis."""
        with self.assertRaises(ExpressionError):
            parse_sexpr("(+ 1 2")

        with self.assertRaises(ExpressionError):
            parse_sexpr("+ 1 2)")

    def test_parse_error_empty_input(self):
        """Test parse error on empty input."""
        with self.assertRaises(ExpressionError):
            parse_sexpr("")

        with self.assertRaises(ExpressionError):
            parse_sexpr("   ")


class TestFormatSexpr(unittest.TestCase):
    """Test S-expression formatting."""

    def test_format_number(self):
        """Test formatting numbers."""
        self.assertEqual(format_sexpr(42), "42")
        self.assertEqual(format_sexpr(3.14), "3.14")
        self.assertEqual(format_sexpr(-5), "-5")

    def test_format_symbol(self):
        """Test formatting symbols."""
        self.assertEqual(format_sexpr("x"), "x")
        self.assertEqual(format_sexpr("+"), "+")

    def test_format_simple_list(self):
        """Test formatting simple lists."""
        self.assertEqual(format_sexpr(['+', 1, 2]), "(+ 1 2)")
        self.assertEqual(format_sexpr(['*', 'x', 'y']), "(* x y)")

    def test_format_nested_list(self):
        """Test formatting nested lists."""
        expr = ['+', ['*', 2, 3], 4]
        self.assertEqual(format_sexpr(expr), "(+ (* 2 3) 4)")

    def test_format_empty_list(self):
        """Test formatting empty list."""
        self.assertEqual(format_sexpr([]), "()")

    def test_format_complex_expression(self):
        """Test formatting complex expression."""
        expr = ['define', ['square', 'x'], ['*', 'x', 'x']]
        self.assertEqual(format_sexpr(expr), "(define (square x) (* x x))")

    def test_format_with_patterns(self):
        """Test formatting with pattern syntax."""
        self.assertEqual(format_sexpr(['?', 'x']), "(? x)")
        self.assertEqual(format_sexpr(['?c', 'const']), "(?c const)")
        self.assertEqual(format_sexpr([':', 'var']), "(: var)")


class TestDSLParser(unittest.TestCase):
    """Test the DSL parser."""

    def setUp(self):
        """Set up DSL parser instance."""
        self.parser = DSLParser()

    def test_parse_number(self):
        """Test parsing numbers in DSL."""
        self.assertEqual(self.parser.parse("42"), 42)
        self.assertEqual(self.parser.parse("3.14"), 3.14)
        self.assertEqual(self.parser.parse("-5"), -5)

    def test_parse_identifier(self):
        """Test parsing identifiers in DSL."""
        self.assertEqual(self.parser.parse("x"), "x")
        self.assertEqual(self.parser.parse("foo_bar"), "foo_bar")

    def test_parse_function_call(self):
        """Test parsing function calls in DSL."""
        result = self.parser.parse("sin(x)")
        self.assertEqual(result, ['sin', 'x'])

        result = self.parser.parse("add(1, 2)")
        self.assertEqual(result, ['add', 1, 2])

    def test_parse_nested_functions(self):
        """Test parsing nested function calls."""
        result = self.parser.parse("sin(cos(x))")
        self.assertEqual(result, ['sin', ['cos', 'x']])

    def test_parse_list_literal(self):
        """Test parsing list literals in DSL."""
        result = self.parser.parse("[1, 2, 3]")
        self.assertEqual(result, ['list', 1, 2, 3])

    def test_parse_empty_list(self):
        """Test parsing empty list in DSL."""
        result = self.parser.parse("[]")
        self.assertEqual(result, ['list'])

    def test_parse_pattern_syntax(self):
        """Test parsing pattern syntax in DSL."""
        result = self.parser.parse("?x")
        self.assertEqual(result, ['?', 'x'])

        result = self.parser.parse("?c:const")
        self.assertEqual(result, ['?c', 'const'])

        result = self.parser.parse("?v:var")
        self.assertEqual(result, ['?v', 'var'])

    def test_parse_substitution_syntax(self):
        """Test parsing substitution syntax in DSL."""
        result = self.parser.parse(":x")
        self.assertEqual(result, [':', 'x'])

    def test_parse_rule_syntax(self):
        """Test parsing rule syntax in DSL."""
        result = self.parser.parse("(+ ?x 0) -> :x")
        expected = ['rule', ['+', ['?', 'x'], 0], [':', 'x']]
        self.assertEqual(result, expected)

    def test_parse_complex_dsl(self):
        """Test parsing complex DSL expressions."""
        result = self.parser.parse("deriv(sin(x), x)")
        self.assertEqual(result, ['deriv', ['sin', 'x'], 'x'])


class TestInfixParser(unittest.TestCase):
    """Test the infix expression parser."""

    def setUp(self):
        """Set up infix parser instance."""
        self.parser = InfixParser()

    def test_parse_simple_arithmetic(self):
        """Test parsing simple arithmetic."""
        self.assertEqual(self.parser.parse("1 + 2"), ['+', 1, 2])
        self.assertEqual(self.parser.parse("3 - 4"), ['-', 3, 4])
        self.assertEqual(self.parser.parse("5 * 6"), ['*', 5, 6])
        self.assertEqual(self.parser.parse("8 / 2"), ['/', 8, 2])

    def test_parse_operator_precedence(self):
        """Test operator precedence."""
        result = self.parser.parse("1 + 2 * 3")
        self.assertEqual(result, ['+', 1, ['*', 2, 3]])

        result = self.parser.parse("2 * 3 + 4")
        self.assertEqual(result, ['+', ['*', 2, 3], 4])

    def test_parse_parentheses(self):
        """Test parsing with parentheses."""
        result = self.parser.parse("(1 + 2) * 3")
        self.assertEqual(result, ['*', ['+', 1, 2], 3])

    def test_parse_power_operator(self):
        """Test parsing power operator."""
        result = self.parser.parse("x ^ 2")
        self.assertEqual(result, ['^', 'x', 2])

        result = self.parser.parse("2 ^ 3 ^ 4")
        # Right associative
        self.assertEqual(result, ['^', 2, ['^', 3, 4]])

    def test_parse_unary_minus(self):
        """Test parsing unary minus."""
        result = self.parser.parse("-x")
        self.assertEqual(result, ['-', 0, 'x'])

        result = self.parser.parse("-5 + 3")
        self.assertEqual(result, ['+', ['-', 0, 5], 3])

    def test_parse_function_calls(self):
        """Test parsing function calls in infix."""
        result = self.parser.parse("sin(x)")
        self.assertEqual(result, ['sin', 'x'])

        result = self.parser.parse("sin(x) + cos(y)")
        self.assertEqual(result, ['+', ['sin', 'x'], ['cos', 'y']])

    def test_parse_complex_expression(self):
        """Test parsing complex infix expression."""
        result = self.parser.parse("2 * sin(x) + 3 * cos(y)")
        expected = ['+', ['*', 2, ['sin', 'x']], ['*', 3, ['cos', 'y']]]
        self.assertEqual(result, expected)


class TestOptimizeExpression(unittest.TestCase):
    """Test expression optimization."""

    def test_optimize_constants(self):
        """Test optimizing constant expressions."""
        # Should evaluate constant arithmetic
        result = optimize_expression(['+', 1, 2])
        self.assertEqual(result, 3)

        result = optimize_expression(['*', 3, 4])
        self.assertEqual(result, 12)

    def test_optimize_identity(self):
        """Test optimizing identity operations."""
        # x + 0 = x
        result = optimize_expression(['+', 'x', 0])
        self.assertEqual(result, 'x')

        # x * 1 = x
        result = optimize_expression(['*', 'x', 1])
        self.assertEqual(result, 'x')

        # x * 0 = 0
        result = optimize_expression(['*', 'x', 0])
        self.assertEqual(result, 0)

    def test_optimize_nested(self):
        """Test optimizing nested expressions."""
        expr = ['+', ['*', 'x', 1], 0]
        result = optimize_expression(expr)
        self.assertEqual(result, 'x')

    def test_optimize_no_change(self):
        """Test optimization with no applicable rules."""
        expr = ['+', 'x', 'y']
        result = optimize_expression(expr)
        self.assertEqual(result, expr)


class TestValidateExpression(unittest.TestCase):
    """Test expression validation."""

    def test_validate_valid_expressions(self):
        """Test validating valid expressions."""
        # Should not raise
        validate_expression(42)
        validate_expression('x')
        validate_expression(['+', 1, 2])
        validate_expression(['+', ['*', 'x', 2], 3])

    def test_validate_empty_list(self):
        """Test validating empty list."""
        with self.assertRaises(ExpressionError):
            validate_expression([])

    def test_validate_invalid_operator(self):
        """Test validating invalid operator."""
        with self.assertRaises(ExpressionError):
            validate_expression([42, 1, 2])  # Operator must be string

    def test_validate_single_element_list(self):
        """Test validating single element list."""
        with self.assertRaises(ExpressionError):
            validate_expression(['+'])  # Operator needs operands

    def test_validate_nested_invalid(self):
        """Test validating nested invalid expression."""
        with self.assertRaises(ExpressionError):
            validate_expression(['+', [42, 1], 2])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_parse_sexpr_with_comments(self):
        """Test parsing S-expressions with comments."""
        # Comments should be ignored
        result = parse_sexpr("; This is a comment\n(+ 1 2)")
        self.assertEqual(result, ['+', 1, 2])

    def test_format_sexpr_none(self):
        """Test formatting None value."""
        result = format_sexpr(None)
        self.assertEqual(result, "nil")

    def test_format_sexpr_boolean(self):
        """Test formatting boolean values."""
        self.assertEqual(format_sexpr(True), "#t")
        self.assertEqual(format_sexpr(False), "#f")

    def test_tokenize_special_characters(self):
        """Test tokenizing special characters."""
        result = tokenize("(>= x 5)")
        self.assertEqual(result, ['(', '>=', 'x', '5', ')'])

        result = tokenize("(!= a b)")
        self.assertEqual(result, ['(', '!=', 'a', 'b', ')'])

    def test_parse_sexpr_unicode(self):
        """Test parsing with Unicode characters."""
        result = parse_sexpr("(λ x (* x x))")
        self.assertEqual(result, ['λ', 'x', ['*', 'x', 'x']])

    def test_dsl_parser_errors(self):
        """Test DSL parser error handling."""
        parser = DSLParser()

        with self.assertRaises(ExpressionError):
            parser.parse("(unclosed")

        with self.assertRaises(ExpressionError):
            parser.parse("invalid syntax @#$")

    def test_infix_parser_errors(self):
        """Test infix parser error handling."""
        parser = InfixParser()

        with self.assertRaises(ExpressionError):
            parser.parse("1 +")  # Missing operand

        with self.assertRaises(ExpressionError):
            parser.parse("+ 1")  # Missing operand

        with self.assertRaises(ExpressionError):
            parser.parse("1 2")  # Missing operator


if __name__ == '__main__':
    unittest.main()