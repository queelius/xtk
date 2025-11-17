"""
Core rewriter module for symbolic expression transformation.

This module provides pattern matching, instantiation, and evaluation
capabilities for rule-based expression rewriting.
"""

import logging
from typing import Any, Dict, List, Union, Optional, Callable
from copy import deepcopy
from .step_logger import StepLogger

logger = logging.getLogger(__name__)

ExprType = Union[int, float, str, List]
DictType = Union[List[List], str]
RuleType = List[List]


class MatchFailure(Exception):
    """Exception raised when pattern matching fails."""
    pass


def car(lst: List) -> Any:
    """
    Return the first element of a list (head).
    
    Args:
        lst: A non-empty list
        
    Returns:
        The first element of the list
        
    Raises:
        TypeError: If argument is not a list
        ValueError: If list is empty
    """
    if not isinstance(lst, list):
        raise TypeError("car: argument must be a list")
    elif not lst:
        raise ValueError("car: argument is an empty list")
    return lst[0]


def cdr(lst: List) -> List:
    """
    Return all but the first element of a list (tail).
    
    Args:
        lst: A list
        
    Returns:
        A list containing all elements except the first
    """
    if not isinstance(lst, list):
        raise TypeError("cdr: argument must be a list")
    elif not lst:
        return []
    return lst[1:]


def cons(item: Any, lst: List) -> List:
    """
    Construct a new list by prepending an item.
    
    Args:
        item: The item to prepend
        lst: The list to prepend to
        
    Returns:
        A new list with item as the first element
    """
    return [item] + lst


def atom(exp: ExprType) -> bool:
    """
    Check if an expression is atomic (not compound).
    
    Args:
        exp: The expression to check
        
    Returns:
        True if exp is a constant or variable, False otherwise
    """
    return constant(exp) or variable(exp)


def compound(exp: ExprType) -> bool:
    """
    Check if an expression is compound (a list).
    
    Args:
        exp: The expression to check
        
    Returns:
        True if exp is a list, False otherwise
    """
    return isinstance(exp, list)


def constant(exp: ExprType) -> bool:
    """
    Check if an expression is a numeric constant.
    
    Args:
        exp: The expression to check
        
    Returns:
        True if exp is an int or float, False otherwise
    """
    return isinstance(exp, (int, float))


def variable(exp: ExprType) -> bool:
    """
    Check if an expression is a variable (string).
    
    Args:
        exp: The expression to check
        
    Returns:
        True if exp is a string, False otherwise
    """
    return isinstance(exp, str)


def null(s: Any) -> bool:
    """
    Check if an expression is null (empty list).
    
    Args:
        s: The expression to check
        
    Returns:
        True if s is an empty list, False otherwise
    """
    return s == []


def empty_dictionary() -> List:
    """Create an empty bindings dictionary."""
    return []


def arbitrary_constant(pat: ExprType) -> bool:
    """Check if pattern matches any constant."""
    return compound(pat) and car(pat) == "?c"


def arbitrary_variable(pat: ExprType) -> bool:
    """Check if pattern matches any variable."""
    return compound(pat) and car(pat) == "?v"


def arbitrary_expression(pat: ExprType) -> bool:
    """Check if pattern matches any expression."""
    return compound(pat) and car(pat) == "?"


def skeleton_evaluation(s: ExprType) -> bool:
    """Check if skeleton element should be evaluated."""
    return compound(s) and car(s) == ":"


def eval_exp(s: List) -> Any:
    """Extract the expression to evaluate from a skeleton element."""
    return car(cdr(s))


def pattern(rule: RuleType) -> ExprType:
    """Extract the pattern from a rule."""
    return car(rule)


def skeleton(rule: RuleType) -> ExprType:
    """Extract the skeleton from a rule."""
    return car(cdr(rule))


def variable_name(pat: List) -> str:
    """Extract the variable name from a pattern element."""
    return car(cdr(pat))


def extend_dictionary(pat: List, dat: ExprType, dict_: DictType) -> DictType:
    """
    Extend a bindings dictionary with a new binding.
    
    Args:
        pat: The pattern containing the variable name
        dat: The data to bind
        dict_: The current bindings dictionary
        
    Returns:
        Extended dictionary or "failed" on conflict
    """
    if dict_ == "failed":
        return "failed"
    
    name = variable_name(pat)
    for entry in dict_:
        if entry[0] == name:
            if entry[1] == dat:
                return dict_
            else:
                logger.debug(f"Conflict in dictionary: {entry[0]} -> {entry[1]} vs {dat}")
                return "failed"
    
    logger.debug(f"Extending dictionary: {name} -> {dat}")
    return dict_ + [[name, dat]]


def lookup(var: str, dict_: DictType) -> Any:
    """
    Look up a variable in the bindings dictionary.
    
    Args:
        var: The variable name
        dict_: The bindings dictionary
        
    Returns:
        The bound value or var if not found
    """
    for entry in dict_:
        if entry[0] == var:
            return entry[1]
    return var


def match(pat: ExprType, exp: ExprType, dict_: DictType) -> DictType:
    """
    Match a pattern against an expression with bindings.
    
    Args:
        pat: The pattern to match
        exp: The expression to match against
        dict_: Current bindings dictionary
        
    Returns:
        Updated dictionary on success, "failed" on failure
    """
    logger.debug(f"match({pat}, {exp}, {dict_})")
    
    if dict_ == "failed":
        return "failed"
    
    elif null(pat):
        return dict_ if null(exp) else "failed"
        
    elif atom(pat):
        return dict_ if atom(exp) and pat == exp else "failed"
        
    elif arbitrary_constant(pat):
        return extend_dictionary(pat, exp, dict_) if constant(exp) else "failed"
        
    elif arbitrary_variable(pat):
        return extend_dictionary(pat, exp, dict_) if variable(exp) else "failed"
        
    elif arbitrary_expression(pat):
        return extend_dictionary(pat, exp, dict_) if not callable(exp) else "failed"

    elif atom(exp) or callable(exp):
        return "failed"

    else:  # Both are compound
        # Check if either list is empty before calling car/cdr
        if null(pat) or null(exp):
            return "failed"
        submatch = match(car(pat), car(exp), dict_)
        return match(cdr(pat), cdr(exp), submatch)


def instantiate(skeleton: ExprType, dict_: DictType) -> ExprType:
    """
    Instantiate a skeleton with bindings.
    
    Args:
        skeleton: The skeleton to instantiate
        dict_: The bindings dictionary
        
    Returns:
        The instantiated expression
    """
    logger.debug(f"instantiate({skeleton}, {dict_})")
    
    def loop(s):
        if null(s):
            return []
        elif atom(s):
            return s
        elif skeleton_evaluation(s):
            eval_s = eval_exp(s)
            eval_result = evaluate(eval_s, dict_)
            return eval_result
        else:  # Compound
            return cons(loop(car(s)), loop(cdr(s)))
    
    return loop(skeleton)


def evaluate(form: ExprType, dict_: DictType) -> ExprType:
    """
    Evaluate an expression with bindings.
    
    Args:
        form: The expression to evaluate
        dict_: The bindings dictionary
        
    Returns:
        The evaluated expression
    """
    logger.debug(f"evaluate({form}, {dict_})")
    
    if null(form):
        return []
    
    elif compound(form):
        op = car(form)
        args = cdr(form)
        simplified_args = [evaluate(arg, dict_) for arg in args]
        simplified_form = cons(op, simplified_args)
        obj = lookup(op, dict_)
        
        if callable(obj):
            try:
                result = obj(*simplified_args)
                return result
            except Exception as e:
                logger.debug(f"Error evaluating {op}: {e}")
                return simplified_form
        
        return simplified_form
    
    elif constant(form):
        return form
    
    elif atom(form):
        return lookup(form, dict_)
    
    return form


def rewriter(the_rules: List[RuleType], step_logger: Optional[StepLogger] = None, constant_folding: bool = True) -> Callable:
    """
    Create a rewriter function using given rules.

    Args:
        the_rules: List of transformation rules
        step_logger: Optional step logger for tracking transformations
        constant_folding: Enable automatic constant folding (default: True)

    Returns:
        A function that rewrites expressions
    """
    def simplify_exp(exp, is_root=False):
        """Simplify an expression using the rules."""
        logger.debug(f"simplify_exp({exp})")
        
        if is_root and step_logger:
            step_logger.log_initial(exp)
        
        max_iterations = 1000  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            old_exp = deepcopy(exp)

            # Try applying rules
            result = try_rules(exp)
            if result != exp:
                exp = result
                continue

            # Try constant folding (arithmetic evaluation) if enabled
            if constant_folding:
                result = try_constant_fold(exp)
                if result != exp:
                    exp = result
                    continue

            # If compound, simplify parts
            if compound(exp):
                result = simplify_parts(exp)
                if result != exp:
                    exp = result
                    continue

            # No changes, we're done
            if exp == old_exp:
                break
        
        if is_root and step_logger:
            step_logger.log_final(exp, {'iterations': iterations})
        
        return exp
    
    def simplify_parts(exp):
        """Recursively simplify parts of a compound expression."""
        if null(exp):
            return []
        else:
            return cons(simplify_exp(car(exp)), simplify_parts(cdr(exp)))
    
    def try_constant_fold(exp):
        """Try to evaluate arithmetic on constant operands."""
        if not compound(exp) or null(exp):
            return exp

        op = car(exp)
        args = cdr(exp)

        # Check if all arguments are numeric constants
        if not all(isinstance(arg, (int, float)) for arg in args):
            return exp

        # Evaluate arithmetic operations
        try:
            if op == '+' and len(args) == 2:
                result = args[0] + args[1]
            elif op == '-' and len(args) == 2:
                result = args[0] - args[1]
            elif op == '-' and len(args) == 1:
                result = -args[0]
            elif op == '*' and len(args) == 2:
                result = args[0] * args[1]
            elif op == '/' and len(args) == 2:
                result = args[0] / args[1] if args[1] != 0 else exp
            elif op == '^' and len(args) == 2:
                result = args[0] ** args[1]
            else:
                return exp

            # Log constant folding if logger is available
            if step_logger:
                step_logger.log_rewrite(
                    before=exp,
                    after=result,
                    rule_pattern=f"constant-fold-{op}",
                    rule_skeleton=result,
                    bindings=[]
                )

            return result
        except:
            return exp

    def try_rules(exp):
        """Try applying rules to an expression."""
        def scan(rules):
            if null(rules):
                return exp
            else:
                rule = car(rules)
                pat = pattern(rule)
                skel = skeleton(rule)

                dict_ = match(pat, exp, empty_dictionary())
                if dict_ == "failed":
                    return scan(cdr(rules))
                else:
                    skel_inst = instantiate(skel, dict_)

                    # Log the rewrite if logger is available
                    if step_logger:
                        step_logger.log_rewrite(
                            before=exp,
                            after=skel_inst,
                            rule_pattern=pat,
                            rule_skeleton=skel,
                            bindings=dict_
                        )

                    return simplify_exp(skel_inst)

        return scan(the_rules)
    
    # Return a wrapper that sets is_root=True for the initial call
    def wrapper(exp):
        return simplify_exp(exp, is_root=True)

    return wrapper


# Backwards compatibility alias
simplifier = rewriter