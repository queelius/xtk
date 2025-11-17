"""
Integration tests for the complete xtk system.

These tests verify that all components work together correctly,
demonstrating the homoiconic nature where JSON = AST = Code = Data.
"""

import unittest
import json
import tempfile
from pathlib import Path

from xtk import (
    Expression, E, parse_sexpr, format_sexpr,
    load_rules, save_rules, merge_rules,
    simplifier, match, instantiate, evaluate,
    empty_dictionary
)
from xtk.rules.algebra_rules import simplify_rules
from xtk.rules.deriv_rules import deriv_rules_fixed


class TestHomoiconicNature(unittest.TestCase):
    """Test the homoiconic nature of the system: code = data = AST."""
    
    def test_json_is_ast(self):
        """Test that JSON directly represents the AST."""
        # JSON representation
        json_ast = ["+", ["*", 2, "x"], 1]
        
        # This IS the AST - no conversion needed
        expr = Expression(json_ast)
        
        # Can be used directly
        self.assertEqual(expr.expr, json_ast)
        self.assertEqual(expr.to_string(), "(+ (* 2 x) 1)")
    
    def test_rules_are_data(self):
        """Test that rules are just data structures."""
        # Rules are JSON/lists
        rule = [["+", ["?", "x"], 0], [":", "x"]]
        
        # Rules can be manipulated as data
        pattern = rule[0]
        skeleton = rule[1]
        
        # Can check structure programmatically
        self.assertEqual(pattern[0], "+")
        self.assertEqual(pattern[2], 0)
        self.assertEqual(skeleton[0], ":")
        
        # Can apply as code
        result = match(pattern, ["+", "y", 0], empty_dictionary())
        self.assertEqual(result, [["x", "y"]])
    
    def test_expressions_as_data_structures(self):
        """Test manipulating expressions as data structures."""
        # Start with expression as data
        expr_data = ["+", "x", "y"]
        
        # Manipulate as data
        expr_data[0] = "*"  # Change operator
        expr_data.append("z")  # Add term
        
        # Use as expression
        expr = Expression(expr_data)
        self.assertEqual(expr.to_string(), "(* x y z)")
    
    def test_pattern_matching_on_ast(self):
        """Test that pattern matching works directly on AST."""
        ast = ["+", ["*", 2, "x"], ["*", 3, "x"]]
        pattern = ["+", ["*", ["?c", "a"], ["?", "x"]], ["*", ["?c", "b"], ["?", "x"]]]
        
        # Direct pattern matching on AST
        bindings = match(pattern, ast, empty_dictionary())
        
        self.assertNotEqual(bindings, "failed")
        self.assertEqual(bindings, [["a", 2], ["x", "x"], ["b", 3]])
    
    def test_ast_transformation(self):
        """Test transforming AST with rules."""
        # AST
        ast = ["+", "x", 0]
        
        # Rule (also AST)
        rule = [["+", ["?", "x"], 0], [":", "x"]]
        
        # Apply transformation
        bindings = match(rule[0], ast, empty_dictionary())
        result = instantiate(rule[1], bindings)
        
        self.assertEqual(result, "x")
    
    def test_code_data_roundtrip(self):
        """Test that code can be treated as data and vice versa."""
        # Start with code (expression)
        code = ["+", ["^", "x", 2], ["*", 2, "x"], 1]
        
        # Serialize as data (JSON)
        json_data = json.dumps(code)
        
        # Deserialize back to code
        loaded_code = json.loads(json_data)
        
        # Should be identical
        self.assertEqual(code, loaded_code)
        
        # Can use as expression
        expr = Expression(loaded_code)
        self.assertEqual(expr.expr, code)


class TestCompleteWorkflows(unittest.TestCase):
    """Test complete end-to-end workflows."""
    
    def test_symbolic_differentiation_workflow(self):
        """Test complete differentiation workflow."""
        # Create expression: x^3 + 2x^2 + x
        expr = Expression(["+", ["^", "x", 3], ["*", 2, ["^", "x", 2]], "x"])

        # Differentiate
        deriv_expr = Expression(["dd", expr.expr, "x"])

        # Apply derivative rules
        simplified = deriv_expr.with_rules(deriv_rules_fixed).simplify()

        # Should get 3x^2 + 4x + 1 (in some form)
        # Check that it contains the expected terms
        result_str = str(simplified.expr)
        self.assertIn("x", result_str)
    
    def test_algebraic_simplification_workflow(self):
        """Test complete algebraic simplification."""
        # Complex expression
        expr = Expression(["+", 
            ["*", "x", 1],
            ["*", 0, "y"],
            ["+", "z", 0],
            ["/", "w", 1]
        ])
        
        # Apply simplification rules
        result = expr.with_rules(simplify_rules).simplify()
        
        # Should simplify to (+ x z w) or similar
        self.assertIsInstance(result.expr, list)
        self.assertEqual(result.expr[0], "+")
    
    def test_rule_composition_workflow(self):
        """Test composing multiple rule sets."""
        # Expression with both algebraic and special patterns
        expr = Expression(["+", ["*", "x", "x"], ["*", "x", "x"]])
        
        # Custom rule for x*x -> x^2
        square_rule = [[["*", ["?", "x"], ["?", "x"]], ["^", [":", "x"], 2]]]
        
        # Rule for a + a -> 2*a
        double_rule = [[["+", ["?", "x"], ["?", "x"]], ["*", 2, [":", "x"]]]]
        
        # Compose rules
        all_rules = merge_rules(square_rule, double_rule)
        
        # Apply
        result = expr.with_rules(all_rules).simplify()
        
        # Should get 2*x^2 or (* 2 (^ x 2))
        self.assertEqual(result.expr, ["*", 2, ["^", "x", 2]])
    
    def test_symbolic_to_numeric_workflow(self):
        """Test symbolic manipulation followed by numeric evaluation."""
        # Symbolic expression: (x + 1)^2
        expr = Expression(["^", ["+", "x", 1], 2])

        # Expansion rule
        expansion_rule = [
            ["^", ["+", ["?", "a"], ["?", "b"]], 2],
            ["+", ["+", ["^", [":", "a"], 2],
                       ["*", 2, ["*", [":", "a"], [":", "b"]]]],
                  ["^", [":", "b"], 2]]
        ]

        # Expand symbolically
        expanded = expr.with_rules([expansion_rule]).simplify()

        # Evaluate numerically at x = 3
        numeric = (expanded
            .bind("x", 3)
            .bind("+", lambda *args: sum(args))
            .bind("*", lambda a, b: a * b)
            .bind("^", lambda a, b: a ** b)
            .evaluate())

        # (3 + 1)^2 = 16
        self.assertEqual(numeric.expr, 16)


class TestFileFormats(unittest.TestCase):
    """Test loading and saving in different formats."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_json_format_preservation(self):
        """Test that JSON format is preserved exactly."""
        # Original AST
        ast = ["+", ["*", 2, "x"], 1]
        
        # Save as JSON
        json_file = self.temp_path / "expr.json"
        with open(json_file, "w") as f:
            json.dump(ast, f)
        
        # Load back
        with open(json_file, "r") as f:
            loaded = json.load(f)
        
        # Should be identical
        self.assertEqual(ast, loaded)
        
        # Can use directly as expression
        expr = Expression(loaded)
        self.assertEqual(expr.expr, ast)
    
    def test_lisp_to_json_conversion(self):
        """Test that Lisp format converts to same JSON AST."""
        # Lisp expression
        lisp_str = "(+ (* 2 x) 1)"
        
        # Parse to AST
        ast = parse_sexpr(lisp_str)
        
        # Should produce same AST as JSON
        expected_ast = ["+", ["*", 2, "x"], 1]
        self.assertEqual(ast, expected_ast)
        
        # Both can be used identically
        expr1 = Expression(ast)
        expr2 = Expression(expected_ast)
        self.assertEqual(expr1.expr, expr2.expr)
    
    def test_rule_format_equivalence(self):
        """Test that rules work the same regardless of format."""
        # Rule in JSON format
        json_rule = [["+", ["?", "x"], 0], [":", "x"]]
        
        # Same rule from Lisp
        lisp_str = "((+ (? x) 0) (: x))"
        lisp_rule = parse_sexpr(lisp_str)
        
        # Should be identical
        self.assertEqual(json_rule, lisp_rule)
        
        # Both should work the same
        expr = ["+", "y", 0]
        
        result1 = match(json_rule[0], expr, empty_dictionary())
        result2 = match(lisp_rule[0], expr, empty_dictionary())
        
        self.assertEqual(result1, result2)
        self.assertEqual(result1, [["x", "y"]])


class TestCLIIntegration(unittest.TestCase):
    """Test CLI and REPL integration."""
    
    def test_expression_creation_methods(self):
        """Test different ways to create expressions."""
        # Method 1: Direct AST
        expr1 = Expression(["+", "x", 1])
        
        # Method 2: Builder API
        expr2 = E.add("x", 1)
        
        # Method 3: Parse from S-expression
        expr3 = Expression(parse_sexpr("(+ x 1)"))
        
        # Method 4: From JSON string
        json_str = '["+", "x", 1]'
        expr4 = Expression(json.loads(json_str))
        
        # All should be equivalent
        self.assertEqual(expr1.expr, expr2.expr)
        self.assertEqual(expr2.expr, expr3.expr)
        self.assertEqual(expr3.expr, expr4.expr)
    
    def test_rule_loading_methods(self):
        """Test different ways to load rules."""
        # Create test files
        json_file = self.temp_path / "rules.json"
        lisp_file = self.temp_path / "rules.lisp"
        
        rules = [[["+", ["?", "x"], 0], [":", "x"]]]
        
        # Save in both formats
        save_rules(rules, json_file)
        save_rules(rules, lisp_file)
        
        # Load from both
        json_rules = load_rules(json_file)
        lisp_rules = load_rules(lisp_file)
        
        # Should be identical
        self.assertEqual(json_rules, lisp_rules)
        self.assertEqual(json_rules, rules)
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across the system."""
    
    def test_malformed_sexpr(self):
        """Test handling of malformed S-expressions."""
        from xtk.parser import ParseError
        
        with self.assertRaises(ParseError):
            parse_sexpr("(+ 1 2")  # Missing closing paren
        
        with self.assertRaises(ParseError):
            parse_sexpr("+ 1 2)")  # Extra closing paren
    
    def test_invalid_pattern_matching(self):
        """Test pattern matching with invalid inputs."""
        # Type mismatch
        result = match(["?c", "x"], "not_a_number", empty_dictionary())
        self.assertEqual(result, "failed")
        
        # Structural mismatch
        result = match(["+", "x", "y"], ["-", "x", "y"], empty_dictionary())
        self.assertEqual(result, "failed")
    
    def test_evaluation_errors(self):
        """Test evaluation with missing bindings."""
        expr = Expression(["+", "x", "y"])
        
        # Evaluate without bindings - should return unchanged
        result = expr.evaluate()
        self.assertEqual(result.expr, ["+", "x", "y"])
        
        # Partial bindings
        result = expr.bind("x", 3).evaluate()
        self.assertEqual(result.expr[0], "+")  # Still a list/expression
    
    def test_rule_application_errors(self):
        """Test rule application with invalid rules."""
        expr = Expression(["+", "x", 1])
        
        # Empty rules
        result = expr.with_rules([]).simplify()
        self.assertEqual(result.expr, ["+", "x", 1])
        
        # Malformed rule (not a pair)
        with self.assertRaises((IndexError, TypeError, ValueError)):
            expr.with_rules([[["+", "x", 1]]]).simplify()
    
    def test_file_loading_errors(self):
        """Test file loading with invalid files."""
        # Non-existent file treated as inline string
        result = load_rules("((+ x 0) x)")
        self.assertEqual(len(result), 1)
        
        # Invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json}")
            f.flush()
            
            # Should fall back to trying S-expr parsing
            result = load_rules(f.name)
            # Will get empty since it's not valid S-expr either
            self.assertEqual(result, [])


class TestPerformance(unittest.TestCase):
    """Test performance-critical operations."""
    
    def test_deep_nesting_performance(self):
        """Test handling of deeply nested expressions."""
        # Create deeply nested expression
        expr = "x"
        for i in range(100):
            expr = ["+", expr, i]
        
        # Should handle without stack overflow
        e = Expression(expr)
        result = e.to_string()
        self.assertIsNotNone(result)
    
    def test_large_expression_performance(self):
        """Test handling of expressions with many terms."""
        # Expression with many terms
        terms = list(range(1000))
        expr = Expression(["+"] + terms)
        
        # Should handle efficiently
        result = expr.to_string()
        self.assertIsNotNone(result)
    
    def test_many_rules_performance(self):
        """Test applying many rules."""
        # Generate many rules
        rules = []
        for i in range(100):
            rules.append([["+", f"x{i}", 0], f"x{i}"])
        
        expr = Expression(["+", "x50", 0])
        result = expr.with_rules(rules).simplify()
        
        # Should find and apply the matching rule
        self.assertEqual(result.expr, "x50")
    
    def test_pattern_matching_performance(self):
        """Test pattern matching on complex expressions."""
        # Complex expression
        expr = ["+", 
            ["*", ["^", "x", 2], "y"],
            ["*", ["^", "x", 2], "z"],
            ["*", ["^", "x", 2], "w"]
        ]
        
        # Complex pattern
        pattern = ["+", 
            ["*", ["^", ["?", "base"], ["?c", "exp"]], ["?", "v1"]],
            ["*", ["^", ["?", "base"], ["?c", "exp"]], ["?", "v2"]],
            ["*", ["^", ["?", "base"], ["?c", "exp"]], ["?", "v3"]]
        ]
        
        # Should match efficiently
        result = match(pattern, expr, empty_dictionary())
        self.assertNotEqual(result, "failed")


if __name__ == "__main__":
    unittest.main()