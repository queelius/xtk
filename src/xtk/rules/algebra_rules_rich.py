"""
Algebra rules with rich metadata for explanations.

This file provides algebraic manipulation rules with added metadata
to enable better explanations and educational features.
"""

# Identity rules

add_zero_right = {
    "pattern": ["+", ["?", "x"], 0],
    "skeleton": [":", "x"],
    "name": "add-zero-right",
    "description": "Adding zero to any expression doesn't change it (additive identity)",
    "category": "algebra-identity",
    "examples": ["x + 0 = x", "5 + 0 = 5"]
}

add_zero_left = {
    "pattern": ["+", 0, ["?", "x"]],
    "skeleton": [":", "x"],
    "name": "add-zero-left",
    "description": "Zero plus any expression equals the expression (additive identity)",
    "category": "algebra-identity",
    "examples": ["0 + x = x", "0 + 5 = 5"]
}

mult_one_right = {
    "pattern": ["*", ["?", "x"], 1],
    "skeleton": [":", "x"],
    "name": "mult-one-right",
    "description": "Multiplying any expression by one doesn't change it (multiplicative identity)",
    "category": "algebra-identity",
    "examples": ["x·1 = x", "5·1 = 5"]
}

mult_one_left = {
    "pattern": ["*", 1, ["?", "x"]],
    "skeleton": [":", "x"],
    "name": "mult-one-left",
    "description": "One times any expression equals the expression (multiplicative identity)",
    "category": "algebra-identity",
    "examples": ["1·x = x", "1·5 = 5"]
}

mult_zero_right = {
    "pattern": ["*", ["?", "x"], 0],
    "skeleton": 0,
    "name": "mult-zero-right",
    "description": "Multiplying any expression by zero gives zero",
    "category": "algebra-identity",
    "examples": ["x·0 = 0", "100·0 = 0"]
}

mult_zero_left = {
    "pattern": ["*", 0, ["?", "x"]],
    "skeleton": 0,
    "name": "mult-zero-left",
    "description": "Zero times any expression gives zero",
    "category": "algebra-identity",
    "examples": ["0·x = 0", "0·100 = 0"]
}

div_by_one = {
    "pattern": ["/", ["?", "x"], 1],
    "skeleton": [":", "x"],
    "name": "div-by-one",
    "description": "Dividing any expression by one doesn't change it",
    "category": "algebra-identity",
    "examples": ["x/1 = x", "5/1 = 5"]
}

zero_div_by_any = {
    "pattern": ["/", 0, ["?", "x"]],
    "skeleton": 0,
    "name": "zero-div-by-any",
    "description": "Zero divided by any non-zero expression is zero",
    "category": "algebra-identity",
    "examples": ["0/x = 0", "0/5 = 0"]
}

pow_one = {
    "pattern": ["^", ["?", "x"], 1],
    "skeleton": [":", "x"],
    "name": "pow-one",
    "description": "Any expression to the power of 1 equals itself",
    "category": "algebra-power",
    "examples": ["x^1 = x", "5^1 = 5"]
}

pow_zero = {
    "pattern": ["^", ["?", "x"], 0],
    "skeleton": 1,
    "name": "pow-zero",
    "description": "Any non-zero expression to the power of 0 equals 1",
    "category": "algebra-power",
    "examples": ["x^0 = 1", "5^0 = 1"]
}

# Distributive property

distrib_left = {
    "pattern": ["*", ["?", "a"], ["+", ["?", "x"], ["?", "y"]]],
    "skeleton": ["+", ["*", [":", "a"], [":", "x"]], ["*", [":", "a"], [":", "y"]]],
    "name": "distributive-left",
    "description": "Distribute multiplication over addition from the left: a·(x + y) = a·x + a·y",
    "category": "algebra-distributive",
    "examples": ["2(x + 3) = 2x + 6", "a(b + c) = ab + ac"]
}

distrib_right = {
    "pattern": ["*", ["+", ["?", "x"], ["?", "y"]], ["?", "a"]],
    "skeleton": ["+", ["*", [":", "x"], [":", "a"]], ["*", [":", "y"], [":", "a"]]],
    "name": "distributive-right",
    "description": "Distribute multiplication over addition from the right: (x + y)·a = x·a + y·a",
    "category": "algebra-distributive",
    "examples": ["(x + 3)·2 = x·2 + 3·2", "(b + c)·a = b·a + c·a"]
}

# FOIL (First, Outer, Inner, Last)

foil_rule = {
    "pattern": ["*", ["+", ["?", "a"], ["?", "b"]], ["+", ["?", "c"], ["?", "d"]]],
    "skeleton": ["+", ["+", ["+", ["*", [":", "a"], [":", "c"]],
                                  ["*", [":", "a"], [":", "d"]]],
                                  ["*", [":", "b"], [":", "c"]]],
                                  ["*", [":", "b"], [":", "d"]]],
    "name": "foil-rule",
    "description": "FOIL method for multiplying binomials: (a+b)(c+d) = ac + ad + bc + bd",
    "category": "algebra-expansion",
    "examples": ["(x+1)(x+2) = x² + 2x + x + 2 = x² + 3x + 2"]
}

# Combine like terms

combine_like_terms = {
    "pattern": ["+", ["*", ["?c", "a"], ["?", "x"]], ["*", ["?c", "b"], ["?", "x"]]],
    "skeleton": ["*", ["+", [":", "a"], [":", "b"]], [":", "x"]],
    "name": "combine-like-terms",
    "description": "Combine like terms by factoring: a·x + b·x = (a+b)·x",
    "category": "algebra-factoring",
    "examples": ["3x + 5x = 8x", "2y + 7y = 9y"]
}

# Associativity

assoc_add = {
    "pattern": ["+", ["+", ["?", "x"], ["?", "y"]], ["?", "z"]],
    "skeleton": ["+", [":", "x"], ["+", [":", "y"], [":", "z"]]],
    "name": "assoc-addition",
    "description": "Addition is associative: (x + y) + z = x + (y + z)",
    "category": "algebra-associative",
    "examples": ["(1 + 2) + 3 = 1 + (2 + 3) = 6"]
}

assoc_mult = {
    "pattern": ["*", ["*", ["?", "x"], ["?", "y"]], ["?", "z"]],
    "skeleton": ["*", [":", "x"], ["*", [":", "y"], [":", "z"]]],
    "name": "assoc-multiplication",
    "description": "Multiplication is associative: (x·y)·z = x·(y·z)",
    "category": "algebra-associative",
    "examples": ["(2·3)·4 = 2·(3·4) = 24"]
}

# Power rules

power_of_power = {
    "pattern": ["^", ["^", ["?", "x"], ["?", "a"]], ["?", "b"]],
    "skeleton": ["^", [":", "x"], ["*", [":", "a"], [":", "b"]]],
    "name": "power-of-power",
    "description": "Power of a power: (x^a)^b = x^(a·b)",
    "category": "algebra-power",
    "examples": ["(x²)³ = x^6", "(2³)² = 2^6 = 64"]
}

mult_same_base = {
    "pattern": ["*", ["^", ["?", "x"], ["?", "a"]], ["^", ["?", "x"], ["?", "b"]]],
    "skeleton": ["^", [":", "x"], ["+", [":", "a"], [":", "b"]]],
    "name": "multiply-same-base",
    "description": "Multiplying powers with same base: x^a · x^b = x^(a+b)",
    "category": "algebra-power",
    "examples": ["x²·x³ = x^5", "2³·2² = 2^5 = 32"]
}

div_same_base = {
    "pattern": ["/", ["^", ["?", "x"], ["?", "a"]], ["^", ["?", "x"], ["?", "b"]]],
    "skeleton": ["^", [":", "x"], ["-", [":", "a"], [":", "b"]]],
    "name": "divide-same-base",
    "description": "Dividing powers with same base: x^a / x^b = x^(a-b)",
    "category": "algebra-power",
    "examples": ["x^5/x² = x³", "2^5/2² = 2³ = 8"]
}

# Fraction simplification

cancel_common_factor = {
    "pattern": ["/", ["*", ["?", "a"], ["?", "x"]], ["*", ["?", "b"], ["?", "x"]]],
    "skeleton": ["/", [":", "a"], [":", "b"]],
    "name": "cancel-common-factor",
    "description": "Cancel common factors in numerator and denominator: (a·x)/(b·x) = a/b",
    "category": "algebra-fraction",
    "examples": ["(2x)/(3x) = 2/3", "(5y)/(10y) = 1/2"]
}

# Double negative

double_negative = {
    "pattern": ["-", 0, ["-", 0, ["?", "x"]]],
    "skeleton": [":", "x"],
    "name": "double-negative",
    "description": "Double negative elimination: -(-x) = x",
    "category": "algebra-simplify",
    "examples": ["-(-5) = 5", "-(-x) = x"]
}

# Collect constants in nested operations

collect_mult_const_right = {
    "pattern": ["*", ["?c", "a"], ["*", ["?c", "b"], ["?v", "x"]]],
    "skeleton": ["*", ["*", [":", "a"], [":", "b"]], [":", "x"]],
    "name": "collect-mult-const-right",
    "description": "Collect constants in nested multiplication: a·(b·x) = (a·b)·x",
    "category": "algebra-collect",
    "examples": ["2·(3·x) = 6·x", "5·(2·y) = 10·y"]
}

collect_mult_const_left = {
    "pattern": ["*", ["*", ["?c", "a"], ["?v", "x"]], ["?c", "b"]],
    "skeleton": ["*", ["*", [":", "a"], [":", "b"]], [":", "x"]],
    "name": "collect-mult-const-left",
    "description": "Collect constants in nested multiplication: (a·x)·b = (a·b)·x",
    "category": "algebra-collect",
    "examples": ["(2·x)·3 = 6·x", "(5·y)·2 = 10·y"]
}

collect_add_const_right = {
    "pattern": ["+", ["?c", "a"], ["+", ["?c", "b"], ["?v", "x"]]],
    "skeleton": ["+", ["+", [":", "a"], [":", "b"]], [":", "x"]],
    "name": "collect-add-const-right",
    "description": "Collect constants in nested addition: a+(b+x) = (a+b)+x",
    "category": "algebra-collect",
    "examples": ["2+(3+x) = 5+x", "10+(5+y) = 15+y"]
}

collect_add_const_left = {
    "pattern": ["+", ["+", ["?c", "a"], ["?v", "x"]], ["?c", "b"]],
    "skeleton": ["+", ["+", [":", "a"], [":", "b"]], [":", "x"]],
    "name": "collect-add-const-left",
    "description": "Collect constants in nested addition: (a+x)+b = (a+b)+x",
    "category": "algebra-collect",
    "examples": ["(2+x)+3 = 5+x", "(10+y)+5 = 15+y"]
}

# Export all simplification rules
simplify_rules_rich = [
    # Identities
    add_zero_right, add_zero_left,
    mult_one_right, mult_one_left,
    mult_zero_right, mult_zero_left,
    div_by_one, zero_div_by_any,
    pow_one, pow_zero,
    # Distributive
    distrib_left, distrib_right,
    # Combining
    combine_like_terms,
    # Collect constants - TEMPORARILY DISABLED due to infinite loop with other rules
    # TODO: Fix interaction between collect rules and other algebra rules
    # collect_mult_const_right, collect_mult_const_left,
    # collect_add_const_right, collect_add_const_left,
    # Powers
    power_of_power, mult_same_base, div_same_base,
    # Fractions
    cancel_common_factor,
    # Misc
    double_negative,
]

# Constant collection rules (use separately to avoid loops with other rules)
collect_const_rules_rich = [
    collect_mult_const_right, collect_mult_const_left,
    collect_add_const_right, collect_add_const_left,
]

# Separate associativity rules (use with caution - can cause loops with other rules)
assoc_rules_rich = [
    assoc_add,
    assoc_mult,
]

# Export expansion rules
expand_rules_rich = [
    distrib_left,
    distrib_right,
    foil_rule,
]

# Export factoring rules (reverse of expansion)
factor_rules_rich = [
    combine_like_terms,
]

# Export all rules
algebra_rules_rich = simplify_rules_rich
