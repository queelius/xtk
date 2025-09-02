#!/usr/bin/env python3
"""
Simple demonstration of step logging for expression rewriting visualization.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtk.rewriter import simplifier
from xtk.step_logger import StepLogger
from xtk.parser import parse_sexpr

# Simple non-recursive rules
simple_rules = [
    # Identity elements
    [['+', 0, ['?', 'x']], [':', 'x']],
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', 1, ['?', 'x']], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
    
    # Zero multiplication
    [['*', 0, ['?', 'x']], 0],
    [['*', ['?', 'x'], 0], 0],
]


def main():
    """Run simple example with step logging."""
    print("Simple Step Logging Example")
    print("=" * 40)
    
    # Create output directory
    output_dir = Path('examples/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a step logger
    logger = StepLogger('examples/output/simple_steps.json')
    
    # Create simplifier with logging
    simplify = simplifier(simple_rules, step_logger=logger)
    
    # Simple expression: 0 + x
    expr = ['+', 0, 'x']
    print(f"Input: {expr}")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"Result: {result}")
    
    # Save the steps
    logger.save()
    print(f"\nSteps saved to: {logger.output_path}")
    
    # Print step details
    print(f"\nRecorded {len(logger.get_steps())} steps:")
    for step in logger.get_steps():
        if step['type'] == 'initial':
            print(f"  Step {step['step']}: Initial expression = {step['expression']}")
        elif step['type'] == 'rewrite':
            print(f"  Step {step['step']}: Rewrite {step['before']} -> {step['after']}")
            if step['bindings']:
                print(f"               Bindings: {step['bindings']}")
        elif step['type'] == 'final':
            print(f"  Step {step['step']}: Final result = {step['expression']}")
    
    print("\nTo visualize:")
    print("1. Open integrations/xtk-tree-viewer/viewer.html in a browser")
    print("2. Load examples/output/simple_steps.json")


if __name__ == "__main__":
    main()