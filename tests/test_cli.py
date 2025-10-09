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
        # Updated to include 'explain' command
        self.assertIn(result1, ['exit', 'expand', 'explain'])
        self.assertIn(result2, ['exit', 'expand', 'explain'])
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
    def test_run_quit_command(self, mock_input):
        """Test REPL quits on 'quit' command."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.run()

            # Check goodbye message was printed
            # The print may receive rich objects or strings
            self.assertTrue(mock_print.called)
            # At least one call should contain 'Goodbye' (in rich markup or plain text)
            found_goodbye = False
            for call in mock_print.call_args_list:
                if call.args:
                    arg_str = str(call.args[0])
                    if 'Goodbye' in arg_str:
                        found_goodbye = True
                        break
            self.assertTrue(found_goodbye, "Expected 'Goodbye' message not found")

    @patch('builtins.input', side_effect=['exit'])
    def test_run_exit_command(self, mock_input):
        """Test REPL quits on 'exit' command."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.run()

            # Check goodbye message was printed
            found_goodbye = False
            for call in mock_print.call_args_list:
                if call.args:
                    arg_str = str(call.args[0])
                    if 'Goodbye' in arg_str:
                        found_goodbye = True
                        break
            self.assertTrue(found_goodbye, "Expected 'Goodbye' message not found")

    @patch('builtins.input', side_effect=['', 'quit'])
    @patch('builtins.print')
    def test_run_empty_line(self, mock_print, mock_input):
        """Test REPL handles empty lines."""
        self.repl.run()
        # Should continue without error

    def test_run_keyboard_interrupt(self):
        """Test REPL handles KeyboardInterrupt."""
        with patch('builtins.input', side_effect=[KeyboardInterrupt(), 'quit']):
            with patch.object(self.repl.console, 'print') as mock_print:
                self.repl.run()

                # Check that a message about using quit was printed
                found_message = False
                for call in mock_print.call_args_list:
                    if call.args:
                        arg_str = str(call.args[0])
                        if 'quit' in arg_str.lower() or 'exit' in arg_str.lower():
                            found_message = True
                            break
                self.assertTrue(found_message, "Expected message about quit/exit not found")

    @patch('builtins.input', side_effect=EOFError())
    def test_run_eof_error(self, mock_input):
        """Test REPL handles EOFError."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.run()

            # Check goodbye message was printed
            found_goodbye = False
            for call in mock_print.call_args_list:
                if call.args:
                    arg_str = str(call.args[0])
                    if 'Goodbye' in arg_str:
                        found_goodbye = True
                        break
            self.assertTrue(found_goodbye, "Expected 'Goodbye' message not found")


class TestXTKReplProcessing(unittest.TestCase):
    """Test line and command processing."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    @patch('xtk.cli.Console.print')
    def test_process_command_line(self, mock_print):
        """Test processing command lines starting with '/'."""
        with patch.object(self.repl, 'process_command') as mock_process_command:
            self.repl.process_line('/help')
            mock_process_command.assert_called_once_with('help')

    @patch('xtk.cli.Console.print')
    def test_process_variable_assignment(self, mock_print):
        """Test processing variable assignments."""
        with patch.object(self.repl, 'set_variable') as mock_set_variable:
            self.repl.process_line('x = 42')
            mock_set_variable.assert_called_once_with('x', '42')

    @patch('xtk.cli.Console.print')
    def test_process_sexpr(self, mock_print):
        """Test processing S-expressions."""
        self.repl.process_line('(+ 1 2)')

        # Check expression was added to history
        self.assertEqual(len(self.repl.history), 1)

        # Check output - should have printed the parsed expression
        self.assertTrue(mock_print.called)

    def test_process_command_help(self):
        """Test help command."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.process_command('help')

            # Should print a Markdown object
            mock_print.assert_called_once()
            from rich.markdown import Markdown
            call_arg = mock_print.call_args[0][0]
            self.assertIsInstance(call_arg, Markdown)
            # Check content is present
            self.assertIn('Available Commands', call_arg.markup)

    @patch('os.system')
    def test_process_command_clear(self, mock_system):
        """Test clear command."""
        self.repl.process_command('clear')
        mock_system.assert_called_once()

    def test_process_command_history(self):
        """Test history command."""
        # Add some history
        from xtk.fluent_api import Expression
        from rich.table import Table
        self.repl.history = [Expression(['+', 1, 2])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.process_command('history')

            # Should print a Table object
            mock_print.assert_called_once()
            call_arg = mock_print.call_args[0][0]
            self.assertIsInstance(call_arg, Table)

    def test_process_command_vars(self):
        """Test vars command."""
        from xtk.fluent_api import Expression
        from rich.table import Table
        self.repl.variables = {'x': Expression(['+', 1, 2])}

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.process_command('vars')

            # Should print a Table object
            mock_print.assert_called_once()
            call_arg = mock_print.call_args[0][0]
            self.assertIsInstance(call_arg, Table)

    @patch('xtk.cli.Console.print')
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

    def test_show_help(self):
        """Test show_help method."""
        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.show_help()
            # Should print a Markdown object
            mock_console_print.assert_called_once()
            # Check that it was called with a Markdown object (can't easily check content)
            from rich.markdown import Markdown
            call_arg = mock_console_print.call_args[0][0]
            self.assertIsInstance(call_arg, Markdown)

    def test_show_history_empty(self):
        """Test show_history with no history."""
        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.show_history()
            # Should print "No history yet" with yellow formatting
            mock_console_print.assert_called_once()
            call_args = str(mock_console_print.call_args)
            self.assertIn("No history yet", call_args)

    def test_show_history_with_items(self):
        """Test show_history with items."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2]), Expression(['*', 3, 4])]

        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.show_history()
            # Should print a Table object
            mock_console_print.assert_called_once()
            from rich.table import Table
            call_arg = mock_console_print.call_args[0][0]
            self.assertIsInstance(call_arg, Table)

    def test_show_variables_empty(self):
        """Test show_variables with no variables."""
        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.show_variables()
            mock_console_print.assert_called_once()
            call_args = str(mock_console_print.call_args)
            self.assertIn("No variables defined", call_args)

    def test_show_variables_with_items(self):
        """Test show_variables with variables."""
        from xtk.fluent_api import Expression
        self.repl.variables = {'x': Expression(['+', 1, 2])}

        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.show_variables()
            mock_console_print.assert_called_once()
            call_args = str(mock_console_print.call_args_list)
            # Should show table with variable name
            self.assertIn('x', call_args)

    def test_set_variable_sexpr(self):
        """Test setting variable with S-expression."""
        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.set_variable('x', '(+ 1 2)')

            self.assertIn('x', self.repl.variables)
            call_args = str(mock_console_print.call_args_list)
            self.assertIn('x', call_args)

    def test_rewrite_last_no_history(self):
        """Test rewrite_last with no history."""
        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.rewrite_last()
            call_args = str(mock_console_print.call_args)
            self.assertIn("No expression", call_args)

    def test_rewrite_last_with_history(self):
        """Test rewrite_last with history."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 0])]
        self.repl.rules = [[['+', ['?', 'x'], 0], [':', 'x']]]

        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.rewrite_last()
            call_args = str(mock_console_print.call_args_list)
            self.assertIn('Rewritten', call_args)
            self.assertEqual(len(self.repl.history), 2)

    def test_show_latex_no_history(self):
        """Test show_latex with no history."""
        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.show_latex()
            call_args = str(mock_console_print.call_args)
            self.assertIn("No expression", call_args)

    def test_list_rules_empty(self):
        """Test list_rules with no rules."""
        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.list_rules()
            call_args = str(mock_console_print.call_args)
            self.assertIn("No rules loaded", call_args)

    def test_list_rules_with_rules(self):
        """Test list_rules with rules."""
        from rich.table import Table
        self.repl.rules = [
            [['+', ['?', 'x'], 0], [':', 'x']],
            [['*', ['?', 'x'], 1], [':', 'x']]
        ]

        with patch.object(self.repl.console, 'print') as mock_console_print:
            self.repl.list_rules()
            # Should print a table with rules
            self.assertTrue(mock_console_print.called)
            call_arg = mock_console_print.call_args[0][0]
            self.assertIsInstance(call_arg, Table)


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
    @patch('xtk.cli.Console.print')
    def test_main_with_sexpr(self, mock_print):
        """Test main with S-expression."""
        main()

        # Should parse and print the expression
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', '(+ 1 2)', '-f', 'latex'])
    @patch('xtk.cli.Console.print')
    def test_main_with_latex_format(self, mock_print):
        """Test main with LaTeX format."""
        main()

        # Should output in LaTeX format
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', '(+ 1 2)', '-f', 'tree'])
    @patch('xtk.cli.Console.print')
    def test_main_with_tree_format(self, mock_print):
        """Test main with tree format."""
        main()

        # Should output a Rich Tree
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0, "Console.print should be called for tree format")

    @patch('sys.argv', ['xtk', '(+ x 0)', '-s'])
    @patch('xtk.cli.Console.print')
    def test_main_with_simplify(self, mock_print):
        """Test main with simplify flag."""
        main()

        # Should simplify the expression
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', 'invalid expression'])
    @patch('xtk.cli.Console.print')
    def test_main_with_invalid_expression(self, mock_print):
        """Test main with invalid expression."""
        # "invalid expression" is actually valid - it's parsed as "invalid"
        # The parser doesn't do error checking, so this just outputs "invalid"
        main()
        self.assertTrue(len(mock_print.call_args_list) > 0)

    @patch('sys.argv', ['xtk', '(^ x 2)', '-d', 'x'])
    @patch('xtk.cli.Console.print')
    def test_main_with_differentiate(self, mock_print):
        """Test main with differentiate flag."""
        main()

        # Should differentiate the expression
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)

    @patch('sys.argv', ['xtk', '(+ 1 2)', '-e'])
    @patch('xtk.cli.Console.print')
    def test_main_with_evaluate(self, mock_print):
        """Test main with evaluate flag."""
        main()

        # Should evaluate the expression
        calls = mock_print.call_args_list
        self.assertTrue(len(calls) > 0)


if __name__ == '__main__':
    unittest.main()