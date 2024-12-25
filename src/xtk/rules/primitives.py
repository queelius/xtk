import math

primitive_rules = [

    # Simplification: addition by constants
    [["+", ["?c", "c1"], ["?c", "c2"]], [":", lambda c1, c2: c1 + c2]],
    # Simplification: multiplication by constants
    [["*", ["?c", "c1"], ["?c", "c2"]], [":", lambda c1, c2: c1 * c2]],
    # Simplification: subtraction by constants
    [["-", ["?c", "c1"], ["?c", "c2"]], [":", lambda c1, c2: c1 - c2]],
    # Simplification: division by constants
    [["/", ["?c", "c1"], ["?c", "c2"]], [":", lambda c1, c2: c1 / c2]],
    # Simplification: power of constants
    [["^", ["?c", "c1"], ["?c", "c2"]], [":", lambda c1, c2: c1**c2]],
    # Simplification: exponentiation of e
    [["exp", ["?c", "c"]], [":", lambda c: math.exp(c)]],
    # Simplification: logarithm of e
    [["log", ["?c", "c"]], [":", lambda c: math.log(c)]],
    # Simplification: sine of constants
    [["sin", ["?c", "c"]], [":", lambda c: math.sin(c)]],
    # Simplification: cosine of constants
    [["cos", ["?c", "c"]], [":", lambda c: math.cos(c)]],
    # Simplification: absolute value of constants
    [["abs", ["?c", "c"]], [":", lambda c: abs(c)]],

]
