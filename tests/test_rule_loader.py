"""
Comprehensive tests for the rule loader module.
"""

import unittest
import json
import tempfile
from pathlib import Path

from xtk.rule_loader import (
    load_rules, save_rules, parse_rules, merge_rules,
    extract_sexprs, is_rule_format, format_rules_as_lisp
)


class TestExtractSexprs(unittest.TestCase):
    """Test S-expression extraction from text."""
    
    def test_single_sexpr(self):
        """Test extracting a single S-expression."""
        result = extract_sexprs("(+ 1 2)")
        self.assertEqual(result, ["(+ 1 2)"])
    
    def test_multiple_sexprs(self):
        """Test extracting multiple S-expressions."""
        result = extract_sexprs("(+ 1 2) (* 3 4)")
        self.assertEqual(result, ["(+ 1 2)", "(* 3 4)"])
    
    def test_nested_sexprs(self):
        """Test extracting nested S-expressions."""
        result = extract_sexprs("(+ (* 2 3) 4)")
        self.assertEqual(result, ["(+ (* 2 3) 4)"])
    
    def test_with_text_around(self):
        """Test extraction with surrounding text."""
        result = extract_sexprs("text before (+ 1 2) text after")
        self.assertEqual(result, ["(+ 1 2)"])
    
    def test_with_comments(self):
        """Test extraction ignoring comments."""
        text = "; comment\n(+ 1 2)\n; another comment"
        result = extract_sexprs(text)
        self.assertEqual(result, ["(+ 1 2)"])
    
    def test_empty_input(self):
        """Test empty input."""
        self.assertEqual(extract_sexprs(""), [])
        self.assertEqual(extract_sexprs("   "), [])
        self.assertEqual(extract_sexprs("; only comments"), [])
    
    def test_unbalanced_parens(self):
        """Test handling of unbalanced parentheses."""
        # Extra closing paren - should still extract valid part
        result = extract_sexprs("(+ 1 2))")
        self.assertEqual(result, ["(+ 1 2)"])
        
        # Missing closing paren - should not extract
        result = extract_sexprs("(+ 1 2")
        self.assertEqual(result, [])


class TestIsRuleFormat(unittest.TestCase):
    """Test rule format detection."""
    
    def test_valid_rule_format(self):
        """Test valid rule formats."""
        self.assertTrue(is_rule_format([['+', 'x', 0], 'x']))
        self.assertTrue(is_rule_format([['?', 'x'], [':', 'x']]))
        self.assertTrue(is_rule_format([1, 2]))  # Simple pair
    
    def test_invalid_rule_format(self):
        """Test invalid rule formats."""
        self.assertFalse(is_rule_format([]))  # Empty
        self.assertFalse(is_rule_format([1]))  # Single element
        self.assertFalse(is_rule_format([1, 2, 3]))  # Too many elements
        self.assertFalse(is_rule_format('not a list'))  # Not a list


class TestParseRules(unittest.TestCase):
    """Test rule parsing from strings."""
    
    def test_parse_json_rules(self):
        """Test parsing JSON format rules."""
        json_str = '[[["+", ["?", "x"], 0], [":", "x"]]]'
        rules = parse_rules(json_str)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0][0], ['+', ['?', 'x'], 0])
        self.assertEqual(rules[0][1], [':', 'x'])
    
    def test_parse_lisp_complete_rules(self):
        """Test parsing complete Lisp rules."""
        lisp_str = """
        ((+ (? x) 0) (: x))
        ((* (? x) 1) (: x))
        """
        rules = parse_rules(lisp_str)
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0][0], ['+', ['?', 'x'], 0])
        self.assertEqual(rules[0][1], [':', 'x'])
    
    def test_parse_lisp_alternating_format(self):
        """Test parsing alternating pattern/skeleton format."""
        lisp_str = """
        (+ (? x) 0)
        (: x)
        
        (* (? x) 1)
        (: x)
        """
        rules = parse_rules(lisp_str)
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0][0], ['+', ['?', 'x'], 0])
        self.assertEqual(rules[0][1], [':', 'x'])
    
    def test_parse_with_comments(self):
        """Test parsing with comments."""
        lisp_str = """
        ; This is a comment
        ((+ (? x) 0) (: x))  ; inline comment
        // C-style comment
        ((* (? x) 1) (: x))
        """
        rules = parse_rules(lisp_str)
        self.assertEqual(len(rules), 2)
    
    def test_parse_empty(self):
        """Test parsing empty input."""
        self.assertEqual(parse_rules(""), [])
        self.assertEqual(parse_rules("   "), [])
        self.assertEqual(parse_rules("; only comments"), [])
    
    def test_parse_mixed_formats(self):
        """Test that mixed formats don't work."""
        # JSON followed by S-expr shouldn't parse correctly
        mixed = '[[["+", 1, 2], 3]] (+ 4 5)'
        rules = parse_rules(mixed)
        # Mixed formats fail to parse - returns empty list
        self.assertEqual(len(rules), 0)


class TestLoadRules(unittest.TestCase):
    """Test loading rules from various sources."""
    
    def setUp(self):
        """Set up test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_from_list(self):
        """Test loading rules from a list."""
        rules = [[['+', 'x', 0], 'x']]
        result = load_rules(rules)
        self.assertEqual(result, rules)
    
    def test_load_from_json_file(self):
        """Test loading from JSON file."""
        json_file = self.temp_path / "test.json"
        rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
        
        with open(json_file, 'w') as f:
            json.dump(rules, f)
        
        loaded = load_rules(json_file)
        self.assertEqual(loaded, rules)
    
    def test_load_from_lisp_file(self):
        """Test loading from Lisp file."""
        lisp_file = self.temp_path / "test.lisp"
        
        with open(lisp_file, 'w') as f:
            f.write("((+ (? x) 0) (: x))\n")
            f.write("((* (? x) 1) (: x))")
        
        loaded = load_rules(lisp_file)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0][0], ['+', ['?', 'x'], 0])
    
    def test_load_from_string(self):
        """Test loading from inline string."""
        # JSON string
        json_str = '[[["+", ["?", "x"], 0], [":", "x"]]]'
        rules = load_rules(json_str)
        self.assertEqual(len(rules), 1)
        
        # Lisp string
        lisp_str = "((+ (? x) 0) (: x))"
        rules = load_rules(lisp_str)
        self.assertEqual(len(rules), 1)
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        # Should treat as inline string
        result = load_rules("((+ 1 2) 3)")
        self.assertEqual(len(result), 1)
    
    def test_load_auto_detect(self):
        """Test auto-detection of format."""
        # File without extension
        auto_file = self.temp_path / "test"
        
        # Write JSON content
        with open(auto_file, 'w') as f:
            f.write('[[["+", 1, 2], 3]]')
        
        loaded = load_rules(auto_file)
        self.assertEqual(loaded, [[['+', 1, 2], 3]])
        
        # Write Lisp content
        with open(auto_file, 'w') as f:
            f.write('((+ 1 2) 3)')
        
        loaded = load_rules(auto_file)
        self.assertEqual(loaded, [[['+', 1, 2], 3]])
    
    def test_load_empty_file(self):
        """Test loading from empty file."""
        empty_file = self.temp_path / "empty.json"
        with open(empty_file, 'w') as f:
            f.write('[]')
        
        loaded = load_rules(empty_file)
        self.assertEqual(loaded, [])


class TestSaveRules(unittest.TestCase):
    """Test saving rules to files."""
    
    def setUp(self):
        """Set up test directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_as_json(self):
        """Test saving as JSON."""
        json_file = self.temp_path / "output.json"
        save_rules(self.rules, json_file)
        
        # Verify the file was created
        self.assertTrue(json_file.exists())
        
        # Load and verify content
        with open(json_file, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, self.rules)
    
    def test_save_as_lisp(self):
        """Test saving as Lisp."""
        lisp_file = self.temp_path / "output.lisp"
        save_rules(self.rules, lisp_file)
        
        # Verify the file was created
        self.assertTrue(lisp_file.exists())
        
        # Load and verify content
        loaded = load_rules(lisp_file)
        self.assertEqual(loaded, self.rules)
    
    def test_save_format_explicit(self):
        """Test explicit format specification."""
        # Save as JSON with .txt extension
        txt_file = self.temp_path / "output.txt"
        save_rules(self.rules, txt_file, format='json')
        
        with open(txt_file, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, self.rules)
        
        # Save as Lisp with .txt extension
        txt_file2 = self.temp_path / "output2.txt"
        save_rules(self.rules, txt_file2, format='lisp')
        
        loaded = load_rules(txt_file2)
        self.assertEqual(loaded, self.rules)
    
    def test_save_empty_rules(self):
        """Test saving empty rule list."""
        json_file = self.temp_path / "empty.json"
        save_rules([], json_file)
        
        with open(json_file, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, [])


class TestMergeRules(unittest.TestCase):
    """Test rule merging functionality."""
    
    def test_merge_empty(self):
        """Test merging empty rule sets."""
        self.assertEqual(merge_rules(), [])
        self.assertEqual(merge_rules([]), [])
        self.assertEqual(merge_rules([], []), [])
    
    def test_merge_single_set(self):
        """Test merging single rule set."""
        rules = [[['+', 'x', 0], 'x']]
        self.assertEqual(merge_rules(rules), rules)
    
    def test_merge_multiple_sets(self):
        """Test merging multiple rule sets."""
        rules1 = [[['+', 'x', 0], 'x']]
        rules2 = [[['*', 'x', 1], 'x']]
        rules3 = [[['/', 'x', 1], 'x']]
        
        merged = merge_rules(rules1, rules2, rules3)
        self.assertEqual(len(merged), 3)
        self.assertIn(rules1[0], merged)
        self.assertIn(rules2[0], merged)
        self.assertIn(rules3[0], merged)
    
    def test_merge_with_duplicates(self):
        """Test that duplicates are removed."""
        rules1 = [[['+', 'x', 0], 'x'], [['*', 'x', 1], 'x']]
        rules2 = [[['*', 'x', 1], 'x'], [['-', 'x', 0], 'x']]
        
        merged = merge_rules(rules1, rules2)
        self.assertEqual(len(merged), 3)  # Should remove duplicate (* x 1) → x
        
        # Check that each unique rule appears once
        rule_strs = [(str(r[0]), str(r[1])) for r in merged]
        self.assertEqual(len(rule_strs), len(set(rule_strs)))
    
    def test_merge_preserves_order(self):
        """Test that merge preserves relative order."""
        rules1 = [[['+', 'x', 0], 'x']]
        rules2 = [[['*', 'x', 1], 'x']]
        
        merged = merge_rules(rules1, rules2)
        self.assertEqual(merged[0], rules1[0])
        self.assertEqual(merged[1], rules2[0])


class TestFormatRulesAsLisp(unittest.TestCase):
    """Test Lisp formatting of rules."""
    
    def test_format_empty(self):
        """Test formatting empty rules."""
        result = format_rules_as_lisp([])
        self.assertIn("Rules for xtk", result)
    
    def test_format_single_rule(self):
        """Test formatting single rule."""
        rules = [[['+', 'x', 0], 'x']]
        result = format_rules_as_lisp(rules)
        # Pretty-printed format, check for components
        self.assertIn("(+ x 0)", result)
        self.assertIn("x", result)

    def test_format_multiple_rules(self):
        """Test formatting multiple rules."""
        rules = [
            [['+', 'x', 0], 'x'],
            [['*', 'x', 1], 'x']
        ]
        result = format_rules_as_lisp(rules)
        # Pretty-printed format, check for components
        self.assertIn("(+ x 0)", result)
        self.assertIn("(* x 1)", result)
    
    def test_format_complex_rules(self):
        """Test formatting complex rules."""
        rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['dd', ['sin', ['?', 'x']], ['?v', 'y']], ['cos', [':', 'x']]]
        ]
        result = format_rules_as_lisp(rules)
        self.assertIn("(? x)", result)
        self.assertIn("(: x)", result)
        self.assertIn("sin", result)
        self.assertIn("cos", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for rule loading system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_roundtrip_json(self):
        """Test save → load roundtrip for JSON."""
        original = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']],
            [['^', ['?', 'x'], 0], 1]
        ]
        
        json_file = self.temp_path / "roundtrip.json"
        save_rules(original, json_file)
        loaded = load_rules(json_file)
        
        self.assertEqual(loaded, original)
    
    def test_roundtrip_lisp(self):
        """Test save → load roundtrip for Lisp."""
        original = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']],
            [['^', ['?', 'x'], 0], 1]
        ]
        
        lisp_file = self.temp_path / "roundtrip.lisp"
        save_rules(original, lisp_file)
        loaded = load_rules(lisp_file)
        
        self.assertEqual(loaded, original)
    
    def test_cross_format_compatibility(self):
        """Test that rules saved in one format can be loaded in another."""
        original = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]
        
        # Save as JSON
        json_file = self.temp_path / "rules.json"
        save_rules(original, json_file)
        
        # Load and save as Lisp
        loaded_json = load_rules(json_file)
        lisp_file = self.temp_path / "rules.lisp"
        save_rules(loaded_json, lisp_file)
        
        # Load Lisp and compare
        loaded_lisp = load_rules(lisp_file)
        self.assertEqual(loaded_lisp, original)
    
    def test_complex_rule_preservation(self):
        """Test that complex rules are preserved correctly."""
        complex_rules = [
            # Derivative rule
            [['dd', ['sin', ['?', 'x']], ['?v', 'y']], 
             ['*', ['cos', [':', 'x']], ['dd', [':', 'x'], [':', 'y']]]],
            
            # Pattern with multiple variables
            [['+', ['*', ['?c', 'a'], ['?', 'x']], ['*', ['?c', 'b'], ['?', 'x']]], 
             ['*', ['+', [':', 'a'], [':', 'b']], [':', 'x']]],
            
            # Nested patterns
            [['^', ['+', ['?', 'a'], ['?', 'b']], 2],
             ['+', ['+', ['^', [':', 'a'], 2], ['*', 2, ['*', [':', 'a'], [':', 'b']]]], 
                   ['^', [':', 'b'], 2]]]
        ]
        
        # Test both formats
        for ext in ['.json', '.lisp']:
            file = self.temp_path / f"complex{ext}"
            save_rules(complex_rules, file)
            loaded = load_rules(file)
            self.assertEqual(loaded, complex_rules, f"Failed for {ext} format")


if __name__ == '__main__':
    unittest.main()