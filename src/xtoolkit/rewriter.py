import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def car(lst):
    if not isinstance(lst, list):
        raise TypeError("car: argument must be a list")
    elif not lst:
        raise ValueError("car: argument is an empty list")
    else:
        return lst[0]

def cdr(lst):
    if not isinstance(lst, list):
        raise TypeError("cdr: argument must be a list")
    elif not lst: # If lst is empty, return an empty list
        return []
    else:
        return lst[1:]

def match(pat, exp, dict):
    logger.debug(f"Called: match({pat}, {exp}, {dict})")

    if dict == "failed":
        logger.debug("match::Dictionary already failed. Returning 'failed'.")
        return "failed"
    
    elif null(pat):
        logger.debug("match::Pattern is empty.")

        if null(exp):
            logger.debug("match::Both pattern and expression are empty. Match successful.")
            return dict
        else:
            logger.debug("match::Pattern is empty but expression is not. Match failed.")
            return "failed"
        
    elif atom(pat):
        logger.debug(f"match::Pattern is atomic: {pat}, expression is {exp}")
        
        if atom(exp) and pat == exp:
            logger.debug("match::Atoms match. Returning dictionary.")
            return dict
        else:
            logger.debug("match::Atoms do not match. Match failed.")
            return "failed"
        
    elif arbitrary_constant(pat):
        logger.debug(f"match::Arbitrary constant match. Pattern: {pat}, expression: {exp}")

        if constant(exp):
            logger.debug(
                f"match::Arbitrary constant match. Extending dictionary with {pat} -> {exp}."
            )
            return extend_dictionary(pat, exp, dict)
        else:
            logger.debug("match::Arbitrary constant failed to match.")
            return "failed"
        
    elif arbitrary_variable(pat):
        logger.debug(f"match::Arbitrary variable match. Pattern: {pat}, expression: {exp}")

        if variable(exp):
            logger.debug(
                f"match::Arbitrary variable match. Extending dictionary with {pat} -> {exp}."
            )
            return extend_dictionary(pat, exp, dict)
        else:
            logger.debug("match::Arbitrary variable failed to match.")
            return "failed"
        
    elif arbitrary_expression(pat):
        logger.debug(f"match::Arbitrary expression match. Pattern: {pat}, expression: {exp}")

        logger.debug(
            f"match::Arbitrary expression match. Extending dictionary with {pat} -> {exp}."
        )
        return extend_dictionary(pat, exp, dict)
    elif atom(exp):
        logger.debug("match::Expression is atomic but pattern is not. Match failed.")
        return "failed"
    elif callable(exp):
        logger.debug("match::Expression is callable. Returning failed.")
        return "failed"
    else:
        logger.debug("match::Recursively matching car and cdr.")
        submatch = match(car(pat), car(exp), dict)
        logger.debug(f"match::Submatch result: {submatch}")
        return match(cdr(pat), cdr(exp), submatch)


def instantiate(skeleton, dict):
    logger.debug(f"Called: instantiate({skeleton}, {dict})")

    def loop(s):
        logger.debug(f"instantiate::Called: instantiate::loop({s})")
        if null(s):  # Empty list case
            logger.debug("instantiate::loop::Encountered an empty list in instantiate.")
            return []
        elif atom(s):  # Atom case
            logger.debug(f"instantiate::loop::Atom encountered in instantiate: {s}")
            return s
        elif skeleton_evaluation(s):  # Skeleton evaluation
            logger.debug(f"instantiate::loop::Evaluating skeleton: {s}")
            eval_s = eval_exp(s)
            logger.debug(f"instantiate::loop::Evaluated skeleton: {eval_s}")
            eval_result = evaluate(eval_s, dict)
            logger.debug(f"instantiate::loop::Evaluated result: {eval_result}")
            return eval_result
        
        else:  # Compound list case
            logger.debug(f"instantiate::loop::Recursively instantiating compound structure: {s}")
            car_s = car(s)
            cdr_s = cdr(s)
            logger.debug(f"instantiate::loop::Car: {car_s}, Cdr: {cdr_s}")
            return cons(loop(car_s), loop(cdr_s))

    result = loop(skeleton)
    logger.debug(f"instantiate::Instantiation result: {result}")
    return result


def evaluate(form, dict):
    logger.debug(f"Called: evaluate({form}, {dict})")
    if null(form):
       logger.debug("Empty form encountered. Returning as is.")
       return []
    
    elif compound(form):
        logger.debug(f"evaluate::Compound form {form} encountered.")
        op = car(form)
        args = cdr(form)
        logger.debug(f"evaluate::Operator: {op}, Arguments: {args}")
        simplified_args = [evaluate(arg, dict) for arg in args]
        logger.debug(f"evaluate::Simplified arguments: {simplified_args}")
        simplified_form = cons(op, simplified_args)
        logger.debug(f"evaluate::Simplified form: {simplified_form}")
        obj = lookup(op, dict)
        logger.debug(f"evaluate::looked up object {obj} for operator {op}")

        if callable(obj):
            result = obj(*simplified_args)
            logger.debug(f"evaluate::Callable operator. Result: {result} for operator {op} on smip args {simplified_args}")
            return result
        
        logger.debug(f"evaluate::Operator is not callable. Returning simplified form {simplified_form}")
        return simplified_form

    elif constant(form):
        logger.debug(f"evaluate::Evaluated constant {form} to {form}")
        return form

    elif atom(form):
        value = lookup(form, dict)
        logger.debug(f"evaluate::Evaluated atom {form} to {value}")
        return value
    
    
    logger.debug(f"evaluate::Unrecognized form {form}. Returning as is.")
    return form



def simplifier(the_rules: list) -> callable:
    """
    Returns a simplifier function that simplifies expressions using the given rules.

    Args:
        the_rules (list): A list of rules to apply to the expression.

    Returns:
        callable: A function that simplifies expressions using the given rules.
    """

    logger.debug(f"simplifier::creating simplifier with rules={the_rules}")

    def simplify_exp(exp):
        logger.debug(f"Called: simplify_exp({exp})")
        while True:

            if compound(exp):
                # If no rules matched, simplify recursively
                result = simplify_parts(exp)
                if result != exp:
                    logger.debug(f"simplify_exp::Simplified compound expression={exp} to {result}")
                    exp = result

            result = try_rules(exp)
            if result != exp:
                logger.debug(f"simplify_exp::Rule applied. Simplified expression={exp} to {result}")
                exp = result
                continue

            break  # No more changes

        return exp

    def simplify_parts(exp):
        logger.debug(f"Called: simplify_parts({exp})")
        if null(exp):
            logger.debug("simplify_parts::Simplify parts: empty expression encountered")
            return empty_dictionary()
        else:
            logger.debug(f"simplify_parts::Simplifying parts of expression={exp}")
            result = cons(simplify_exp(car(exp)), simplify_parts(cdr(exp)))
            logger.debug(f"simplify_parts::Simplified parts of {exp} to {result}")
            return result

    def try_rules(exp):
        logger.debug(f"Called: try_rules({exp})")

        def scan(rules):
            logger.debug(f"Called: try_rules::scan({rules})")
            if null(rules):
                logger.debug(f"try_rules::scan::no rules matched for expression={exp}")
                return exp
            else:
                rule = car(rules)
                logger.debug(f"try_rules::scan::Testing rule={rule} on expression={exp}")

                pat = pattern(rule)
                skel = skeleton(rule)

                dict = match(pat, exp, empty_dictionary())
                logger.debug(
                    f"try_rules::scan::Match result: {dict} on pattern rule {pat} and expression {exp}"
                )
                if dict == "failed":
                    logger.debug(f"try_rules::scan::Rule {rule} failed to match. Trying next rule.")
                    return scan(cdr(rules))
                else:
                    logger.debug(
                        f"try_rules::scan::Rule {rule} matched with dictionary {dict}. Instantiating skeleton"
                    )
                    skel_inst = instantiate(skel, dict)
                    logger.debug(
                        f"try_rules::scan::Instantiated skeleton: {skel_inst} with dictionary {dict} and skeleton {skel}"
                    )
                    result = simplify_exp(skel_inst)
                    logger.debug(f"try_rules::scan::Instantiated rule: {result}")
                    return result

        return scan(the_rules)

    return simplify_exp


# Helper functions
def atom(exp):
    """
    Returns True if the expression is an atom, False otherwise.

    An atom is a constant or a variable (i.e. not a compound expression).

    Args:
        exp: The expression to check.

    Returns:
        bool: True if the expression is an atom, False otherwise
    """
    #return not isinstance(exp, list)
    return constant(exp) or variable(exp)


def compound(exp):
    """
    Returns True if the expression is a compound expression, False otherwise.

    A compound expression is a list.

    Args:
        exp: The expression to check.

    Returns:
        bool: True if the expression is a compound expression, False otherwise
    """
    return isinstance(exp, list)


def constant(exp):
    return isinstance(exp, (int, float))


def variable(exp):
    return isinstance(exp, str)


def empty_dictionary():
    return []


def extend_dictionary(pat, dat, dict):
    logger.debug(f"Called: extend_dictionary({pat}, {dat}, {dict})")
    name = variable_name(pat)
    for entry in dict:
        if entry[0] == name:
            if entry[1] == dat:
                return dict
            else:
                logger.debug(
                    f"Conflict in dictionary: {entry[0]} -> {entry[1]} vs {dat}"
                )
                return "failed"
    logger.debug(f"Extending dictionary: {name} -> {dat}")
    return dict + [[name, dat]]


def lookup(var, dict):
    logger.debug(f"Called: lookup({var}, {dict})")
    for entry in dict:
        if entry[0] == var:
            return entry[1]
    logger.debug(f"Variable {var} not found in dictionary. Returning as is.")
    return var


def arbitrary_constant(pat):
    return compound(pat) and car(pat) == "?c"


def arbitrary_variable(pat):
    return compound(pat) and car(pat) == "?v"


def arbitrary_expression(pat):
    return compound(pat) and car(pat) == "?"


def skeleton_evaluation(s):
    return compound(s) and car(s) == ":"


def eval_exp(s):
    return car(cdr(s))


def pattern(rule):
    return car(rule)


def skeleton(rule):
    return car(cdr(rule))


def variable_name(pat):
    return car(cdr(pat))


def null(s):
    return s == []


def cons(item, lst):
    return [item] + lst
