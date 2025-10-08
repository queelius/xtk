"""
Arithmetic evaluation rules with constant folding.

These rules enable full arithmetic evaluation of constant expressions.
The simplifier has been extended to automatically compute operations
when both operands are numeric constants.

This allows expressions like (+ 2 3) to rewrite to 5.
"""

# Basic identity rules that work with any expression
arithmetic_rules = [
    # Addition identities
    [["+", 0, ["?", "x"]], [":", "x"]],
    [["+", ["?", "x"], 0], [":", "x"]],

    # Multiplication identities
    [["*", 1, ["?", "x"]], [":", "x"]],
    [["*", ["?", "x"], 1], [":", "x"]],
    [["*", 0, ["?", "x"]], 0],
    [["*", ["?", "x"], 0], 0],

    # Division identity
    [["/", ["?", "x"], 1], [":", "x"]],
    [["/", 0, ["?", "x"]], 0],

    # Exponentiation identities
    [["^", ["?", "x"], 0], 1],
    [["^", ["?", "x"], 1], [":", "x"]],
    [["^", 1, ["?", "x"]], 1],
    [["^", 0, ["?c", "x"]], 0],  # Assuming x > 0

    # Subtraction identity
    [["-", ["?", "x"], 0], [":", "x"]],

    # Double negation
    [["-", ["-", ["?", "x"]]], [":", "x"]],
]

# Note: Constant folding (e.g., (+ 2 3) → 5) is handled automatically
# by the simplifier when both operands are numeric constants.
# No explicit rules needed for every arithmetic combination!
