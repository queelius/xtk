#!/usr/bin/env python3
"""
Test to verify full tree display in progressive viewer.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtk.rewriter import simplifier
from xtk.step_logger import StepLogger

# Simple rules that will show partial rewrites
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
    """Create a test case showing full tree at each step."""
    print("Creating Full Tree Test Data")
    print("=" * 40)
    
    # Create output directory
    output_dir = Path('examples/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a step logger
    logger = StepLogger('examples/output/full_tree_test.json')
    
    # Create simplifier with logging
    simplify = simplifier(simple_rules, step_logger=logger)
    
    # Expression with nested structure: (x + 0) + (y * 1)
    # This should show the FULL tree at each step, not just the part being rewritten
    expr = ['+', ['+', 'x', 0], ['*', 'y', 1]]
    print(f"Input expression: {expr}")
    print(f"Readable form: (x + 0) + (y * 1)")
    print("\nExpected transformation sequence:")
    print("  Step 0: (x + 0) + (y * 1)  [initial - full tree visible]")
    print("  Step 1: x + (y * 1)         [left subtree simplified, right still visible]")
    print("  Step 2: x + y               [right subtree simplified]")
    print("  Final:  x + y               [final result]")
    
    # Simplify with logging
    result = simplify(expr)
    print(f"\nActual result: {result}")
    
    # Save the steps
    logger.save()
    print(f"\nSteps saved to: {logger.output_path}")
    
    print("\nTo verify full tree display:")
    print("1. Open integrations/xtk-tree-viewer/progressive-viewer.html")
    print("2. Load examples/output/full_tree_test.json")
    print("3. Step through and verify you see the COMPLETE tree at each step")
    print("   - Not just 'x' when x+0 becomes x")
    print("   - But the full 'x + (y * 1)' with the changed part highlighted")


if __name__ == "__main__":
    main()