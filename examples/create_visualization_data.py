#!/usr/bin/env python3
"""
Create interesting visualization data with multiple rewrite steps.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtk.rewriter import simplifier
from xtk.step_logger import StepLogger

# More interesting rules with multiple steps
math_rules = [
    # Identity elements
    [['+', 0, ['?', 'x']], [':', 'x']],
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', 1, ['?', 'x']], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
    
    # Zero multiplication
    [['*', 0, ['?', 'x']], 0],
    [['*', ['?', 'x'], 0], 0],
    
    # Double negation
    [['-', ['-', ['?', 'x']]], [':', 'x']],
    
    # Simplify subtraction
    [['-', ['?', 'x'], 0], [':', 'x']],
    [['-', ['?', 'x'], ['?', 'x']], 0],
]


def create_multi_step_example():
    """Create an example with multiple rewrite steps."""
    print("Creating Multi-Step Visualization Data")
    print("=" * 40)
    
    # Create output directory
    output_dir = Path('examples/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a step logger
    logger = StepLogger('examples/output/multi_step_demo.json')
    
    # Create simplifier with logging
    simplify = simplifier(math_rules, step_logger=logger)
    
    # Expression with multiple simplifications: (x * 1) + (y * 0) + 0
    expr = ['+', ['+', ['*', 'x', 1], ['*', 'y', 0]], 0]
    print(f"Input expression: {expr}")
    print(f"Readable form: ((x * 1) + (y * 0)) + 0")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"\nResult: {result}")
    
    # Save the steps
    logger.save()
    print(f"\nSteps saved to: {logger.output_path}")
    
    # Show what transformations happened
    print(f"\nTransformation sequence ({len(logger.get_steps())} steps):")
    for step in logger.get_steps():
        if step['type'] == 'initial':
            print(f"  Initial: ((x * 1) + (y * 0)) + 0")
        elif step['type'] == 'rewrite':
            print(f"  Rewrite: Applied rule to simplify expression")
        elif step['type'] == 'final':
            print(f"  Final:   {step['expression']}")
    
    return logger


def create_nested_example():
    """Create an example with nested expressions."""
    print("\n\nCreating Nested Expression Visualization")
    print("=" * 40)
    
    # Create a step logger
    logger = StepLogger('examples/output/nested_demo.json')
    
    # Create simplifier with logging
    simplify = simplifier(math_rules, step_logger=logger)
    
    # Nested expression: (((x + 0) * 1) - ((y * 0) + 0))
    expr = ['-', ['*', ['+', 'x', 0], 1], ['+', ['*', 'y', 0], 0]]
    print(f"Input expression: {expr}")
    print(f"Readable form: ((x + 0) * 1) - ((y * 0) + 0)")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"\nResult: {result}")
    
    # Save the steps
    logger.save()
    print(f"\nSteps saved to: {logger.output_path}")
    
    return logger


def create_double_negation_example():
    """Create an example with double negation."""
    print("\n\nCreating Double Negation Example")
    print("=" * 40)
    
    # Create a step logger
    logger = StepLogger('examples/output/negation_demo.json')
    
    # Create simplifier with logging
    simplify = simplifier(math_rules, step_logger=logger)
    
    # Expression: -(-((x * 1) + 0))
    expr = ['-', ['-', ['+', ['*', 'x', 1], 0]]]
    print(f"Input expression: {expr}")
    print(f"Readable form: -(-((x * 1) + 0))")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"\nResult: {result}")
    
    # Save the steps
    logger.save()
    print(f"\nSteps saved to: {logger.output_path}")
    
    return logger


def main():
    """Run all examples."""
    create_multi_step_example()
    create_nested_example()
    create_double_negation_example()
    
    print("\n" + "=" * 40)
    print("Visualization data created successfully!")
    print("\nTo visualize the results:")
    print("1. Open integrations/xtk-tree-viewer/viewer.html in your browser")
    print("2. Click 'Choose File' and select one of these files:")
    print("   - examples/output/multi_step_demo.json")
    print("   - examples/output/nested_demo.json")
    print("   - examples/output/negation_demo.json")
    print("3. Click through the steps in the sidebar to see the transformations")


if __name__ == "__main__":
    main()