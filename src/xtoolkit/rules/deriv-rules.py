deriv__rules = [
    # Derivative of a variable with respect to itself is 1
    [["dd", ["?v", "v"], ["?", "v"]], 1],
    # Derivative of a constant is 0
    [["dd", ["?c", "c"], ["?", "v"]], 0],

    # Derivative of a sum distributes: d(f(x) + g(x))/dx = f'(x) + g'(x)
    [["dd", ["+", ["?", "x1"], ["?", "x2"]], ["?", "v"]],
        ["+", ["dd", [":", "x1"], [":", "v"]],
              ["dd", [":", "x2"], [":", "v"]]]],

    # Product rule: d(f(x) * g(x))/dx = f'(x) * g(x) + f(x) * g'(x)
    [["dd", ["*", ["?", "x1"], ["?", "x2"]], ["?", "v"]],
        ["+", ["*", ["dd", [":", "x1"], [":", "v"]], [":", "x2"]],
              ["*", [":", "x1"], ["dd", [":", "x2"], [":", "v"]]]]],

    # Derivative: power rule - d(f(x)^n)/dx = n * f(x)^(n-1) * f'(x)
    [["dd", ["^", ["?", "f"], ["?c", "n"]], ["?", "v"]],
        ["*", ["*", [":", "n"], ["^", [":", "f"], ["-", [":", "n"], 1]]],
              ["dd", [":", "f"], [":", "v"]]]],

    # Derivative: chain rule - d(f(g(x)))/dx = f'(g(x)) * g'(x)
    [["dd", ["?", "f"], ["?", "v"]],
        ["*", ["dd", [":", "f"], [":", "v"]], ["dd", [":", "v"], [":", "v"]]]],

    # Derivative: sin(x) -> cos(x)
    [["dd", ["sin", ["?", "x1"]], ["?v", "v"]], ["cos", [":", "x1"]]],

    # Derivative: cos(x) -> -sin(x)
    [["dd", ["cos", ["?", "x1"]], ["?v", "v"]], ["-", ["sin", [":", "x1"]]]],

    # Derivative: exp(x) -> exp(x)
    [["dd", ["exp", ["?", "x1"]], ["?v", "v"]], ["exp", [":", "x1"]]],

    # Derivative: log(x) -> 1/x
    [["dd", ["log", ["?", "x1"]], ["?v", "v"]], ["/", 1, [":", "x1"]]],

    # Derivative: inverse function rule - d(f^(-1)(x))/dx = 1 / f'(f^(-1)(x))
    [["dd", ["?", "f"], ["?", "v"]],
        ["/", 1, ["dd", [":", "f"], ["?", "v"]]]],

    # Derivative: quotient rule - d(f(x)/g(x))/dx = (f'(x) * g(x) - f(x) * g'(x)) / g(x)^2
    [["dd", ["/", ["?", "f"], ["?", "g"]], ["?v", "v"]],
        ["/", ["-", ["*", ["dd", [":", "f"], [":", "v"]], [":", "g"]],
              ["*", [":", "f"], ["dd", [":", "g"], [":", "v"]]]],
              ["^", [":", "g"], 2]]],

    # Derivative of sinh(x) -> cosh(x)
    [["dd", ["sinh", ["?", "x1"]], ["?v", "v"]], ["cosh", [":", "x1"]]],

    # Derivative of cosh(x) -> sinh(x)
    [["dd", ["cosh", ["?", "x1"]], ["?v", "v"]], ["sinh", [":", "x1"]]],

    # Derivative of error function: erf(x) -> 2/sqrt(pi) * exp(-x^2), where
    # erf(x) = 2/sqrt(pi) * integral from 0 to x of exp(-t^2) dt
    [["dd", ["erf", ["?", "x1"]], ["?v", "v"]],
        ["*", ["/", 2, ["sqrt", "pi"]], ["exp", ["*", ["-", [":", "x1"], 2]]]]],

    # Derivative of gamma function: gamma(x) -> gamma(x) * psi(x), where
    # psi(x) is the digamma function
    [["dd", ["gamma", ["?", "x1"]], ["?v", "v"]],
        ["*", ["gamma", [":", "x1"]], ["psi", [":", "x1"]]]],

    # Derivative of digramma function: psi(x) -> psi(x) + 1/x
    [["dd", ["psi", ["?", "x1"]], ["?v", "v"]],
        ["+", ["psi", [":", "x1"]], ["/", 1, [":", "x1"]]]],

    # Derivative of beta function: beta(x, y) -> beta(x, y) * (psi(x) - psi(x + y))
    [["dd", ["beta", ["?", "x1"], ["?", "x2"]], ["?v", "v"]],
        ["*", ["beta", [":", "x1"], [":", "x2"]],
              ["-", ["psi", [":", "x1"]], ["psi", [":", ["+", "x1", "x2"]]]]]],

    # Suppose we do not know the derivative of a function, we can still
    # differentiate it by using the limit definition of the derivative,
    # but we must make sure it is only triggered when the derivative is
    # not known: lim h -> 0 (f(x + h) - f(x)) / h
    # to represent the function applicatio f(x) and f(x + h), we
    # use an "apply" operator, which is a binary operator that takes
    # the function and the argument as its operands
    # Derivative: limit definition of the derivative
    #    [["dd", ["?", "f"], ["?v", "x"]],
    #       ["lim", ["->", "h", 0], ["/", ["-", [":", "f"],
    #                                           ["f", ["+", "x", "h"]]], 0]]]
]