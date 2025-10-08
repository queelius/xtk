"""
Fixed derivative rules for symbolic differentiation.
"""

deriv_rules_fixed = [
    # Basic rules
    # Derivative of a variable with respect to itself is 1
    [["dd", ["?v", "x"], ["?v", "x"]], 1],
    
    # Derivative of a constant is 0
    [["dd", ["?c", "c"], ["?v", "v"]], 0],
    
    # Derivative of a different variable is 0
    [["dd", ["?v", "u"], ["?v", "v"]], 0],  # Only if u != v
    
    # Linear rules
    # Sum rule: d(f + g)/dx = df/dx + dg/dx
    [["dd", ["+", ["?", "f"], ["?", "g"]], ["?v", "v"]],
     ["+", ["dd", [":", "f"], [":", "v"]], ["dd", [":", "g"], [":", "v"]]]],
    
    # Difference rule: d(f - g)/dx = df/dx - dg/dx
    [["dd", ["-", ["?", "f"], ["?", "g"]], ["?v", "v"]],
     ["-", ["dd", [":", "f"], [":", "v"]], ["dd", [":", "g"], [":", "v"]]]],
    
    # Constant multiple rule: d(c*f)/dx = c * df/dx
    [["dd", ["*", ["?c", "c"], ["?", "f"]], ["?v", "v"]],
     ["*", [":", "c"], ["dd", [":", "f"], [":", "v"]]]],
    
    # Product rule
    # Product rule: d(f*g)/dx = f'*g + f*g'
    [["dd", ["*", ["?", "f"], ["?", "g"]], ["?v", "v"]],
     ["+", ["*", ["dd", [":", "f"], [":", "v"]], [":", "g"]],
           ["*", [":", "f"], ["dd", [":", "g"], [":", "v"]]]]],
    
    # Quotient rule: d(f/g)/dx = (f'*g - f*g')/g^2
    [["dd", ["/", ["?", "f"], ["?", "g"]], ["?v", "v"]],
     ["/", ["-", ["*", ["dd", [":", "f"], [":", "v"]], [":", "g"]],
                 ["*", [":", "f"], ["dd", [":", "g"], [":", "v"]]]],
           ["^", [":", "g"], 2]]],
    
    # Power rule
    # Power rule for constants: d(x^n)/dx = n*x^(n-1)
    [["dd", ["^", ["?v", "x"], ["?c", "n"]], ["?v", "x"]],
     ["*", [":", "n"], ["^", [":", "x"], ["-", [":", "n"], 1]]]],
    
    # General power rule: d(f^n)/dx = n*f^(n-1)*f'
    [["dd", ["^", ["?", "f"], ["?c", "n"]], ["?v", "v"]],
     ["*", ["*", [":", "n"], ["^", [":", "f"], ["-", [":", "n"], 1]]],
           ["dd", [":", "f"], [":", "v"]]]],
    
    # Exponential and logarithm rules
    # d(e^x)/dx = e^x
    [["dd", ["exp", ["?v", "x"]], ["?v", "x"]], ["exp", [":", "x"]]],
    
    # d(e^f)/dx = e^f * f'
    [["dd", ["exp", ["?", "f"]], ["?v", "v"]],
     ["*", ["exp", [":", "f"]], ["dd", [":", "f"], [":", "v"]]]],
    
    # d(ln(x))/dx = 1/x
    [["dd", ["log", ["?v", "x"]], ["?v", "x"]], ["/", 1, [":", "x"]]],
    
    # d(ln(f))/dx = f'/f
    [["dd", ["log", ["?", "f"]], ["?v", "v"]],
     ["/", ["dd", [":", "f"], [":", "v"]], [":", "f"]]],
    
    # Trigonometric rules
    # d(sin(x))/dx = cos(x)
    [["dd", ["sin", ["?v", "x"]], ["?v", "x"]], ["cos", [":", "x"]]],
    
    # d(sin(f))/dx = cos(f) * f'
    [["dd", ["sin", ["?", "f"]], ["?v", "v"]],
     ["*", ["cos", [":", "f"]], ["dd", [":", "f"], [":", "v"]]]],
    
    # d(cos(x))/dx = -sin(x)
    [["dd", ["cos", ["?v", "x"]], ["?v", "x"]],
     ["-", 0, ["sin", [":", "x"]]]],
    
    # d(cos(f))/dx = -sin(f) * f'
    [["dd", ["cos", ["?", "f"]], ["?v", "v"]],
     ["-", 0, ["*", ["sin", [":", "f"]], ["dd", [":", "f"], [":", "v"]]]]],
    
    # d(tan(x))/dx = sec^2(x) = 1/cos^2(x)
    [["dd", ["tan", ["?v", "x"]], ["?v", "x"]],
     ["/", 1, ["^", ["cos", [":", "x"]], 2]]],
    
    # d(tan(f))/dx = sec^2(f) * f'
    [["dd", ["tan", ["?", "f"]], ["?v", "v"]],
     ["*", ["/", 1, ["^", ["cos", [":", "f"]], 2]], 
           ["dd", [":", "f"], [":", "v"]]]],
    
    # Hyperbolic functions
    # d(sinh(x))/dx = cosh(x)
    [["dd", ["sinh", ["?v", "x"]], ["?v", "x"]], ["cosh", [":", "x"]]],
    
    # d(sinh(f))/dx = cosh(f) * f'
    [["dd", ["sinh", ["?", "f"]], ["?v", "v"]],
     ["*", ["cosh", [":", "f"]], ["dd", [":", "f"], [":", "v"]]]],
    
    # d(cosh(x))/dx = sinh(x)
    [["dd", ["cosh", ["?v", "x"]], ["?v", "x"]], ["sinh", [":", "x"]]],
    
    # d(cosh(f))/dx = sinh(f) * f'
    [["dd", ["cosh", ["?", "f"]], ["?v", "v"]],
     ["*", ["sinh", [":", "f"]], ["dd", [":", "f"], [":", "v"]]]],
    
    # d(tanh(x))/dx = sech^2(x) = 1/cosh^2(x)
    [["dd", ["tanh", ["?v", "x"]], ["?v", "x"]],
     ["/", 1, ["^", ["cosh", [":", "x"]], 2]]],
    
    # d(tanh(f))/dx = sech^2(f) * f'
    [["dd", ["tanh", ["?", "f"]], ["?v", "v"]],
     ["*", ["/", 1, ["^", ["cosh", [":", "f"]], 2]], 
           ["dd", [":", "f"], [":", "v"]]]],
    
    # Inverse trigonometric functions
    # d(arcsin(x))/dx = 1/sqrt(1-x^2)
    [["dd", ["arcsin", ["?v", "x"]], ["?v", "x"]],
     ["/", 1, ["sqrt", ["-", 1, ["^", [":", "x"], 2]]]]],
    
    # d(arccos(x))/dx = -1/sqrt(1-x^2)
    [["dd", ["arccos", ["?v", "x"]], ["?v", "x"]],
     ["-", 0, ["/", 1, ["sqrt", ["-", 1, ["^", [":", "x"], 2]]]]]],
    
    # d(arctan(x))/dx = 1/(1+x^2)
    [["dd", ["arctan", ["?v", "x"]], ["?v", "x"]],
     ["/", 1, ["+", 1, ["^", [":", "x"], 2]]]],
]