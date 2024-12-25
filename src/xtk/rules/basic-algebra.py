# Basic algebra rules
algebra_rules = [
    # Simplification: Addition of 0 (right)
    [["+", ["?", "x1"], 0], [":", "x1"]],
    # Simplification: Addition of 0 (left)
    [["+", 0, ["?", "x1"]], [":", "x1"]],
    # Simplification: Multiplication by 1 (right)
    [["*", ["?", "x1"], 1], [":", "x1"]],
    # Simplification: Multiplication by 1 (left)
    [["*", 1, ["?", "x1"]], [":", "x1"]],
    # Simplification: Multiplication by 0 (right)
    [["*", ["?", "x1"], 0], 0],
    # Simplification: Multiplication by 0 (left)
    [["*", 0, ["?", "x1"]], 0],
    # Simplification: Subtraction of 0 (right)
    [["-", ["?", "x1"], 0], [":", "x1"]],
    # Simplification: Subtraction of 0 (left)
    [["-", 0, ["?", "x1"]], ["-", 0, [":", "x1"]]],
    # Simplification: Division by 1
    [["/", ["?", "x1"], 1], [":", "x1"]],
    # Simplification: Power of 0
    [["^", ["?", "x1"], 0], 1],
    # Simplification: Power of 1
    [["^", ["?", "x1"], 1], [":", "x1"]],
    # Simplification: abs(-x) -> abs(x)
    [["abs", ["-", ["?", "x1"]]], ["abs", [":", "x1"]]],
    # Simplification: x1/x1 -> 1, assumming x1 is not 0
    [["/", ["?", "x1"], ["?", "x1"]], 1],
]
