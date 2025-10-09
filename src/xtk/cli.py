"""
Command-line interface and REPL for xtk with rich TUI features.
"""

import argparse
import sys
import os
import readline
import atexit
from typing import Optional, List, Dict, Any
import json

from rich.console import Console
from rich.tree import Tree as RichTree
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

from .fluent_api import Expression, ExpressionBuilder as E
from .parser import parse_sexpr, format_sexpr, dsl_parser
from .rewriter import rewriter
from .step_logger import StepLogger
from .rule_utils import normalize_rules, RichRule
from .explainer import RewriteExplainer


class XTKRepl:
    """Interactive REPL for xtk with rich TUI."""

    def __init__(self):
        self.console = Console()
        self.history = []
        self.bindings = []
        self.rules = []  # Rule pairs for rewriter
        self.rich_rules = []  # Rich rules with metadata
        self.variables = {}
        self.constant_folding_enabled = True  # Toggle for constant folding
        self.last_rewrite_info = None  # Track last rewrite for /explain

        # Setup LLM explainer (defaults to fallback mode if no API key)
        try:
            provider = os.getenv("XTK_LLM_PROVIDER", "none")
            if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
                self.explainer = RewriteExplainer.from_config("anthropic")
            elif provider == "openai" and os.getenv("OPENAI_API_KEY"):
                self.explainer = RewriteExplainer.from_config("openai")
            elif provider == "ollama":
                self.explainer = RewriteExplainer.from_config("ollama")
            else:
                self.explainer = RewriteExplainer.from_config("none")
        except Exception:
            self.explainer = RewriteExplainer.from_config("none")

        self.setup_readline()

    def setup_readline(self):
        """Setup readline for better interaction."""
        histfile = os.path.expanduser('~/.xtk_history')
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            pass
        atexit.register(readline.write_history_file, histfile)

        # Enable tab completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete)

    def complete(self, text, state):
        """Tab completion for commands and variables."""
        commands = [
            'help', 'quit', 'exit', 'clear', 'history',
            'rewrite', 'rw', 'eval', 'tree', 'trace', 'trace-explain',
            'rules', 'vars', 'latex', 'render', 'constant-folding', 'explain'
        ]

        # Add / prefix if user hasn't typed it yet
        if text.startswith('/'):
            options = ['/' + cmd for cmd in commands if cmd.startswith(text[1:])]
        else:
            options = [cmd for cmd in commands if cmd.startswith(text)]

        options.extend([var for var in self.variables if var.startswith(text)])

        if state < len(options):
            return options[state]
        return None

    @property
    def ans(self):
        """Get last result."""
        return self.history[-1] if self.history else None

    def get_history_ref(self, ref: str) -> Optional[Expression]:
        """Get expression from history by reference ($1, $2, ans, etc.)."""
        if ref == 'ans':
            return self.ans
        if ref.startswith('$'):
            try:
                idx = int(ref[1:])
                if 0 <= idx < len(self.history):
                    return self.history[idx]
            except ValueError:
                pass
        return None

    def run(self):
        """Run the REPL."""
        self.print_welcome()

        while True:
            try:
                line = input("xtk> ").strip()

                if not line:
                    continue

                if line in ('quit', 'exit', '/quit', '/exit'):
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                self.process_line(line)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /quit or /exit to leave the REPL[/yellow]")
            except EOFError:
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def print_welcome(self):
        """Print welcome message with rich formatting."""
        welcome = """
# XTK - Expression Toolkit REPL

Type `/help` for available commands

Try:
- `(+ (* 2 x) 3)` - Parse S-expression
- `2*x + 3` - Parse infix notation
- `/tree` - Visualize expression tree
- `/rules load algebra` - Load rewrite rules
        """
        self.console.print(Panel(Markdown(welcome), border_style="cyan"))

    def process_line(self, line: str):
        """Process a single input line."""
        # Skip comments
        if line.startswith('#'):
            return

        # Check for commands
        if line.startswith('/'):
            self.process_command(line[1:])
            return

        # Check for history references
        if line in ('ans',) or line.startswith('$'):
            expr = self.get_history_ref(line)
            if expr:
                self.console.print(f"[cyan]{line}[/cyan] = {expr.to_string()}")
            else:
                self.console.print(f"[red]Invalid reference: {line}[/red]")
            return

        # Check for variable assignment
        if '=' in line and not line.startswith('('):
            parts = line.split('=', 1)
            if len(parts) == 2:
                var_name = parts[0].strip()
                expr_str = parts[1].strip()
                self.set_variable(var_name, expr_str)
                return

        # Parse and display expression
        try:
            # Try parsing as S-expression first
            if line.startswith('('):
                expr = Expression(parse_sexpr(line))
            else:
                # Try parsing as DSL
                expr = Expression(dsl_parser.parse(line))

            # Store in history
            self.history.append(expr)

            # Display result with syntax highlighting
            self.console.print(f"[green]$[{len(self.history)-1}][/green] {expr.to_string()}")

        except Exception as e:
            self.console.print(f"[red]Parse error: {e}[/red]")

    def process_command(self, cmd: str):
        """Process a REPL command."""
        # For rules add, we need to preserve S-expressions
        # So we parse differently
        if cmd.startswith('rules add '):
            # Extract the pattern and skeleton while preserving parentheses
            self.handle_rules_add(cmd[10:])  # Skip 'rules add '
            return

        parts = cmd.split()
        if not parts:
            return

        command = parts[0]
        args = parts[1:]

        if command == 'help':
            self.show_help()
        elif command == 'clear':
            os.system('clear' if os.name == 'posix' else 'cls')
        elif command == 'history':
            self.show_history()
        elif command == 'vars':
            self.show_variables()
        elif command in ('rewrite', 'rw'):
            self.rewrite_last()
        elif command == 'eval':
            self.evaluate_with_bindings(args)
        elif command == 'tree':
            self.show_tree(args)
        elif command == 'trace':
            self.show_trace()
        elif command == 'trace-explain':
            self.show_trace_explain()
        elif command == 'latex':
            self.show_latex()
        elif command == 'render':
            self.show_render()
        elif command == 'explain':
            self.show_explain()
        elif command == 'rules':
            self.handle_rules_command(args)
        elif command == 'constant-folding':
            self.toggle_constant_folding()
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("[yellow]Type /help for available commands[/yellow]")

    def show_help(self):
        """Show help message."""
        help_text = """
# Available Commands

## Term Rewriting
- `/rewrite` or `/rw` - Apply loaded rules to rewrite last expression
- `/trace` - Show step-by-step rewriting trace
- `/trace-explain` - Show trace with natural language explanations
- `/explain` - Explain the last rewrite step in detail

## Evaluation
- `/eval [x=5 y=3]` - Evaluate with variable bindings

## Visualization
- `/tree [index]` - Show ASCII tree of expression
- `/latex` - Show expression in LaTeX format
- `/render` - Show expression as ASCII art (fractions, powers, etc.)

## Rules Management
- `/rules` - List all loaded rules
- `/rules load <file>` - Load rules from file
- `/rules save <file>` - Save rules to file
- `/rules add <pattern> <skeleton>` - Add a new rule
- `/rules delete <index>` - Delete a rule by index
- `/rules show <index>` - Show details of a specific rule
- `/rules clear` - Clear all rules

## History & Variables
- `/history` - Show expression history
- `/vars` - Show defined variables
- `$0`, `$1`, `$2` - Reference history items
- `ans` - Last result

## Misc
- `/clear` - Clear the screen
- `/constant-folding` - Toggle constant folding (currently enabled by default)
- `/help` - Show this help
- `/quit`, `/exit` - Exit the REPL

## Expression Syntax
**S-expressions**: `(+ 1 2)`, `(* x (+ y 3))`
**Infix notation**: `x + 2*y`, `sin(x) + cos(y)`
**Variables**: `a = (+ x 1)`

## Operators
Operations are expressed as functions in expressions:
- `(dd <expr> <var>)` - Derivative of expr w.r.t. var
- `(expand <expr>)` - Expand expression
- `(factor <expr>)` - Factor expression

## Examples
```
# Load rules for differentiation
/rules load src/xtk/rules/deriv_rules.py

# Differentiate x^2 with respect to x
(dd (^ x 2) x)
/rewrite

# View tree structure
/tree

# Load algebra rules and expand
/rules load src/xtk/rules/algebra_rules.py
(expand (* (+ x 1) (+ x 2)))
/rw
```
        """
        self.console.print(Markdown(help_text))

    def show_history(self):
        """Show expression history in a table."""
        if not self.history:
            self.console.print("[yellow]No history yet[/yellow]")
            return

        table = Table(title="Expression History", show_header=True, header_style="bold cyan")
        table.add_column("Ref", style="green", width=6)
        table.add_column("Expression", style="white")

        for i, expr in enumerate(self.history):
            table.add_row(f"${i}", expr.to_string())

        self.console.print(table)

    def show_variables(self):
        """Show defined variables in a table."""
        if not self.variables:
            self.console.print("[yellow]No variables defined[/yellow]")
            return

        table = Table(title="Variables", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="green")
        table.add_column("Value", style="white")

        for name, expr in self.variables.items():
            table.add_row(name, expr.to_string())

        self.console.print(table)

    def set_variable(self, name: str, expr_str: str):
        """Set a variable."""
        try:
            # Check if referencing history
            if expr_str in ('ans',) or expr_str.startswith('$'):
                expr = self.get_history_ref(expr_str)
                if not expr:
                    self.console.print(f"[red]Invalid reference: {expr_str}[/red]")
                    return
            else:
                # Parse expression
                if expr_str.startswith('('):
                    expr = Expression(parse_sexpr(expr_str))
                else:
                    expr = Expression(dsl_parser.parse(expr_str))

            self.variables[name] = expr
            self.console.print(f"[green]{name}[/green] = {expr.to_string()}")
        except Exception as e:
            self.console.print(f"[red]Error setting variable: {e}[/red]")

    def toggle_constant_folding(self):
        """Toggle constant folding on/off."""
        self.constant_folding_enabled = not self.constant_folding_enabled
        status = "[green]enabled[/green]" if self.constant_folding_enabled else "[red]disabled[/red]"
        self.console.print(f"Constant folding is now {status}")

    def rewrite_last(self):
        """Rewrite the last expression using loaded rules."""
        if not self.history:
            self.console.print("[yellow]No expression to rewrite[/yellow]")
            return

        expr = self.history[-1]

        # Allow rewriting even without rules (for constant folding)
        if not self.rules:
            # Use empty rules - constant folding will still work if enabled
            rewritten = expr.with_rules([]).simplify(constant_folding=self.constant_folding_enabled)
        else:
            rewritten = expr.with_rules(self.rules).simplify(constant_folding=self.constant_folding_enabled)

        self.history.append(rewritten)
        self.console.print(f"[cyan]Rewritten:[/cyan] {rewritten.to_string()}")

        # Store info for /explain
        self.last_rewrite_info = {
            'expression': expr.to_string(),
            'result': rewritten.to_string(),
            'rule_name': None,  # We'll try to infer this
            'rule_description': None
        }

        # Try to find which rich rule might have applied
        # This is a simple heuristic - check if result matches any known patterns
        for rich_rule in self.rich_rules:
            if rich_rule.name:
                self.last_rewrite_info['rule_name'] = rich_rule.name
                self.last_rewrite_info['rule_description'] = rich_rule.description
                break  # Use first named rule as a guess

    def evaluate_with_bindings(self, args: List[str]):
        """Evaluate expression with variable bindings."""
        if not self.history:
            self.console.print("[yellow]No expression to evaluate[/yellow]")
            return

        # Parse bindings from args like x=5 y=3
        # XTK uses association lists: [['x', 5], ['y', 3]]
        bindings = []
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=', 1)
                try:
                    bindings.append([name.strip(), eval(value.strip())])
                except:
                    self.console.print(f"[red]Invalid binding: {arg}[/red]")
                    return

        expr = self.history[-1]
        try:
            result = expr.evaluate(bindings)
            self.console.print(f"[cyan]Result:[/cyan] {result}")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

    def show_tree(self, args: List[str]):
        """Show expression tree visualization."""
        # Get expression index if provided
        if args:
            if args[0] == 'ans':
                expr = self.ans
            elif args[0].startswith('$'):
                expr = self.get_history_ref(args[0])
            else:
                try:
                    idx = int(args[0])
                    expr = self.history[idx] if 0 <= idx < len(self.history) else None
                except ValueError:
                    expr = None
        else:
            expr = self.ans

        if not expr:
            self.console.print("[yellow]No expression to show[/yellow]")
            return

        # Build rich tree
        tree = self.build_rich_tree(expr.expr)
        self.console.print(tree)

    def build_rich_tree(self, expr, parent=None):
        """Build a Rich Tree from an expression."""
        if parent is None:
            # Root node
            if isinstance(expr, list) and expr:
                root = RichTree(f"[bold cyan]{expr[0]}[/bold cyan]")
                for child in expr[1:]:
                    self.build_rich_tree(child, root)
                return root
            else:
                return RichTree(f"[green]{expr}[/green]")
        else:
            # Child node
            if isinstance(expr, list) and expr:
                node = parent.add(f"[bold cyan]{expr[0]}[/bold cyan]")
                for child in expr[1:]:
                    self.build_rich_tree(child, node)
            else:
                parent.add(f"[green]{expr}[/green]")

    def show_trace(self):
        """Show step-by-step simplification trace."""
        if not self.history:
            self.console.print("[yellow]No expression to trace[/yellow]")
            return

        if not self.rules:
            self.console.print("[yellow]No rules loaded[/yellow]")
            return

        expr = self.history[-1]

        # Create a step logger to track simplification
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            logger = StepLogger(f.name)

        try:
            # Rewrite with logging
            rewrite_fn = rewriter(self.rules, step_logger=logger, constant_folding=self.constant_folding_enabled)
            result = rewrite_fn(expr.expr)
            logger.save()

            # Display steps
            steps = logger.get_steps()

            self.console.print(Panel("[bold cyan]Rewriting Trace[/bold cyan]", border_style="cyan"))

            for step in steps:
                if step['type'] == 'initial':
                    self.console.print(f"[yellow]Initial:[/yellow] {step['expression']}")
                elif step['type'] == 'rewrite':
                    self.console.print(f"[cyan]Step {step['step']}:[/cyan] {step['after']}")
                    if step.get('rule'):
                        self.console.print(f"  [dim]Rule: {step['rule']}[/dim]")
                elif step['type'] == 'final':
                    self.console.print(f"[green]Final:[/green] {step['expression']}")

        finally:
            # Clean up temp file
            if os.path.exists(logger.output_path):
                os.remove(logger.output_path)

    def show_latex(self):
        """Show last expression in LaTeX."""
        if not self.history:
            self.console.print("[yellow]No expression[/yellow]")
            return

        expr = self.history[-1]
        latex = expr.to_latex()
        self.console.print(Panel(f"[cyan]{latex}[/cyan]", title="LaTeX", border_style="cyan"))

    def show_render(self):
        """Show last expression rendered in ASCII art."""
        if not self.history:
            self.console.print("[yellow]No expression[/yellow]")
            return

        expr = self.history[-1]
        ascii_lines = expr.to_ascii()

        # Display each line with proper formatting
        ascii_output = '\n'.join(ascii_lines)
        self.console.print(Panel(f"[cyan]{ascii_output}[/cyan]", title="ASCII Rendering", border_style="cyan"))

    def show_explain(self):
        """Explain the last rewrite step using LLM if available."""
        if not self.last_rewrite_info:
            self.console.print("[yellow]No rewrite to explain. Run /rewrite first.[/yellow]")
            return

        info = self.last_rewrite_info

        # Get rule metadata if available
        rule_name = info.get('rule_name')
        rule_description = info.get('rule_description')

        self.console.print(Panel("[bold cyan]Rewrite Explanation[/bold cyan]", border_style="cyan"))
        self.console.print(f"[cyan]Expression:[/cyan] {info['expression']}")
        self.console.print(f"[green]Result:[/green] {info['result']}")

        if rule_name:
            self.console.print(f"[yellow]Rule:[/yellow] {rule_name}")

        # Generate explanation
        try:
            explanation = self.explainer.explain_step(
                expression=info['expression'],
                result=info['result'],
                rule_name=rule_name,
                rule_description=rule_description,
                bindings=info.get('bindings'),
                pattern=info.get('pattern'),
                skeleton=info.get('skeleton')
            )

            self.console.print()
            self.console.print(Panel(explanation, title="📖 Explanation", border_style="green"))
        except Exception as e:
            self.console.print(f"[red]Error generating explanation: {e}[/red]")

    def show_trace_explain(self):
        """Show step-by-step trace with explanations."""
        if not self.history:
            self.console.print("[yellow]No expression to trace[/yellow]")
            return

        if not self.rules:
            self.console.print("[yellow]No rules loaded[/yellow]")
            return

        expr = self.history[-1]

        # Create a step logger to track simplification
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            logger = StepLogger(f.name)

        try:
            # Rewrite with logging
            rewrite_fn = rewriter(self.rules, step_logger=logger, constant_folding=self.constant_folding_enabled)
            result = rewrite_fn(expr.expr)
            logger.save()

            # Display steps with explanations
            steps = logger.get_steps()

            self.console.print(Panel("[bold cyan]Rewriting Trace with Explanations[/bold cyan]", border_style="cyan"))

            for i, step in enumerate(steps):
                if step['type'] == 'initial':
                    self.console.print(f"\n[yellow]Initial:[/yellow] {step['expression']}")

                elif step['type'] == 'rewrite':
                    self.console.print(f"\n[cyan]Step {step['step']}:[/cyan] {step['after']}")

                    if step.get('rule'):
                        self.console.print(f"  [dim]Rule: {step['rule']}[/dim]")

                    # Try to get explanation
                    # Find matching rich rule
                    rule_name = None
                    rule_description = None

                    # Try to match this step to a rich rule
                    for rich_rule in self.rich_rules:
                        if rich_rule.name and step.get('rule') and rich_rule.name in step.get('rule', ''):
                            rule_name = rich_rule.name
                            rule_description = rich_rule.description
                            break

                    # Generate explanation for this step
                    try:
                        explanation = self.explainer.explain_step(
                            expression=step.get('before', ''),
                            result=step.get('after', ''),
                            rule_name=rule_name,
                            rule_description=rule_description
                        )
                        self.console.print(f"  [green]💡 {explanation}[/green]")
                    except:
                        pass  # Skip explanation if it fails

                elif step['type'] == 'final':
                    self.console.print(f"\n[green]Final:[/green] {step['expression']}")

        finally:
            # Clean up temp file
            if os.path.exists(logger.output_path):
                os.remove(logger.output_path)

    def handle_rules_command(self, args: List[str]):
        """Handle rules subcommands."""
        if not args:
            # List rules
            self.list_rules()
            return

        subcommand = args[0]

        if subcommand == 'load':
            if len(args) > 1:
                self.load_rules(args[1])
            else:
                self.console.print("[yellow]Usage: /rules load <filename>[/yellow]")

        elif subcommand == 'save':
            if len(args) > 1:
                self.save_rules(args[1])
            else:
                self.console.print("[yellow]Usage: /rules save <filename>[/yellow]")

        elif subcommand == 'clear':
            self.rules.clear()
            self.rich_rules.clear()
            self.console.print("[green]Rules cleared[/green]")

        elif subcommand == 'list':
            self.list_rules()

        elif subcommand == 'add':
            # This is now handled in process_command before splitting
            self.console.print("[yellow]Usage: /rules add <pattern> <skeleton>[/yellow]")
            self.console.print("[dim]Example: /rules add (+ (?v x) 0) (: x)[/dim]")

        elif subcommand == 'delete':
            if len(args) > 1:
                try:
                    index = int(args[1])
                    self.delete_rule(index)
                except ValueError:
                    self.console.print("[red]Index must be a number[/red]")
            else:
                self.console.print("[yellow]Usage: /rules delete <index>[/yellow]")

        elif subcommand == 'show':
            if len(args) > 1:
                try:
                    index = int(args[1])
                    self.show_rule(index)
                except ValueError:
                    self.console.print("[red]Index must be a number[/red]")
            else:
                self.console.print("[yellow]Usage: /rules show <index>[/yellow]")

        else:
            self.console.print(f"[red]Unknown subcommand: {subcommand}[/red]")
            self.console.print("[yellow]Available: load, save, clear, list, add, delete, show[/yellow]")

    def load_rules(self, filename: str):
        """Load rules from a file (JSON or Lisp format)."""
        try:
            from .rule_loader import load_rules
            loaded_rules = load_rules(filename)

            # Normalize to both formats
            rule_pairs, rich_rules = normalize_rules(loaded_rules)

            self.rules.extend(rule_pairs)
            self.rich_rules.extend(rich_rules)

            self.console.print(f"[green]Loaded {len(loaded_rules)} rules from {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error loading rules: {e}[/red]")

    def save_rules(self, filename: str):
        """Save rules to a file."""
        try:
            from .rule_loader import save_rules
            save_rules(self.rules, filename)
            self.console.print(f"[green]Saved {len(self.rules)} rules to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error saving rules: {e}[/red]")

    def handle_rules_add(self, args_str: str):
        """Handle /rules add command with proper S-expression parsing."""
        # Extract pattern and skeleton from the args
        # Pattern is the first S-expression, skeleton is the second
        try:
            # Find the first S-expression (pattern)
            if not args_str.strip().startswith('('):
                raise ValueError("Pattern must be an S-expression starting with (")

            # Count parentheses to find where first S-expression ends
            depth = 0
            pattern_end = 0
            for i, char in enumerate(args_str):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        pattern_end = i + 1
                        break

            if depth != 0:
                raise ValueError("Unbalanced parentheses in pattern")

            pattern_str = args_str[:pattern_end].strip()
            skeleton_str = args_str[pattern_end:].strip()

            if not skeleton_str:
                self.console.print("[yellow]Usage: /rules add <pattern> <skeleton>[/yellow]")
                self.console.print("[dim]Example: /rules add (+ (?v x) 0) (: x)[/dim]")
                return

            self.add_rule(pattern_str, skeleton_str)

        except Exception as e:
            self.console.print(f"[red]Error parsing command: {e}[/red]")
            self.console.print("[dim]Make sure to use S-expression format[/dim]")

    def add_rule(self, pattern_str: str, skeleton_str: str):
        """Add a new rule interactively."""
        try:
            # Parse pattern and skeleton
            pattern = parse_sexpr(pattern_str)
            skeleton = parse_sexpr(skeleton_str)

            # Create rule pair and rich rule
            rule_pair = [pattern, skeleton]
            rich_rule = RichRule(pattern=pattern, skeleton=skeleton)

            # Add to both lists
            self.rules.append(rule_pair)
            self.rich_rules.append(rich_rule)

            self.console.print(f"[green]Added rule {len(self.rules)-1}:[/green]")
            self.console.print(f"  [cyan]{Expression(pattern).to_string()}[/cyan] → [yellow]{Expression(skeleton).to_string()}[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error adding rule: {e}[/red]")
            self.console.print("[dim]Make sure to use S-expression format[/dim]")

    def delete_rule(self, index: int):
        """Delete a rule by index."""
        if 0 <= index < len(self.rules):
            rule = self.rules[index]
            pattern = Expression(rule[0]).to_string()
            skeleton = Expression(rule[1]).to_string()

            del self.rules[index]
            del self.rich_rules[index]

            self.console.print(f"[green]Deleted rule {index}:[/green]")
            self.console.print(f"  [dim]{pattern} → {skeleton}[/dim]")
        else:
            self.console.print(f"[red]Invalid index: {index}[/red]")
            self.console.print(f"[dim]Valid range: 0-{len(self.rules)-1}[/dim]")

    def show_rule(self, index: int):
        """Show detailed information about a specific rule."""
        if 0 <= index < len(self.rules):
            rule = self.rules[index]
            pattern = Expression(rule[0]).to_string()
            skeleton = Expression(rule[1]).to_string()

            table = Table(title=f"Rule {index}", show_header=True, header_style="bold cyan")
            table.add_column("Component", style="white", width=10)
            table.add_column("Value", style="cyan")

            table.add_row("Pattern", pattern)
            table.add_row("Skeleton", skeleton)
            table.add_row("Raw Pattern", str(rule[0]))
            table.add_row("Raw Skeleton", str(rule[1]))

            self.console.print(table)
        else:
            self.console.print(f"[red]Invalid index: {index}[/red]")
            self.console.print(f"[dim]Valid range: 0-{len(self.rules)-1}[/dim]")

    def list_rules(self):
        """List loaded rules in a table."""
        if not self.rules:
            self.console.print("[yellow]No rules loaded[/yellow]")
            return

        table = Table(title=f"Loaded Rules ({len(self.rules)})", show_header=True, header_style="bold cyan")
        table.add_column("Index", style="green", width=6)
        table.add_column("Pattern", style="cyan")
        table.add_column("→", style="white", width=3)
        table.add_column("Skeleton", style="yellow")

        for i, rule in enumerate(self.rules[:20]):  # Show first 20
            try:
                pattern = Expression(rule[0]).to_string()
                skeleton = Expression(rule[1]).to_string()
                table.add_row(str(i), pattern, "→", skeleton)
            except:
                table.add_row(str(i), str(rule[0]), "→", str(rule[1]))

        if len(self.rules) > 20:
            self.console.print(table)
            self.console.print(f"[dim]... and {len(self.rules) - 20} more[/dim]")
        else:
            self.console.print(table)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='xtk - Expression Toolkit')
    parser.add_argument('expression', nargs='?', help='Expression to process')
    parser.add_argument('-s', '--simplify', action='store_true',
                       help='Simplify the expression')
    parser.add_argument('-d', '--differentiate', metavar='VAR',
                       help='Differentiate with respect to VAR')
    parser.add_argument('-e', '--evaluate', action='store_true',
                       help='Evaluate the expression')
    parser.add_argument('-r', '--rules', metavar='FILE',
                       help='Load rules from FILE')
    parser.add_argument('-f', '--format', choices=['sexpr', 'latex', 'tree'],
                       default='sexpr', help='Output format')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Start interactive REPL')

    args = parser.parse_args()

    # Start REPL if interactive or no expression given
    if args.interactive or not args.expression:
        repl = XTKRepl()
        repl.run()
        return

    # Process expression
    console = Console()
    try:
        # Parse expression
        if args.expression.startswith('('):
            expr = Expression(parse_sexpr(args.expression))
        else:
            expr = Expression(dsl_parser.parse(args.expression))

        # Load rules if specified
        if args.rules:
            with open(args.rules, 'r') as f:
                rules = json.loads(f.read())
                expr = expr.with_rules(rules)

        # Process operations
        if args.differentiate:
            expr = expr.differentiate(args.differentiate)

        if args.simplify:
            expr = expr.simplify()

        if args.evaluate:
            expr = expr.evaluate()

        # Output in requested format
        if args.format == 'latex':
            console.print(expr.to_latex())
        elif args.format == 'tree':
            # Use rich tree for console output
            repl = XTKRepl()
            tree = repl.build_rich_tree(expr.expr)
            console.print(tree)
        else:
            console.print(expr.to_string())

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
