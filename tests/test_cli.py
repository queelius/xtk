"""Comprehensive test suite for cli.py module."""

import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open, call
from io import StringIO

from xtk.cli import XTKRepl, RuleDSL, parse_expression, format_expression, main


class TestXTKRepl(unittest.TestCase):
    """Test the XTK REPL class."""

    def setUp(self):
        """Set up test REPL instance."""
        # Mock readline to avoid history file operations
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_initialization(self):
        """Test REPL initialization."""
        self.assertEqual(self.repl.history, [])
        self.assertEqual(self.repl.bindings, [])
        self.assertEqual(self.repl.rules, [])
        self.assertEqual(self.repl.variables, {})

    @patch('xtk.cli.readline')
    def test_setup_readline(self, mock_readline):
        """Test readline setup."""
        with patch('xtk.cli.atexit.register') as mock_register:
            repl = XTKRepl()
            mock_readline.parse_and_bind.assert_called_with('tab: complete')
            mock_readline.set_completer.assert_called_once()
            mock_register.assert_called_once()

    def test_complete_commands(self):
        """Test tab completion for commands."""
        # Test completion for 'he'
        self.assertEqual(self.repl.complete('he', 0), 'help')

        # Test completion for 'ex'
        self.assertEqual(self.repl.complete('ex', 0), 'exit')
        self.assertEqual(self.repl.complete('ex', 1), 'expand')

        # Test completion for empty string
        result = self.repl.complete('', 0)
        self.assertIn(result, ['help', 'quit', 'exit', 'clear', 'history',
                               'simplify', 'evaluate', 'differentiate', 'substitute',
                               'expand', 'factor', 'match', 'transform',
                               'load-rules', 'save-rules', 'list-rules',
                               'set', 'get', 'del', 'vars',
                               'latex', 'tree', 'sexpr'])

    def test_complete_variables(self):
        """Test tab completion for variables."""
        self.repl.variables = {'x': 1, 'xyz': 2, 'y': 3}

        # Should complete variable names with $
        self.assertEqual(self.repl.complete('$x', 0), '$x')
        self.assertEqual(self.repl.complete('$x', 1), '$xyz')

    def test_execute_help(self):
        """Test help command execution."""
        with patch('builtins.print') as mock_print:
            self.repl.execute('help')
            # Should print help information
            mock_print.assert_called()
            call_args = str(mock_print.call_args_list)
            self.assertIn('Commands:', call_args)

    def test_execute_quit(self):
        """Test quit command."""
        with self.assertRaises(SystemExit):
            self.repl.execute('quit')

    def test_execute_exit(self):
        """Test exit command."""
        with self.assertRaises(SystemExit):
            self.repl.execute('exit')

    def test_execute_clear(self):
        """Test clear command."""
        self.repl.history = [1, 2, 3]
        self.repl.variables = {'x': 1}

        with patch('builtins.print') as mock_print:
            self.repl.execute('clear')

        self.assertEqual(self.repl.history, [])
        self.assertEqual(self.repl.variables, {})

    def test_execute_history(self):
        """Test history command."""
        self.repl.history = ['expr1', 'expr2', 'expr3']

        with patch('builtins.print') as mock_print:
            self.repl.execute('history')
            # Should print history
            calls = mock_print.call_args_list
            self.assertTrue(any('expr1' in str(call) for call in calls))
            self.assertTrue(any('expr2' in str(call) for call in calls))

    def test_execute_set_variable(self):
        """Test setting variables."""
        with patch('builtins.print') as mock_print:
            self.repl.execute('set x = 42')
            self.assertEqual(self.repl.variables['x'], 42)

            self.repl.execute('set y = [+ 1 2]')
            self.assertEqual(self.repl.variables['y'], ['+', 1, 2])

    def test_execute_get_variable(self):
        """Test getting variables."""
        self.repl.variables = {'x': 42, 'y': ['+', 1, 2]}

        with patch('builtins.print') as mock_print:
            self.repl.execute('get x')
            mock_print.assert_called_with('x = 42')

            self.repl.execute('get y')
            # Should print the expression

    def test_execute_del_variable(self):
        """Test deleting variables."""
        self.repl.variables = {'x': 42}

        with patch('builtins.print') as mock_print:
            self.repl.execute('del x')
            self.assertNotIn('x', self.repl.variables)

    def test_execute_vars(self):
        """Test listing variables."""
        self.repl.variables = {'x': 42, 'y': ['+', 1, 2]}

        with patch('builtins.print') as mock_print:
            self.repl.execute('vars')
            calls = str(mock_print.call_args_list)
            self.assertIn('x', calls)
            self.assertIn('y', calls)

    @patch('builtins.print')
    def test_execute_simplify(self, mock_print):
        """Test simplify command."""
        self.repl.execute('simplify (+ x 0)')
        # Should simplify the expression

    @patch('builtins.print')
    def test_execute_evaluate(self, mock_print):
        """Test evaluate command."""
        self.repl.execute('evaluate (+ 1 2)')
        # Should evaluate the expression

    @patch('builtins.print')
    def test_execute_differentiate(self, mock_print):
        """Test differentiate command."""
        self.repl.execute('differentiate (+ x 1) x')
        # Should differentiate the expression

    @patch('builtins.print')
    def test_execute_substitute(self, mock_print):
        """Test substitute command."""
        self.repl.execute('substitute (+ x y) x 2')
        # Should substitute in the expression

    def test_execute_invalid_command(self):
        """Test handling of invalid commands."""
        with patch('builtins.print') as mock_print:
            self.repl.execute('invalid_command')
            calls = str(mock_print.call_args_list)
            self.assertIn('Unknown command', calls)

    def test_run_interactive(self):
        """Test interactive REPL loop."""
        inputs = ['help', 'quit']
        with patch('builtins.input', side_effect=inputs):
            with patch('builtins.print'):
                with self.assertRaises(SystemExit):
                    self.repl.run()


class TestRuleDSL(unittest.TestCase):
    """Test the Rule DSL class."""

    def setUp(self):
        """Set up test DSL instance."""
        self.dsl = RuleDSL()

    def test_pattern_methods(self):
        """Test pattern creation methods."""
        # Test any pattern
        self.assertEqual(self.dsl.any('x'), ['?', 'x'])

        # Test const pattern
        self.assertEqual(self.dsl.const('c'), ['?c', 'c'])

        # Test var pattern
        self.assertEqual(self.dsl.var('v'), ['?v', 'v'])

    def test_skeleton_methods(self):
        """Test skeleton creation methods."""
        # Test sub (substitution)
        self.assertEqual(self.dsl.sub('x'), [':', 'x'])

    def test_rule_creation(self):
        """Test rule creation."""
        pattern = self.dsl.any('x')
        skeleton = self.dsl.sub('x')
        rule = self.dsl.rule(pattern, skeleton)
        self.assertEqual(rule, [['?', 'x'], [':', 'x']])

    def test_parse_valid_rule(self):
        """Test parsing valid rule strings."""
        # Simple rule
        rule_str = "(+ ?x 0) -> :x"
        result = self.dsl.parse(rule_str)
        self.assertEqual(result, [['+', ['?', 'x'], 0], [':', 'x']])

        # Rule with constants
        rule_str = "(* ?c:a ?c:b) -> :(* a b)"
        result = self.dsl.parse(rule_str)
        self.assertEqual(result, [['*', ['?c', 'a'], ['?c', 'b']], [':', ['*', 'a', 'b']]])

    def test_parse_invalid_rule(self):
        """Test parsing invalid rule strings."""
        with self.assertRaises(ValueError):
            self.dsl.parse("invalid rule format")

        with self.assertRaises(ValueError):
            self.dsl.parse("(+ x y)")  # Missing arrow

    def test_format_rule(self):
        """Test formatting rules."""
        rule = [['+', ['?', 'x'], 0], [':', 'x']]
        result = self.dsl.format(rule)
        self.assertEqual(result, "(+ ?x 0) -> :x")


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""

    def test_parse_expression(self):
        """Test expression parsing."""
        # S-expression
        result = parse_expression("(+ 1 2)")
        self.assertEqual(result, ['+', 1, 2])

        # Infix expression
        result = parse_expression("1 + 2")
        self.assertEqual(result, ['+', 1, 2])

        # JSON expression
        result = parse_expression('["+", 1, 2]')
        self.assertEqual(result, ['+', 1, 2])

    def test_format_expression(self):
        """Test expression formatting."""
        expr = ['+', 1, 2]

        # Default format (sexpr)
        result = format_expression(expr)
        self.assertEqual(result, "(+ 1 2)")

        # JSON format
        result = format_expression(expr, 'json')
        self.assertEqual(result, '["+", 1, 2]')

        # Infix format
        result = format_expression(expr, 'infix')
        self.assertEqual(result, "1 + 2")


class TestMainFunction(unittest.TestCase):
    """Test the main CLI entry point."""

    @patch('sys.argv', ['xtk', '--help'])
    def test_help_option(self):
        """Test --help option."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
            output = fake_out.getvalue()
            self.assertIn('xtk', output.lower())

    @patch('sys.argv', ['xtk', '--version'])
    @patch('builtins.print')
    def test_version_option(self, mock_print):
        """Test --version option."""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
        mock_print.assert_called()

    @patch('sys.argv', ['xtk', 'eval', '(+ 1 2)'])
    @patch('builtins.print')
    def test_eval_command(self, mock_print):
        """Test eval command."""
        main()
        # Should evaluate and print result

    @patch('sys.argv', ['xtk', 'simplify', '(+ x 0)'])
    @patch('builtins.print')
    def test_simplify_command(self, mock_print):
        """Test simplify command."""
        main()
        # Should simplify and print result

    @patch('sys.argv', ['xtk', 'parse', '(+ 1 2)'])
    @patch('builtins.print')
    def test_parse_command(self, mock_print):
        """Test parse command."""
        main()
        mock_print.assert_called_with('["+", 1, 2]')

    @patch('sys.argv', ['xtk', 'format', '["+", 1, 2]'])
    @patch('builtins.print')
    def test_format_command(self, mock_print):
        """Test format command."""
        main()
        mock_print.assert_called_with('(+ 1 2)')

    @patch('sys.argv', ['xtk', 'format', '["+", 1, 2]', '--format', 'infix'])
    @patch('builtins.print')
    def test_format_command_with_format_option(self, mock_print):
        """Test format command with format option."""
        main()
        mock_print.assert_called_with('1 + 2')

    @patch('sys.argv', ['xtk', 'repl'])
    def test_repl_command(self):
        """Test REPL command."""
        with patch('xtk.cli.XTKRepl') as mock_repl_class:
            mock_repl = MagicMock()
            mock_repl_class.return_value = mock_repl
            main()
            mock_repl.run.assert_called_once()

    @patch('sys.argv', ['xtk', 'batch', 'test.xtk'])
    def test_batch_command(self):
        """Test batch processing command."""
        test_commands = "simplify (+ x 0)\nevaluate (+ 1 2)"

        with patch('builtins.open', mock_open(read_data=test_commands)):
            with patch('xtk.cli.XTKRepl') as mock_repl_class:
                mock_repl = MagicMock()
                mock_repl_class.return_value = mock_repl
                main()
                # Should execute each command
                self.assertEqual(mock_repl.execute.call_count, 2)

    @patch('sys.argv', ['xtk', 'test'])
    @patch('builtins.print')
    def test_test_command(self, mock_print):
        """Test the test command."""
        main()
        # Should run tests and print results
        calls = str(mock_print.call_args_list)
        self.assertIn('Running', calls)

    @patch('sys.argv', ['xtk'])
    def test_no_command(self):
        """Test running with no command (should start REPL)."""
        with patch('xtk.cli.XTKRepl') as mock_repl_class:
            mock_repl = MagicMock()
            mock_repl_class.return_value = mock_repl
            main()
            mock_repl.run.assert_called_once()


class TestExpressionProcessing(unittest.TestCase):
    """Test expression processing in REPL."""

    def setUp(self):
        """Set up test instance."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    @patch('builtins.print')
    def test_process_valid_sexpr(self, mock_print):
        """Test processing valid s-expression."""
        self.repl.execute('(+ 1 2)')
        # Should process the expression

    @patch('builtins.print')
    def test_process_valid_infix(self, mock_print):
        """Test processing valid infix expression."""
        self.repl.execute('1 + 2 * 3')
        # Should process the expression

    @patch('builtins.print')
    def test_process_with_variables(self, mock_print):
        """Test processing expression with variables."""
        self.repl.variables = {'x': 5}
        self.repl.execute('(+ $x 3)')
        # Should substitute variable and process

    @patch('builtins.print')
    def test_process_invalid_expression(self, mock_print):
        """Test processing invalid expression."""
        self.repl.execute('((invalid')
        calls = str(mock_print.call_args_list)
        self.assertIn('Error', calls)


class TestRuleManagement(unittest.TestCase):
    """Test rule management in REPL."""

    def setUp(self):
        """Set up test instance."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    @patch('builtins.print')
    def test_load_rules(self, mock_print):
        """Test loading rules from file."""
        rules_data = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            temp_file = f.name

        try:
            self.repl.execute(f'load-rules {temp_file}')
            self.assertEqual(len(self.repl.rules), 2)
        finally:
            os.unlink(temp_file)

    @patch('builtins.print')
    def test_save_rules(self, mock_print):
        """Test saving rules to file."""
        self.repl.rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            self.repl.execute(f'save-rules {temp_file}')

            with open(temp_file, 'r') as f:
                saved_rules = json.load(f)

            self.assertEqual(saved_rules, self.repl.rules)
        finally:
            os.unlink(temp_file)

    @patch('builtins.print')
    def test_list_rules(self, mock_print):
        """Test listing rules."""
        self.repl.rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]

        self.repl.execute('list-rules')
        calls = str(mock_print.call_args_list)
        self.assertIn('+', calls)
        self.assertIn('*', calls)


if __name__ == '__main__':
    unittest.main()