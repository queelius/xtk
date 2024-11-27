exp_log_rules = [
    # Simplification: e^f(x) -> exp(f(x))
    [["^", "e", ["?", "x1"]], ["exp", [":", "x1"]]],
    # Simplification: log(1) -> 0
    [["log", 1], 0],
    # Simplification: log(e) -> 1
    [["log", "e"], 1],
    # Simplification: log(exp(x)) -> x
    [["log", ["exp", ["?", "x1"]]], [":", "x1"]],
    # Simplification: exp(log(x)) -> x
    [["exp", ["log", ["?", "x1"]]], [":", "x1"]],
    # Simplification: log(1/x) -> -log(x)
    [["log", ["/", 1, ["?", "x1"]]], ["-", 0, ["log", [":", "x1"]]]],
    # Simplification: log(x*y) -> log(x) + log(y)
    [
        ["log", ["*", ["?", "x1"], ["?", "x2"]]],
        ["+", ["log", [":", "x1"]], ["log", [":", "x2"]]],
    ],
    # Simplification: log(x/y) -> log(x) - log(y)
    [
        ["log", ["/", ["?", "x1"], ["?", "x2"]]],
        ["-", ["log", [":", "x1"]], ["log", [":", "x2"]]],
    ],
    # Simplification: exp(x + y) -> exp(x) * exp(y)
    [
        ["exp", ["+", ["?", "x1"], ["?", "x2"]]],
        ["*", ["exp", [":", "x1"]], ["exp", [":", "x2"]]],
    ],
]
