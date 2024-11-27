trig_rules = [
    # Simplification: sin(0) -> 0
    [["sin", 0], 0],
    # Simplification: cos(0) -> 1
    [["cos", 0], 1],
    # Simplification: tan(0) -> 0
    [["tan", 0], 0],
    # Simplification: sin(pi) -> 0
    [["sin", "pi"], 0],
    # Simplification: cos(pi) -> -1
    [["cos", "pi"], -1],
    # Simplification: tan(pi) -> 0
    [["tan", "pi"], 0],
    # Simplification: sin(pi/2) -> 1
    [["sin", ["/", "pi", 2]], 1],
    # Simplification: cos(pi/2) -> 0
    [["cos", ["/", "pi", 2]], 0],
    # Simplification: sin^2(x) + cos^2(x) -> 1
    [["+", ["^", ["sin", ["?", "x1"]], 2], ["^", ["cos", ["?", "x1"]], 2]], 1],
    # Simplification: tan(x) -> sin(x) / cos(x)
    [["tan", ["?", "x1"]], ["/", ["sin", [":", "x1"]], ["cos", [":", "x1"]]]],
    # Simplification: cot(x) -> cos(x) / sin(x)
    [["cot", ["?", "x1"]], ["/", ["cos", [":", "x1"]], ["sin", [":", "x1"]]]],
    # Simplification: sec(x) -> 1 / cos(x)
    [["sec", ["?", "x1"]], ["/", 1, ["cos", [":", "x1"]]]],
    # Simplification: csc(x) -> 1 / sin(x)
    [["csc", ["?", "x1"]], ["/", 1, ["sin", [":", "x1"]]]],
    # Simplification: sin(-x) -> -sin(x)
    [["sin", ["-", ["?", "x1"]]], ["-", ["sin", [":", "x1"]]]],
    # Simplification: cos(-x) -> cos(x)
    [["cos", ["-", ["?", "x1"]]], ["cos", [":", "x1"]]],
]
