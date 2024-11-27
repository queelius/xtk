# Limit rules

limit_rules = [
    # Limit of a constant
    # lim_x->c a = a
    [["lim", ["->", ["?c", "a"], ["?v", "x"]], ["?c", "a"]]
        [":", "a"]], 
    
    # Limit of a variable
    # lim_x->c x = c
    [["lim", ["->", ["?v", "x"], ["?c", "c"]], ["?", "x"]],
        [":", "c"]],

    # Limit of a sum
    # lim_x->c f(x) + g(x) = lim_x->c f(x) + lim_x->c g(x)
    
    # Product rule for limits
    # lim_x->c f(x) * g(x) = lim_x->c f(x) * lim_x->c g(x)

    # Quotient rule for limits
    # lim_x->c f(x) / g(x) = lim_x->c f(x) / lim_x->c g(x)

    # Limit of a power
    # lim_x->c f(x)^g(x) = lim_x->c f(x) ^ lim_x->c g(x)

    # Limit of a function of a function
    # lim_x->c f(g(x)) = f(lim_x->c g(x))
]