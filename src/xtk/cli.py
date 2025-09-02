"""
Command-line interface and REPL for xtk.
"""

import argparse
import sys
import os
import readline
import atexit
from typing import Optional, List
import json

from .fluent_api import Expression, ExpressionBuilder as E
from .parser import parse_sexpr, format_sexpr, dsl_parser
from .rewriter import simplifier


class XTKRepl:
    """Interactive REPL for xtk."""
    
    def __init__(self):
        self.history = []
        self.bindings = []
        self.rules = []
        self.variables = {}
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
            'simplify', 'evaluate', 'differentiate', 'substitute',
            'expand', 'factor', 'match', 'transform',
            'load-rules', 'save-rules', 'list-rules',
            'set', 'get', 'del', 'vars',
            'latex', 'tree', 'sexpr'
        ]
        
        options = [cmd for cmd in commands if cmd.startswith(text)]
        options.extend([var for var in self.variables if var.startswith(text)])
        
        if state < len(options):
            return options[state]
        return None
    
    def run(self):
        """Run the REPL."""
        self.print_welcome()
        
        while True:
            try:
                line = input("xtk> ").strip()
                
                if not line:
                    continue
                
                if line in ('quit', 'exit'):
                    print("Goodbye!")
                    break
                
                self.process_line(line)
                
            except KeyboardInterrupt:
                print("\nUse 'quit' or 'exit' to leave the REPL")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def print_welcome(self):
        """Print welcome message."""
        print("=" * 60)
        print("Welcome to xtk - Expression Toolkit REPL")
        print("Type 'help' for available commands")
        print("=" * 60)
    
    def process_line(self, line: str):
        """Process a single input line."""
        # Check for commands
        if line.startswith(':'):
            self.process_command(line[1:])
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
            
            # Display result
            print(f"Parsed: {expr.to_string()}")
            
            # Try to simplify if we have rules
            if self.rules:
                simplified = expr.with_rules(self.rules).simplify()
                if simplified != expr:
                    print(f"Simplified: {simplified.to_string()}")
        
        except Exception as e:
            print(f"Parse error: {e}")
    
    def process_command(self, cmd: str):
        """Process a REPL command."""
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
        elif command == 'simplify':
            self.simplify_last()
        elif command == 'differentiate':
            if args:
                self.differentiate_last(args[0])
            else:
                print("Usage: :differentiate <variable>")
        elif command == 'latex':
            self.show_latex()
        elif command == 'load-rules':
            if args:
                self.load_rules(args[0])
            else:
                print("Usage: :load-rules <filename>")
        elif command == 'list-rules':
            self.list_rules()
        else:
            print(f"Unknown command: {command}")
    
    def show_help(self):
        """Show help message."""
        print("""
Available commands:
  :help              Show this help message
  :quit, :exit       Exit the REPL
  :clear             Clear the screen
  :history           Show expression history
  :vars              Show defined variables
  :simplify          Simplify the last expression
  :differentiate <var>  Differentiate last expression
  :latex             Show last expression in LaTeX
  :load-rules <file> Load rules from a file
  :list-rules        List loaded rules
  
Expression syntax:
  S-expressions:     (+ 1 2), (* x (+ y 3))
  Infix notation:    x + 2*y, sin(x) + cos(y)
  Variable assignment: a = (+ x 1)
  
Examples:
  (+ (* 2 x) 3)
  2*x + 3
  f = (^ x 2)
  :differentiate x
  :simplify
        """)
    
    def show_history(self):
        """Show expression history."""
        if not self.history:
            print("No history yet")
            return
        
        for i, expr in enumerate(self.history):
            print(f"[{i}] {expr.to_string()}")
    
    def show_variables(self):
        """Show defined variables."""
        if not self.variables:
            print("No variables defined")
            return
        
        for name, expr in self.variables.items():
            print(f"{name} = {expr.to_string()}")
    
    def set_variable(self, name: str, expr_str: str):
        """Set a variable."""
        try:
            if expr_str.startswith('('):
                expr = Expression(parse_sexpr(expr_str))
            else:
                expr = Expression(dsl_parser.parse(expr_str))
            
            self.variables[name] = expr
            print(f"{name} = {expr.to_string()}")
        except Exception as e:
            print(f"Error setting variable: {e}")
    
    def simplify_last(self):
        """Simplify the last expression."""
        if not self.history:
            print("No expression to simplify")
            return
        
        expr = self.history[-1]
        simplified = expr.with_rules(self.rules).simplify()
        print(f"Simplified: {simplified.to_string()}")
        self.history.append(simplified)
    
    def differentiate_last(self, var: str):
        """Differentiate the last expression."""
        if not self.history:
            print("No expression to differentiate")
            return
        
        expr = self.history[-1]
        deriv = expr.differentiate(var)
        print(f"d/d{var}: {deriv.to_string()}")
        self.history.append(deriv)
    
    def show_latex(self):
        """Show last expression in LaTeX."""
        if not self.history:
            print("No expression")
            return
        
        expr = self.history[-1]
        print(f"LaTeX: {expr.to_latex()}")
    
    def load_rules(self, filename: str):
        """Load rules from a file (JSON or Lisp format)."""
        try:
            from .rule_loader import load_rules
            new_rules = load_rules(filename)
            self.rules.extend(new_rules)
            print(f"Loaded {len(new_rules)} rules from {filename}")
        except Exception as e:
            print(f"Error loading rules: {e}")
    
    def list_rules(self):
        """List loaded rules."""
        if not self.rules:
            print("No rules loaded")
            return
        
        for i, rule in enumerate(self.rules):
            pattern = Expression(rule[0]).to_string()
            skeleton = Expression(rule[1]).to_string()
            print(f"[{i}] {pattern} => {skeleton}")


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
            print(expr.to_latex())
        elif args.format == 'tree':
            print(json.dumps(expr.expr, indent=2))
        else:
            print(expr.to_string())
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()