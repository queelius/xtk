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


class TestXTKReplTreeVisualization(unittest.TestCase):
    """Test tree visualization methods."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_show_tree_with_history(self):
        """Test show_tree with expression in history."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 1])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_tree([])
            # Should print the tree
            mock_print.assert_called_once()

    def test_show_tree_no_history(self):
        """Test show_tree with empty history."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_tree([])
            call_args = str(mock_print.call_args)
            self.assertIn('No expression', call_args)

    def test_show_tree_with_index(self):
        """Test show_tree with specific index."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2]), Expression(['*', 3, 4])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_tree(['0'])
            mock_print.assert_called_once()

    def test_show_tree_with_dollar_ref(self):
        """Test show_tree with $N reference."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_tree(['$0'])
            mock_print.assert_called_once()

    def test_show_tree_with_ans_ref(self):
        """Test show_tree with ans reference."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_tree(['ans'])
            mock_print.assert_called_once()

    def test_build_rich_tree_atom(self):
        """Test build_rich_tree with atom."""
        tree = self.repl.build_rich_tree('x')
        self.assertIsNotNone(tree)

    def test_build_rich_tree_compound(self):
        """Test build_rich_tree with compound expression."""
        tree = self.repl.build_rich_tree(['+', 'x', 1])
        self.assertIsNotNone(tree)

    def test_build_rich_tree_nested(self):
        """Test build_rich_tree with nested expression."""
        tree = self.repl.build_rich_tree(['+', ['*', 'x', 2], ['-', 'y', 1]])
        self.assertIsNotNone(tree)


class TestXTKReplEvaluation(unittest.TestCase):
    """Test evaluation methods."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_evaluate_with_bindings_no_history(self):
        """Test evaluate_with_bindings with empty history."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.evaluate_with_bindings(['x=5'])
            call_args = str(mock_print.call_args)
            self.assertIn('No expression', call_args)

    def test_evaluate_with_bindings_success(self):
        """Test successful evaluation with bindings."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 1])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.evaluate_with_bindings(['x=5'])
            call_args = str(mock_print.call_args_list)
            self.assertIn('Result', call_args)

    def test_evaluate_with_invalid_binding(self):
        """Test evaluation with invalid binding."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 1])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.evaluate_with_bindings(['x=invalid_var'])
            call_args = str(mock_print.call_args_list)
            self.assertIn('Invalid binding', call_args)


class TestXTKReplConstantFolding(unittest.TestCase):
    """Test constant folding toggle."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_toggle_constant_folding(self):
        """Test toggle_constant_folding."""
        # Default should be enabled
        self.assertTrue(self.repl.constant_folding_enabled)

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.toggle_constant_folding()
            self.assertFalse(self.repl.constant_folding_enabled)
            call_args = str(mock_print.call_args)
            self.assertIn('disabled', call_args)

            self.repl.toggle_constant_folding()
            self.assertTrue(self.repl.constant_folding_enabled)


class TestXTKReplRenderAndLatex(unittest.TestCase):
    """Test render and latex methods."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_show_render_no_history(self):
        """Test show_render with empty history."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_render()
            call_args = str(mock_print.call_args)
            self.assertIn('No expression', call_args)

    def test_show_render_with_history(self):
        """Test show_render with expression in history."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['/', 'x', 2])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_render()
            mock_print.assert_called_once()

    def test_show_latex_with_history(self):
        """Test show_latex with expression in history."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['^', 'x', 2])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_latex()
            mock_print.assert_called_once()


class TestXTKReplTrace(unittest.TestCase):
    """Test trace methods."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_show_trace_no_history(self):
        """Test show_trace with empty history."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_trace()
            call_args = str(mock_print.call_args)
            self.assertIn('No expression', call_args)

    def test_show_trace_no_rules(self):
        """Test show_trace with no rules."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 0])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_trace()
            call_args = str(mock_print.call_args)
            self.assertIn('No rules', call_args)

    def test_show_trace_with_rules(self):
        """Test show_trace with rules loaded."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 0])]
        self.repl.rules = [[['+', ['?', 'x'], 0], [':', 'x']]]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_trace()
            # Should print initial, steps, and final
            self.assertTrue(mock_print.called)

    def test_show_trace_explain_no_history(self):
        """Test show_trace_explain with empty history."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_trace_explain()
            call_args = str(mock_print.call_args)
            self.assertIn('No expression', call_args)

    def test_show_trace_explain_no_rules(self):
        """Test show_trace_explain with no rules."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 'x', 0])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_trace_explain()
            call_args = str(mock_print.call_args)
            self.assertIn('No rules', call_args)


class TestXTKReplExplain(unittest.TestCase):
    """Test explain method."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_show_explain_no_rewrite(self):
        """Test show_explain with no rewrite."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_explain()
            call_args = str(mock_print.call_args)
            self.assertIn('No rewrite', call_args)

    def test_show_explain_with_rewrite_info(self):
        """Test show_explain with rewrite info."""
        self.repl.last_rewrite_info = {
            'expression': '(+ x 0)',
            'result': 'x',
            'rule_name': 'identity',
            'rule_description': 'x + 0 = x'
        }

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_explain()
            # Should print the explanation
            self.assertTrue(mock_print.called)


class TestXTKReplRulesManagement(unittest.TestCase):
    """Test rules management methods."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_handle_rules_command_no_args(self):
        """Test handle_rules_command with no args lists rules."""
        with patch.object(self.repl, 'list_rules') as mock_list:
            self.repl.handle_rules_command([])
            mock_list.assert_called_once()

    def test_handle_rules_command_list(self):
        """Test handle_rules_command with list subcommand."""
        with patch.object(self.repl, 'list_rules') as mock_list:
            self.repl.handle_rules_command(['list'])
            mock_list.assert_called_once()

    def test_handle_rules_command_clear(self):
        """Test handle_rules_command with clear subcommand."""
        self.repl.rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
        self.repl.rich_rules = [MagicMock()]

        with patch.object(self.repl.console, 'print'):
            self.repl.handle_rules_command(['clear'])
            self.assertEqual(len(self.repl.rules), 0)
            self.assertEqual(len(self.repl.rich_rules), 0)

    def test_handle_rules_command_load_no_file(self):
        """Test handle_rules_command load without filename."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_command(['load'])
            call_args = str(mock_print.call_args)
            self.assertIn('Usage', call_args)

    def test_handle_rules_command_save_no_file(self):
        """Test handle_rules_command save without filename."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_command(['save'])
            call_args = str(mock_print.call_args)
            self.assertIn('Usage', call_args)

    def test_handle_rules_command_delete_no_index(self):
        """Test handle_rules_command delete without index."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_command(['delete'])
            call_args = str(mock_print.call_args)
            self.assertIn('Usage', call_args)

    def test_handle_rules_command_delete_invalid_index(self):
        """Test handle_rules_command delete with invalid index."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_command(['delete', 'abc'])
            call_args = str(mock_print.call_args)
            self.assertIn('number', call_args)

    def test_handle_rules_command_show_no_index(self):
        """Test handle_rules_command show without index."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_command(['show'])
            call_args = str(mock_print.call_args)
            self.assertIn('Usage', call_args)

    def test_handle_rules_command_show_invalid_index(self):
        """Test handle_rules_command show with invalid index."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_command(['show', 'abc'])
            call_args = str(mock_print.call_args)
            self.assertIn('number', call_args)

    def test_handle_rules_command_unknown(self):
        """Test handle_rules_command with unknown subcommand."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_command(['unknown'])
            call_args = str(mock_print.call_args_list)
            self.assertIn('Unknown subcommand', call_args)

    def test_handle_rules_add_no_skeleton(self):
        """Test handle_rules_add with missing skeleton."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_add('(+ (?v x) 0)')
            call_args = str(mock_print.call_args_list)
            self.assertIn('Usage', call_args)

    def test_handle_rules_add_invalid_pattern(self):
        """Test handle_rules_add with invalid pattern."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.handle_rules_add('not-sexpr skeleton')
            call_args = str(mock_print.call_args_list)
            self.assertIn('Error', call_args)

    def test_add_rule_success(self):
        """Test add_rule successfully adds a rule."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.add_rule('(+ (?v x) 0)', '(: x)')
            self.assertEqual(len(self.repl.rules), 1)
            self.assertEqual(len(self.repl.rich_rules), 1)

    def test_add_rule_invalid(self):
        """Test add_rule with invalid syntax."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.add_rule('invalid', 'syntax')
            # Should print error
            self.assertTrue(mock_print.called)

    def test_delete_rule_success(self):
        """Test delete_rule successfully deletes a rule."""
        self.repl.rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
        self.repl.rich_rules = [MagicMock()]

        with patch.object(self.repl.console, 'print'):
            self.repl.delete_rule(0)
            self.assertEqual(len(self.repl.rules), 0)

    def test_delete_rule_invalid_index(self):
        """Test delete_rule with invalid index."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.delete_rule(99)
            call_args = str(mock_print.call_args_list)
            self.assertIn('Invalid index', call_args)

    def test_show_rule_success(self):
        """Test show_rule shows rule details."""
        from rich.table import Table
        self.repl.rules = [[['+', ['?', 'x'], 0], [':', 'x']]]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_rule(0)
            # Should print a table
            mock_print.assert_called_once()
            call_arg = mock_print.call_args[0][0]
            self.assertIsInstance(call_arg, Table)

    def test_show_rule_invalid_index(self):
        """Test show_rule with invalid index."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.show_rule(99)
            call_args = str(mock_print.call_args_list)
            self.assertIn('Invalid index', call_args)


class TestXTKReplHistoryReference(unittest.TestCase):
    """Test history reference methods."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_get_history_ref_ans(self):
        """Test get_history_ref with ans."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2])]
        result = self.repl.get_history_ref('ans')
        self.assertEqual(result.expr, ['+', 1, 2])

    def test_get_history_ref_dollar_valid(self):
        """Test get_history_ref with valid $N."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2]), Expression(['*', 3, 4])]
        result = self.repl.get_history_ref('$1')
        self.assertEqual(result.expr, ['*', 3, 4])

    def test_get_history_ref_dollar_invalid(self):
        """Test get_history_ref with invalid $N."""
        result = self.repl.get_history_ref('$99')
        self.assertIsNone(result)

    def test_get_history_ref_dollar_non_numeric(self):
        """Test get_history_ref with non-numeric $ref."""
        result = self.repl.get_history_ref('$abc')
        self.assertIsNone(result)

    def test_get_history_ref_unknown(self):
        """Test get_history_ref with unknown reference."""
        result = self.repl.get_history_ref('unknown')
        self.assertIsNone(result)


class TestXTKReplProcessLine(unittest.TestCase):
    """Test process_line edge cases."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_process_line_comment(self):
        """Test process_line skips comments."""
        with patch.object(self.repl, 'process_command') as mock_cmd:
            self.repl.process_line('# this is a comment')
            mock_cmd.assert_not_called()

    def test_process_line_history_ref_valid(self):
        """Test process_line with valid history reference."""
        from xtk.fluent_api import Expression
        self.repl.history = [Expression(['+', 1, 2])]

        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.process_line('ans')
            call_args = str(mock_print.call_args)
            self.assertIn('ans', call_args)

    def test_process_line_history_ref_invalid(self):
        """Test process_line with invalid history reference."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.process_line('$99')
            call_args = str(mock_print.call_args)
            self.assertIn('Invalid reference', call_args)

    def test_process_line_dsl_expression(self):
        """Test process_line with DSL expression."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.process_line('x + 1')
            # Should be parsed and added to history
            self.assertEqual(len(self.repl.history), 1)

    def test_process_line_parse_error(self):
        """Test process_line with parse error."""
        with patch.object(self.repl.console, 'print') as mock_print:
            # Unbalanced parentheses
            self.repl.process_line('(+ 1 2')
            call_args = str(mock_print.call_args)
            self.assertIn('error', call_args.lower())


class TestXTKReplWelcome(unittest.TestCase):
    """Test welcome message."""

    def setUp(self):
        """Set up test REPL."""
        with patch('xtk.cli.readline'):
            with patch('xtk.cli.atexit'):
                self.repl = XTKRepl()

    def test_print_welcome(self):
        """Test print_welcome prints welcome message."""
        with patch.object(self.repl.console, 'print') as mock_print:
            self.repl.print_welcome()
            mock_print.assert_called_once()
            from rich.panel import Panel
            call_arg = mock_print.call_args[0][0]
            self.assertIsInstance(call_arg, Panel)


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