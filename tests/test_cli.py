"""Test suite for the actual cli.py module implementation."""

import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open, call
from io import StringIO

from xtk.cli import XTKRepl, main


class TestXTKReplInit(unittest.TestCase):
    """Test XTKRepl initialization."""

    @patch('xtk.cli.readline')
    @patch('xtk.cli.atexit')
    def test_initialization(self, mock_atexit, mock_readline):
        """Test REPL initialization."""
        repl = XTKRepl()

        # Check initial state
        self.assertEqual(repl.history, [])
        self.assertEqual(repl.bindings, [])
        self.assertEqual(repl.rules, [])
        self.assertEqual(repl.variables, {})

        # Check readline setup was called
        mock_readline.parse_and_bind.assert_called_with('tab: complete')
        mock_readline.set_completer.assert_called_once()
        mock_atexit.register.assert_called_once()


class TestXTKReplComplete(unittest.TestCase):
    """Test tab completion functionality."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_complete_commands(self):
        """Test command completion."""
        # Test completion for 'hel'
        result = self.repl.complete('hel', 0)
        self.assertEqual(result, 'help')

        # Test completion for 'ex'
        result1 = self.repl.complete('ex', 0)
        result2 = self.repl.complete('ex', 1)
        self.assertIn(result1, ['exit', 'expand'])
        self.assertIn(result2, ['exit', 'expand'])
        self.assertNotEqual(result1, result2)

    def test_complete_empty_string(self):
        """Test completion with empty string."""
        result = self.repl.complete('', 0)
        self.assertIsNotNone(result)
        # Should return one of the available commands
        self.assertIn(result, [
            'help', 'quit', 'exit', 'clear', 'history',
            'simplify', 'evaluate', 'differentiate', 'substitute',
            'expand', 'factor', 'match', 'transform',
            'load-rules', 'save-rules', 'list-rules',
            'set', 'get', 'del', 'vars',
            'latex', 'tree', 'sexpr'
        ])

    def test_complete_with_variables(self):
        """Test completion includes variables."""
        self.repl.variables = {'x': None, 'xyz': None, 'y': None}

        # Variables should be included in completion options
        options = []
        i = 0
        while True:
            result = self.repl.complete('x', i)
            if result is None:
                break
            options.append(result)
            i += 1

        # Should include both variables and commands starting with 'x'
        self.assertIn('x', options)
        self.assertIn('xyz', options)


class TestXTKReplRun(unittest.TestCase):
    """Test REPL run loop."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    @patch('builtins.input', side_effect=['quit'])
    @patch('builtins.print')
    def test_run_quit_command(self, mock_print, mock_input):
        """Test REPL quits on 'quit' command."""
        self.repl.run()

        # Check welcome message was printed
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Welcome' in call for call in calls))
        self.assertTrue(any('Goodbye' in call for call in calls))

    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    def test_run_exit_command(self, mock_print, mock_input):
        """Test REPL quits on 'exit' command."""
        self.repl.run()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Goodbye' in call for call in calls))

    @patch('builtins.input', side_effect=['', 'quit'])
    @patch('builtins.print')
    def test_run_empty_line(self, mock_print, mock_input):
        """Test REPL handles empty lines."""
        self.repl.run()
        # Should continue without error

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input):
        """Test REPL handles KeyboardInterrupt."""
        with patch('builtins.input', side_effect=[KeyboardInterrupt(), 'quit']):
            self.repl.run()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Use 'quit'" in call for call in calls))

    @patch('builtins.input', side_effect=EOFError())
    @patch('builtins.print')
    def test_run_eof_error(self, mock_print, mock_input):
        """Test REPL handles EOFError."""
        self.repl.run()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Goodbye' in call for call in calls))


class TestXTKReplProcessing(unittest.TestCase):
    """Test line and command processing."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    @patch('builtins.print')
    def test_process_command_line(self, mock_print):
        """Test processing command lines starting with ':'."""
        with patch.object(self.repl, 'process_command') as mock_process_command:
            self.repl.process_line(':help')
            mock_process_command.assert_called_once_with('help')

    @patch('builtins.print')
    def test_process_variable_assignment(self, mock_print):
        """Test processing variable assignments."""
        with patch.object(self.repl, 'set_variable') as mock_set_variable:
            self.repl.process_line('x = 42')
            mock_set_variable.assert_called_once_with('x', '42')

    @patch('builtins.print')
    def test_process_sexpr(self, mock_print):
        """Test processing S-expressions."""
        self.repl.process_line('(+ 1 2)')

        # Check expression was added to history
        self.assertEqual(len(self.repl.history), 1)

        # Check output
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Parsed' in call for call in calls))

    @patch('builtins.print')
    def test_process_command_help(self, mock_print):
        """Test help command."""
        self.repl.process_command('help')

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Available commands' in call for call in calls))

    @patch('os.system')
    def test_process_command_clear(self, mock_system):
        """Test clear command."""
        self.repl.process_command('clear')
        mock_system.assert_called_once()

    @patch('builtins.print')
    def test_process_command_history(self, mock_print):
        """Test history command."""
        # Add some history
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2])]

        self.repl.process_command('history')

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('[0]' in call for call in calls))

    @patch('builtins.print')
    def test_process_command_vars(self, mock_print):
        """Test vars command."""
        from xtk.fluent_api import Expression
        self.repl.variables = {'x': Expression(['+', 1, 2])}

        self.repl.process_command('vars')

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('x =' in call for call in calls))

    @patch('builtins.print')
    def test_process_command_unknown(self, mock_print):
        """Test unknown command."""
        self.repl.process_command('unknown_command')

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Unknown command' in call for call in calls))


class TestXTKReplMethods(unittest.TestCase):
    """Test specific REPL methods."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    @patch('builtins.print')
    def test_show_help(self, mock_print):
        """Test show_help method."""
        self.repl.show_help()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Available commands' in call for call in calls))
        self.assertTrue(any('Expression syntax' in call for call in calls))

    @patch('builtins.print')
    def test_show_history_empty(self, mock_print):
        """Test show_history with no history."""
        self.repl.show_history()

        mock_print.assert_called_with("No history yet")

    @patch('builtins.print')
    def test_show_history_with_items(self, mock_print):
        """Test show_history with items."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2]), Expression(['*', 3, 4])]

        self.repl.show_history()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('[0]' in call for call in calls))
        self.assertTrue(any('[1]' in call for call in calls))

    @patch('builtins.print')
    def test_show_variables_empty(self, mock_print):
        """Test show_variables with no variables."""
        self.repl.show_variables()

        mock_print.assert_called_with("No variables defined")

    @patch('builtins.print')
    def test_show_variables_with_items(self, mock_print):
        """Test show_variables with variables."""
        from xtk.fluent_api import Expression
        self.repl.variables = {'x': Expression(['+', 1, 2])}

        self.repl.show_variables()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('x =' in call for call in calls))

    @patch('builtins.print')
    def test_set_variable_sexpr(self, mock_print):
        """Test setting variable with S-expression."""
        self.repl.set_variable('x', '(+ 1 2)')

        self.assertIn('x', self.repl.variables)
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('x =' in call for call in calls))

    @patch('builtins.print')
    def test_simplify_last_no_history(self, mock_print):
        """Test simplify_last with no history."""
        self.repl.simplify_last()

        mock_print.assert_called_with("No expression to simplify")

    @patch('builtins.print')
    def test_simplify_last_with_history(self, mock_print):
        """Test simplify_last with history."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 0])]
        self.repl.rules = [[['+', ['?', 'x'], 0], [':', 'x']]]

        self.repl.simplify_last()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Simplified' in call for call in calls))
        self.assertEqual(len(self.repl.history), 2)

    @patch('builtins.print')
    def test_differentiate_last_no_history(self, mock_print):
        """Test differentiate_last with no history."""
        self.repl.differentiate_last('x')

        mock_print.assert_called_with("No expression to differentiate")

    @patch('builtins.print')
    def test_show_latex_no_history(self, mock_print):
        """Test show_latex with no history."""
        self.repl.show_latex()

        mock_print.assert_called_with("No expression")

    @patch('builtins.print')
    def test_list_rules_empty(self, mock_print):
        """Test list_rules with no rules."""
        self.repl.list_rules()

        mock_print.assert_called_with("No rules loaded")

    @patch('builtins.print')
    def test_list_rules_with_rules(self, mock_print):
        """Test list_rules with rules."""
        self.repl.rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]

        self.repl.list_rules()

        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('[0]' in call for call in calls))
        self.assertTrue(any('[1]' in call for call in calls))


class TestMainFunction(unittest.TestCase):
    """Test the main CLI entry point."""

    @patch('sys.argv', ['xtk'])
    def test_main_no_args_starts_repl(self):
        """Test main with no args starts REPL."""
        with patch('xtk.cli.XTKRepl') as mock_repl_class:
            mock_repl = MagicMock()
            mock_repl_class.return_value = mock_repl

            main()

            mock_repl_class.assert_called_once()
            mock_repl.run.assert_called_once()

    @patch('sys.argv', ['xtk', '-i'])
    def test_main_interactive_flag(self):
        """Test main with -i flag starts REPL."""
        with patch('xtk.cli.XTKRepl') as mock_repl_class:
            mock_repl = MagicMock()
            mock_repl_class.return_value = mock_repl

            main()

            mock_repl.run.assert_called_once()

    @patch('sys.argv', ['xtk', '(+ 1 2)'])
    @patch('builtins.print')
    def test_main_with_sexpr(self, mock_print):
        """Test main with S-expression."""
        main()

        # Should parse and print the expression
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', '(+ 1 2)', '-f', 'latex'])
    @patch('builtins.print')
    def test_main_with_latex_format(self, mock_print):
        """Test main with LaTeX format."""
        main()

        # Should output in LaTeX format
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', '(+ 1 2)', '-f', 'tree'])
    @patch('builtins.print')
    def test_main_with_tree_format(self, mock_print):
        """Test main with tree format."""
        main()

        # Should output as JSON tree
        calls = mock_print.call_args_list
        if calls:
            output = str(calls[0])
            # Tree format should be indented JSON
            self.assertTrue('[' in output or '{' in output)

    @patch('sys.argv', ['xtk', '(+ x 0)', '-s'])
    @patch('builtins.print')
    def test_main_with_simplify(self, mock_print):
        """Test main with simplify flag."""
        main()

        # Should simplify the expression
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', 'invalid expression'])
    def test_main_with_invalid_expression(self):
        """Test main with invalid expression."""
        with patch('sys.stderr', new=StringIO()):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

    @patch('sys.argv', ['xtk', '(^ x 2)', '-d', 'x'])
    @patch('builtins.print')
    def test_main_with_differentiate(self, mock_print):
        """Test main with differentiate flag."""
        main()

        # Should differentiate the expression
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', '(+ 1 2)', '-e'])
    @patch('builtins.print')
    def test_main_with_evaluate(self, mock_print):
        """Test main with evaluate flag."""
        main()

        # Should evaluate the expression
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)


if __name__ == '__main__':
    unittest.main()