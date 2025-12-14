"""Tests for the rule DSL parser."""

import unittest
from xtk.rule_dsl import (
    parse_dsl, parse_rule_line, parse_dsl_expr,
    convert_dsl_to_sexpr, format_dsl_rule, format_dsl_expr,
    rule, rules, load_dsl_rules, ParsedRule
)


class TestConvertDslToSexpr(unittest.TestCase):
    """Test DSL to S-expression conversion."""

    def test_simple_match(self):
        """Test ?x -> (? x)."""
        result = convert_dsl_to_sexpr("?x")
        self.assertEqual(result, "(? x)")

    def test_multiple_matches(self):
        """Test multiple ?vars."""
        result = convert_dsl_to_sexpr("(+ ?x ?y)")
        self.assertEqual(result, "(+ (? x) (? y))")

    def test_typed_const(self):
        """Test ?c:const -> (?c c)."""
        result = convert_dsl_to_sexpr("?c:const")
        self.assertEqual(result, "(?c c)")

    def test_typed_var(self):
        """Test ?v:var -> (?v v)."""
        result = convert_dsl_to_sexpr("?v:var")
        self.assertEqual(result, "(?v v)")

    def test_typed_any(self):
        """Test ?x:any -> (? x)."""
        result = convert_dsl_to_sexpr("?x:any")
        self.assertEqual(result, "(? x)")

    def test_skeleton_substitution(self):
        """Test :x -> (: x)."""
        result = convert_dsl_to_sexpr(":x")
        self.assertEqual(result, "(: x)")

    def test_complex_expression(self):
        """Test complex expression with mixed syntax."""
        result = convert_dsl_to_sexpr("(dd ?c:const ?v:var)")
        self.assertEqual(result, "(dd (?c c) (?v v))")

    def test_skeleton_expression(self):
        """Test skeleton with substitutions."""
        result = convert_dsl_to_sexpr("(+ :x :y)")
        self.assertEqual(result, "(+ (: x) (: y))")


class TestParseDslExpr(unittest.TestCase):
    """Test DSL expression parsing."""

    def test_simple_match(self):
        """Test parsing ?x."""
        result = parse_dsl_expr("?x")
        self.assertEqual(result, ['?', 'x'])

    def test_typed_const(self):
        """Test parsing ?c:const."""
        result = parse_dsl_expr("?c:const")
        self.assertEqual(result, ['?c', 'c'])

    def test_typed_var(self):
        """Test parsing ?v:var."""
        result = parse_dsl_expr("?v:var")
        self.assertEqual(result, ['?v', 'v'])

    def test_skeleton_sub(self):
        """Test parsing :x."""
        result = parse_dsl_expr(":x")
        self.assertEqual(result, [':', 'x'])

    def test_compound_pattern(self):
        """Test parsing compound pattern."""
        result = parse_dsl_expr("(+ ?x 0)")
        self.assertEqual(result, ['+', ['?', 'x'], 0])

    def test_nested_pattern(self):
        """Test parsing nested pattern."""
        result = parse_dsl_expr("(dd (+ ?f ?g) ?v:var)")
        expected = ['dd', ['+', ['?', 'f'], ['?', 'g']], ['?v', 'v']]
        self.assertEqual(result, expected)


class TestParseRuleLine(unittest.TestCase):
    """Test single rule line parsing."""

    def test_basic_rule(self):
        """Test basic pattern => skeleton."""
        result = parse_rule_line("(+ ?x 0) => :x")
        self.assertIsNotNone(result)
        self.assertEqual(result.pattern, ['+', ['?', 'x'], 0])
        self.assertEqual(result.skeleton, [':', 'x'])
        self.assertIsNone(result.name)

    def test_named_rule(self):
        """Test @name: pattern => skeleton."""
        result = parse_rule_line("@identity-add: (+ ?x 0) => :x")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "identity-add")
        self.assertEqual(result.pattern, ['+', ['?', 'x'], 0])
        self.assertEqual(result.skeleton, [':', 'x'])

    def test_with_description(self):
        """Test rule with description."""
        result = parse_rule_line("(+ ?x 0) => :x", "Adding zero is identity")
        self.assertIsNotNone(result)
        self.assertEqual(result.description, "Adding zero is identity")

    def test_typed_matches(self):
        """Test rule with typed matches."""
        result = parse_rule_line("(dd ?c:const ?v:var) => 0")
        self.assertIsNotNone(result)
        self.assertEqual(result.pattern, ['dd', ['?c', 'c'], ['?v', 'v']])
        self.assertEqual(result.skeleton, 0)

    def test_complex_skeleton(self):
        """Test rule with complex skeleton."""
        result = parse_rule_line("(dd (+ ?f ?g) ?v:var) => (+ (dd :f :v) (dd :g :v))")
        self.assertIsNotNone(result)
        expected_skeleton = ['+', ['dd', [':', 'f'], [':', 'v']],
                                  ['dd', [':', 'g'], [':', 'v']]]
        self.assertEqual(result.skeleton, expected_skeleton)

    def test_invalid_no_arrow(self):
        """Test rule without => returns None."""
        result = parse_rule_line("(+ ?x 0) :x")
        self.assertIsNone(result)


class TestParseDsl(unittest.TestCase):
    """Test multi-line DSL parsing."""

    def test_single_rule(self):
        """Test parsing single rule."""
        text = "(+ ?x 0) => :x"
        result = parse_dsl(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pattern, ['+', ['?', 'x'], 0])

    def test_multiple_rules(self):
        """Test parsing multiple rules."""
        text = """
        (+ ?x 0) => :x
        (* ?x 1) => :x
        (* ?x 0) => 0
        """
        result = parse_dsl(text)
        self.assertEqual(len(result), 3)

    def test_with_comments(self):
        """Test parsing with comments."""
        text = """
        ; Identity rules
        (+ ?x 0) => :x
        ; Multiplication by one
        (* ?x 1) => :x
        """
        result = parse_dsl(text)
        self.assertEqual(len(result), 2)
        # Comment becomes description
        self.assertEqual(result[0].description, "Identity rules")
        self.assertEqual(result[1].description, "Multiplication by one")

    def test_named_rules(self):
        """Test parsing named rules."""
        text = """
        @add-zero: (+ ?x 0) => :x
        @mul-one: (* ?x 1) => :x
        """
        result = parse_dsl(text)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "add-zero")
        self.assertEqual(result[1].name, "mul-one")

    def test_skip_empty_lines(self):
        """Test that empty lines are skipped."""
        text = """
        (+ ?x 0) => :x

        (* ?x 1) => :x

        """
        result = parse_dsl(text)
        self.assertEqual(len(result), 2)

    def test_hash_comments(self):
        """Test # style comments."""
        text = """
        # Python style comment
        (+ ?x 0) => :x
        """
        result = parse_dsl(text)
        self.assertEqual(len(result), 1)

    def test_slash_comments(self):
        """Test // style comments."""
        text = """
        // C++ style comment
        (+ ?x 0) => :x
        """
        result = parse_dsl(text)
        self.assertEqual(len(result), 1)


class TestFormatDslExpr(unittest.TestCase):
    """Test expression formatting."""

    def test_format_match(self):
        """Test formatting ['?', 'x'] -> ?x."""
        result = format_dsl_expr(['?', 'x'])
        self.assertEqual(result, "?x")

    def test_format_const_match(self):
        """Test formatting ['?c', 'c'] -> ?c:const."""
        result = format_dsl_expr(['?c', 'c'])
        self.assertEqual(result, "?c:const")

    def test_format_var_match(self):
        """Test formatting ['?v', 'v'] -> ?v:var."""
        result = format_dsl_expr(['?v', 'v'])
        self.assertEqual(result, "?v:var")

    def test_format_substitution(self):
        """Test formatting [':', 'x'] -> :x."""
        result = format_dsl_expr([':', 'x'])
        self.assertEqual(result, ":x")

    def test_format_compound(self):
        """Test formatting compound expression."""
        result = format_dsl_expr(['+', ['?', 'x'], 0])
        self.assertEqual(result, "(+ ?x 0)")

    def test_format_atom(self):
        """Test formatting atoms."""
        self.assertEqual(format_dsl_expr('x'), 'x')
        self.assertEqual(format_dsl_expr(42), '42')


class TestFormatDslRule(unittest.TestCase):
    """Test rule formatting."""

    def test_format_basic_rule(self):
        """Test formatting basic rule."""
        rule = [['+', ['?', 'x'], 0], [':', 'x']]
        result = format_dsl_rule(rule)
        self.assertEqual(result, "(+ ?x 0) => :x")

    def test_format_parsed_rule(self):
        """Test formatting ParsedRule."""
        parsed = ParsedRule(
            pattern=['+', ['?', 'x'], 0],
            skeleton=[':', 'x'],
            name="add-zero"
        )
        result = format_dsl_rule(parsed)
        self.assertEqual(result, "@add-zero: (+ ?x 0) => :x")

    def test_format_tuple_rule(self):
        """Test formatting tuple rule."""
        rule = (['+', ['?', 'x'], 0], [':', 'x'])
        result = format_dsl_rule(rule)
        self.assertEqual(result, "(+ ?x 0) => :x")


class TestRuleConvenience(unittest.TestCase):
    """Test convenience functions."""

    def test_rule_function(self):
        """Test rule() convenience function."""
        result = rule("(+ ?x 0) => :x")
        expected = [['+', ['?', 'x'], 0], [':', 'x']]
        self.assertEqual(result, expected)

    def test_rule_invalid(self):
        """Test rule() with invalid input."""
        with self.assertRaises(ValueError):
            rule("invalid")

    def test_rules_function(self):
        """Test rules() convenience function."""
        result = rules("""
            (+ ?x 0) => :x
            (* ?x 1) => :x
        """)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [['+', ['?', 'x'], 0], [':', 'x']])
        self.assertEqual(result[1], [['*', ['?', 'x'], 1], [':', 'x']])


class TestLoadDslRules(unittest.TestCase):
    """Test loading rules from DSL."""

    def test_load_from_string(self):
        """Test loading from string."""
        text = """
        (+ ?x 0) => :x
        (* ?x 1) => :x
        """
        result = load_dsl_rules(text)
        self.assertEqual(len(result), 2)
        # Returns [pattern, skeleton] pairs
        self.assertEqual(result[0][0], ['+', ['?', 'x'], 0])
        self.assertEqual(result[0][1], [':', 'x'])


class TestRoundTrip(unittest.TestCase):
    """Test parsing and formatting round-trips."""

    def test_simple_roundtrip(self):
        """Test simple rule round-trip."""
        original = "(+ ?x 0) => :x"
        parsed = parse_rule_line(original)
        formatted = format_dsl_rule(parsed)
        self.assertEqual(formatted, original)

    def test_named_roundtrip(self):
        """Test named rule round-trip."""
        original = "@add-zero: (+ ?x 0) => :x"
        parsed = parse_rule_line(original)
        formatted = format_dsl_rule(parsed)
        self.assertEqual(formatted, original)

    def test_typed_roundtrip(self):
        """Test typed match round-trip."""
        original = "(dd ?c:const ?v:var) => 0"
        parsed = parse_rule_line(original)
        formatted = format_dsl_rule(parsed)
        self.assertEqual(formatted, original)


class TestParsedRuleConversion(unittest.TestCase):
    """Test ParsedRule conversion methods."""

    def test_to_pair(self):
        """Test to_pair() method."""
        parsed = ParsedRule(
            pattern=['+', ['?', 'x'], 0],
            skeleton=[':', 'x'],
            name="test"
        )
        result = parsed.to_pair()
        self.assertEqual(result, [['+', ['?', 'x'], 0], [':', 'x']])

    def test_to_rich(self):
        """Test to_rich() method."""
        parsed = ParsedRule(
            pattern=['+', ['?', 'x'], 0],
            skeleton=[':', 'x'],
            name="add-zero",
            description="x + 0 = x"
        )
        result = parsed.to_rich()
        self.assertEqual(result['pattern'], ['+', ['?', 'x'], 0])
        self.assertEqual(result['skeleton'], [':', 'x'])
        self.assertEqual(result['name'], "add-zero")
        self.assertEqual(result['description'], "x + 0 = x")


if __name__ == '__main__':
    unittest.main()
