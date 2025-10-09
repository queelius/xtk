"""
Derivative rules with rich metadata for explanations.

This file provides the same differentiation rules as deriv_rules.py,
but with added metadata (names, descriptions, categories, examples)
to enable better explanations and educational features.
"""

# Basic derivative rules

var_rule = {
    "pattern": ["dd", ["?v", "x"], ["?v", "x"]],
    "skeleton": 1,
    "name": "derivative-of-variable",
    "description": "The derivative of a variable with respect to itself is 1",
    "category": "calculus-basic",
    "examples": ["d/dx(x) = 1", "d/dt(t) = 1"]
}

constant_rule = {
    "pattern": ["dd", ["?c", "c"], ["?v", "v"]],
    "skeleton": 0,
    "name": "derivative-of-constant",
    "description": "The derivative of any constant is 0",
    "category": "calculus-basic",
    "examples": ["d/dx(5) = 0", "d/dx(π) = 0"]
}

different_var_rule = {
    "pattern": ["dd", ["?v", "u"], ["?v", "v"]],
    "skeleton": 0,
    "name": "derivative-different-variable",
    "description": "The derivative of one variable with respect to a different variable is 0",
    "category": "calculus-basic",
    "examples": ["d/dx(y) = 0", "d/dt(x) = 0"]
}

# Linear rules

sum_rule = {
    "pattern": ["dd", ["+", ["?", "f"], ["?", "g"]], ["?v", "v"]],
    "skeleton": ["+", ["dd", [":", "f"], [":", "v"]], ["dd", [":", "g"], [":", "v"]]],
    "name": "sum-rule",
    "description": "The sum rule: the derivative of a sum is the sum of the derivatives",
    "category": "calculus-linear",
    "examples": ["d/dx(f + g) = df/dx + dg/dx"]
}

difference_rule = {
    "pattern": ["dd", ["-", ["?", "f"], ["?", "g"]], ["?v", "v"]],
    "skeleton": ["-", ["dd", [":", "f"], [":", "v"]], ["dd", [":", "g"], [":", "v"]]],
    "name": "difference-rule",
    "description": "The difference rule: the derivative of a difference is the difference of the derivatives",
    "category": "calculus-linear",
    "examples": ["d/dx(f - g) = df/dx - dg/dx"]
}

constant_multiple_rule = {
    "pattern": ["dd", ["*", ["?c", "c"], ["?", "f"]], ["?v", "v"]],
    "skeleton": ["*", [":", "c"], ["dd", [":", "f"], [":", "v"]]],
    "name": "constant-multiple-rule",
    "description": "The constant multiple rule: constants can be pulled out of derivatives",
    "category": "calculus-linear",
    "examples": ["d/dx(c·f) = c·df/dx", "d/dx(5x) = 5"]
}

# Product and quotient rules

product_rule = {
    "pattern": ["dd", ["*", ["?", "f"], ["?", "g"]], ["?v", "v"]],
    "skeleton": ["+", ["*", ["dd", [":", "f"], [":", "v"]], [":", "g"]],
                      ["*", [":", "f"], ["dd", [":", "g"], [":", "v"]]]],
    "name": "product-rule",
    "description": "The product rule: d/dx(f·g) = f'·g + f·g'",
    "category": "calculus-product",
    "examples": ["d/dx(x·sin(x)) = 1·sin(x) + x·cos(x)"]
}

quotient_rule = {
    "pattern": ["dd", ["/", ["?", "f"], ["?", "g"]], ["?v", "v"]],
    "skeleton": ["/", ["-", ["*", ["dd", [":", "f"], [":", "v"]], [":", "g"]],
                            ["*", [":", "f"], ["dd", [":", "g"], [":", "v"]]]],
                      ["^", [":", "g"], 2]],
    "name": "quotient-rule",
    "description": "The quotient rule: d/dx(f/g) = (f'·g - f·g')/g²",
    "category": "calculus-quotient",
    "examples": ["d/dx(sin(x)/x) = (cos(x)·x - sin(x)·1)/x²"]
}

# Power rules

power_rule = {
    "pattern": ["dd", ["^", ["?v", "x"], ["?c", "n"]], ["?v", "x"]],
    "skeleton": ["*", [":", "n"], ["^", [":", "x"], ["-", [":", "n"], 1]]],
    "name": "power-rule",
    "description": "The power rule: d/dx(x^n) = n·x^(n-1)",
    "category": "calculus-power",
    "examples": ["d/dx(x²) = 2x", "d/dx(x³) = 3x²"]
}

general_power_rule = {
    "pattern": ["dd", ["^", ["?", "f"], ["?c", "n"]], ["?v", "v"]],
    "skeleton": ["*", ["*", [":", "n"], ["^", [":", "f"], ["-", [":", "n"], 1]]],
                      ["dd", [":", "f"], [":", "v"]]],
    "name": "general-power-rule",
    "description": "The general power rule with chain rule: d/dx(f^n) = n·f^(n-1)·f'",
    "category": "calculus-power",
    "examples": ["d/dx((x+1)²) = 2(x+1)·1"]
}

# Exponential and logarithmic rules

exp_rule_simple = {
    "pattern": ["dd", ["exp", ["?v", "x"]], ["?v", "x"]],
    "skeleton": ["exp", [":", "x"]],
    "name": "exponential-rule",
    "description": "The derivative of e^x is itself: d/dx(e^x) = e^x",
    "category": "calculus-exponential",
    "examples": ["d/dx(e^x) = e^x"]
}

exp_rule_chain = {
    "pattern": ["dd", ["exp", ["?", "f"]], ["?v", "v"]],
    "skeleton": ["*", ["exp", [":", "f"]], ["dd", [":", "f"], [":", "v"]]],
    "name": "exponential-chain-rule",
    "description": "The exponential rule with chain rule: d/dx(e^f) = e^f·f'",
    "category": "calculus-exponential",
    "examples": ["d/dx(e^(x²)) = e^(x²)·2x"]
}

log_rule_simple = {
    "pattern": ["dd", ["log", ["?v", "x"]], ["?v", "x"]],
    "skeleton": ["/", 1, [":", "x"]],
    "name": "logarithm-rule",
    "description": "The derivative of ln(x) is 1/x",
    "category": "calculus-logarithm",
    "examples": ["d/dx(ln(x)) = 1/x"]
}

log_rule_chain = {
    "pattern": ["dd", ["log", ["?", "f"]], ["?v", "v"]],
    "skeleton": ["/", ["dd", [":", "f"], [":", "v"]], [":", "f"]],
    "name": "logarithm-chain-rule",
    "description": "The logarithm rule with chain rule: d/dx(ln(f)) = f'/f",
    "category": "calculus-logarithm",
    "examples": ["d/dx(ln(x²)) = 2x/x² = 2/x"]
}

# Trigonometric rules

sin_rule_simple = {
    "pattern": ["dd", ["sin", ["?v", "x"]], ["?v", "x"]],
    "skeleton": ["cos", [":", "x"]],
    "name": "sine-rule",
    "description": "The derivative of sin(x) is cos(x)",
    "category": "calculus-trig",
    "examples": ["d/dx(sin(x)) = cos(x)"]
}

sin_rule_chain = {
    "pattern": ["dd", ["sin", ["?", "f"]], ["?v", "v"]],
    "skeleton": ["*", ["cos", [":", "f"]], ["dd", [":", "f"], [":", "v"]]],
    "name": "sine-chain-rule",
    "description": "The sine rule with chain rule: d/dx(sin(f)) = cos(f)·f'",
    "category": "calculus-trig",
    "examples": ["d/dx(sin(2x)) = cos(2x)·2"]
}

cos_rule_simple = {
    "pattern": ["dd", ["cos", ["?v", "x"]], ["?v", "x"]],
    "skeleton": ["-", 0, ["sin", [":", "x"]]],
    "name": "cosine-rule",
    "description": "The derivative of cos(x) is -sin(x)",
    "category": "calculus-trig",
    "examples": ["d/dx(cos(x)) = -sin(x)"]
}

cos_rule_chain = {
    "pattern": ["dd", ["cos", ["?", "f"]], ["?v", "v"]],
    "skeleton": ["-", 0, ["*", ["sin", [":", "f"]], ["dd", [":", "f"], [":", "v"]]]],
    "name": "cosine-chain-rule",
    "description": "The cosine rule with chain rule: d/dx(cos(f)) = -sin(f)·f'",
    "category": "calculus-trig",
    "examples": ["d/dx(cos(x²)) = -sin(x²)·2x"]
}

tan_rule_simple = {
    "pattern": ["dd", ["tan", ["?v", "x"]], ["?v", "x"]],
    "skeleton": ["/", 1, ["^", ["cos", [":", "x"]], 2]],
    "name": "tangent-rule",
    "description": "The derivative of tan(x) is sec²(x) = 1/cos²(x)",
    "category": "calculus-trig",
    "examples": ["d/dx(tan(x)) = sec²(x)"]
}

tan_rule_chain = {
    "pattern": ["dd", ["tan", ["?", "f"]], ["?v", "v"]],
    "skeleton": ["*", ["/", 1, ["^", ["cos", [":", "f"]], 2]],
                      ["dd", [":", "f"], [":", "v"]]],
    "name": "tangent-chain-rule",
    "description": "The tangent rule with chain rule: d/dx(tan(f)) = sec²(f)·f'",
    "category": "calculus-trig",
    "examples": ["d/dx(tan(3x)) = sec²(3x)·3"]
}

# Export all rules
deriv_rules_rich = [
    # Basic
    var_rule,
    constant_rule,
    different_var_rule,
    # Linear
    sum_rule,
    difference_rule,
    constant_multiple_rule,
    # Product/Quotient
    product_rule,
    quotient_rule,
    # Power
    power_rule,
    general_power_rule,
    # Exponential/Log
    exp_rule_simple,
    exp_rule_chain,
    log_rule_simple,
    log_rule_chain,
    # Trigonometric
    sin_rule_simple,
    sin_rule_chain,
    cos_rule_simple,
    cos_rule_chain,
    tan_rule_simple,
    tan_rule_chain,
]

# Also export as individual groups for selective loading
basic_deriv_rules = [var_rule, constant_rule, different_var_rule]
linear_deriv_rules = [sum_rule, difference_rule, constant_multiple_rule]
product_quotient_rules = [product_rule, quotient_rule]
power_deriv_rules = [power_rule, general_power_rule]
exp_log_rules = [exp_rule_simple, exp_rule_chain, log_rule_simple, log_rule_chain]
trig_deriv_rules = [sin_rule_simple, sin_rule_chain, cos_rule_simple, cos_rule_chain, tan_rule_simple, tan_rule_chain]
