# Integral rules
integral_rules = [
    # Integral of a constant
    # int c dx = c * x
    [["int", ["?c", "c"], ["?v", "x"]]
        ["*", [":", "c"], [":", "x"]]],

    # Integral of a variable
    # int x dx = x^2 / 2
    [["int", ["?", "x"], ["?v", "x"]],
        ["/", ["^", [":", "x"], 2], 2]],

    # Integral of a sum
    # int (f(x) + g(x)) dx = int f(x) dx + int g(x) dx
    [["int", ["+", ["?", "f"], ["?", "g"]], ["?v", "x"]],
        ["+", ["int", [":", "f"], [":", "x"]],
              ["int", [":", "g"], [":", "x"]]]],

    # Exponential integral
    # int exp(f(x)) dx = exp(f(x)) / f'(x)
    [["int", ["exp", ["?", "f"]], ["?v", "x"]],
        ["/", ["exp", [":", "f"]], ["dd", [":", "f"], [":", "x"]]]],

    # Logarithmic integral
    # int log(f(x)) dx = f(x) * log(f(x)) - f(x)
    [["int", ["log", ["?", "f"]], ["?v", "x"]],
        ["-", ["*", [":", "f"], ["log", [":", "f"]]], [":", "f"]]],

    # Integral of a power
    # int x^n dx = x^(n+1) / (n+1)
    [["int", ["^", ["?v", "x"], ["?c", "n"]], ["?", "x"]],
        ["/", ["^", [":", "x"], ["+", [":", "n"], 1]], ["+", [":", "n"], 1]]],

    # Integral of sinewave
    # int sin(x) dx = -cos(x)
    [["int", ["sin", ["?", "x"]], ["?v", "x"]],
        ["-", ["cos", [":", "x"]]]],

    # Integral of cosine
    # int cos(x) dx = sin(x)
    [["int", ["cos", ["?", "x"]], ["?v", "x"]],
        ["sin", [":", "x"]]],

    # Numerical integration
    # int f(x) dx from a to b = sum(f(x_i) * delta_x)
    # we must look to see if the funcgtion is defined
    # in the environment
    [["int", ["?", "f"], ["?c", "a"], ["?c", "b"]]
        [":", lambda f, a, b, env: integrate(f, a, b, env)]],
     
]

def integrate(f, a, b, env):
    from scipy.integrate import quad

    if not callable(f):
        f = env[f]
        if not callable(f):
            return "failed"
    
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return "failed"
    
    if b < a:
        return -quad(f, b, a)[0]
    else:
        return quad(f, a, b)[0]
    
