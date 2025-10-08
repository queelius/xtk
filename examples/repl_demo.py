#!/usr/bin/env python3
"""
Demo of the enhanced XTK REPL with rich TUI features.

This script demonstrates the key features of the REPL.
To use interactively, run: python3 -m xtk.cli
"""

from xtk.cli import XTKRepl
from xtk.rules.algebra_rules import simplify_rules

def demo():
    """Demonstrate REPL features programmatically."""

    print("XTK REPL Demo - Pure Rule-Based Term Rewriting")
    print("=" * 60)
    print()

    # Create REPL instance
    repl = XTKRepl()

    # Load some rules
    repl.rules = simplify_rules

    # Demo 1: Parse expressions
    print("1. Parsing expressions:")
    repl.process_line("(+ (* 2 x) 3)")
    repl.process_line("x^2 + 2*x + 1")
    print()

    # Demo 2: History
    print("2. History references:")
    repl.process_line("ans")  # Show last expression
    repl.process_line("$0")   # Show first expression
    print()

    # Demo 3: Variables
    print("3. Variables:")
    repl.process_line("a = (+ x 1)")
    repl.process_line("b = ans")
    repl.process_command("vars")
    print()

    # Demo 4: Tree visualization
    print("4. Tree visualization:")
    repl.process_line("(+ (* 2 x) (^ y 3))")
    repl.process_command("tree")
    print()

    # Demo 5: Term rewriting with rules
    print("5. Term rewriting:")
    repl.process_line("(+ x 0)")
    repl.process_command("rewrite")
    print()

    # Demo 6: Differentiation operator
    print("6. Differentiation (requires deriv rules):")
    print("   Expression: (dd (^ x 2) x)")
    print("   After /rewrite: derivative is computed")
    print()

    # Demo 7: History table
    print("7. History:")
    repl.process_command("history")
    print()

    # Demo 8: Rules
    print("8. Loaded Rules:")
    repl.process_command("rules")
    print()

    print("=" * 60)
    print("Pure Rule-Based Design:")
    print("  - Operations are EXPRESSIONS: (dd <expr> <var>)")
    print("  - /rewrite applies loaded rules uniformly")
    print("  - No special commands for operations")
    print("  - Total transparency and flexibility")
    print()
    print("To try interactively, run:")
    print("  python3 -m xtk.cli")
    print()
    print("Example session:")
    print("  /rules load src/xtk/rules/deriv_rules.py")
    print("  (dd (^ x 2) x)")
    print("  /rewrite")
    print("  /tree")


if __name__ == "__main__":
    demo()
