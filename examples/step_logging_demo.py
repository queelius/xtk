#!/usr/bin/env python3
"""
Demonstration of step logging for expression rewriting visualization.

This example shows how to use the StepLogger to track and save
transformation steps for later visualization.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtk.rewriter import simplifier
from xtk.step_logger import StepLogger
from xtk.parser import parse_sexpr

# Define some mathematical rules for demonstration
demo_rules = [
    # Commutative property of addition
    [['+', ['?', 'a'], ['?c', 'b']], ['+', [':', 'b'], [':', 'a']]],
    [['+', ['?c', 'a'], ['?', 'b']], ['+', [':', 'b'], [':', 'a']]],
    
    # Commutative property of multiplication  
    [['*', ['?', 'a'], ['?c', 'b']], ['*', [':', 'b'], [':', 'a']]],
    [['*', ['?c', 'a'], ['?', 'b']], ['*', [':', 'b'], [':', 'a']]],
    
    # Identity elements
    [['+', 0, ['?', 'x']], [':', 'x']],
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', 1, ['?', 'x']], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
    
    # Zero multiplication
    [['*', 0, ['?', 'x']], 0],
    [['*', ['?', 'x'], 0], 0],
    
    # Distribution
    [['*', ['?', 'a'], ['+', ['?', 'b'], ['?', 'c']]], 
     ['+', ['*', [':', 'a'], [':', 'b']], ['*', [':', 'a'], [':', 'c']]]],
]


def example1_basic_arithmetic():
    """Basic arithmetic simplification with logging."""
    print("\n=== Example 1: Basic Arithmetic ===")
    
    # Create a step logger
    logger = StepLogger('examples/output/arithmetic_steps.json')
    
    # Create simplifier with logging
    simplify = simplifier(demo_rules, step_logger=logger)
    
    # Expression: (x + 0) * 1
    expr = parse_sexpr("(* (+ x 0) 1)")
    print(f"Input: {expr}")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"Result: {result}")
    
    # Save the steps
    logger.save()
    print(f"Steps saved to: {logger.output_path}")
    
    return logger


def example2_distribution():
    """Demonstrate distribution rule with logging."""
    print("\n=== Example 2: Distribution ===")
    
    # Create a step logger
    logger = StepLogger('examples/output/distribution_steps.json')
    
    # Create simplifier with logging
    simplify = simplifier(demo_rules, step_logger=logger)
    
    # Expression: 3 * (x + y)
    expr = parse_sexpr("(* 3 (+ x y))")
    print(f"Input: {expr}")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"Result: {result}")
    
    # Save the steps
    logger.save()
    print(f"Steps saved to: {logger.output_path}")
    
    return logger


def example3_complex_expression():
    """Complex expression with multiple rewrites."""
    print("\n=== Example 3: Complex Expression ===")
    
    # Create a step logger
    logger = StepLogger('examples/output/complex_steps.json')
    
    # Create simplifier with logging
    simplify = simplifier(demo_rules, step_logger=logger)
    
    # Expression: (0 + x) * (1 * y)
    expr = parse_sexpr("(* (+ 0 x) (* 1 y))")
    print(f"Input: {expr}")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"Result: {result}")
    
    # Save the steps
    logger.save()
    print(f"Steps saved to: {logger.output_path}")
    
    # Print step summary
    print(f"\nStep Summary:")
    for step in logger.get_steps():
        if step['type'] == 'initial':
            print(f"  Step {step['step']}: Initial expression")
        elif step['type'] == 'rewrite':
            print(f"  Step {step['step']}: Applied rule - pattern: {step['rule']['pattern']}")
        elif step['type'] == 'final':
            print(f"  Step {step['step']}: Final result (after {step['metadata'].get('iterations', '?')} iterations)")
    
    return logger


def example4_derivative_with_logging():
    """Demonstrate derivative calculation with step logging."""
    print("\n=== Example 4: Derivative with Logging ===")
    
    from xtk.rules.deriv_rules_fixed import deriv_rules
    
    # Create a step logger
    logger = StepLogger('examples/output/derivative_steps.json')
    
    # Create simplifier with derivative rules and logging
    simplify = simplifier(deriv_rules, step_logger=logger)
    
    # Expression: d/dx(x^2 + 3*x)
    expr = parse_sexpr("(deriv (+ (* x x) (* 3 x)) x)")
    print(f"Input: {expr}")
    
    # Calculate derivative with logging
    result = simplify(expr)
    print(f"Result: {result}")
    
    # Save the steps
    logger.save()
    print(f"Steps saved to: {logger.output_path}")
    
    return logger


def main():
    """Run all examples."""
    print("XTK Step Logging Demonstration")
    print("=" * 40)
    
    # Create output directory
    output_dir = Path('examples/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run examples
    example1_basic_arithmetic()
    example2_distribution()
    example3_complex_expression()
    example4_derivative_with_logging()
    
    print("\n" + "=" * 40)
    print("All examples completed!")
    print("\nTo visualize the results:")
    print("1. Open integrations/xtk-tree-viewer/viewer.html in a browser")
    print("2. Load one of the generated JSON files from examples/output/")
    print("3. Click through the steps to see the transformation process")


if __name__ == "__main__":
    main()