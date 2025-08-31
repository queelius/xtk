#!/usr/bin/env python3
"""
Comprehensive test runner with coverage analysis for xtk.

Usage:
    python test_all.py              # Run all tests
    python test_all.py --coverage   # Run with coverage report
    python test_all.py --verbose    # Verbose output
    python test_all.py --failfast   # Stop on first failure
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))


def run_tests(coverage_enabled=False, verbose=False, failfast=False, pattern=None):
    """
    Run all tests with optional coverage.
    
    Args:
        coverage_enabled: Enable coverage reporting
        verbose: Verbose test output
        failfast: Stop on first failure
        pattern: Pattern to match test files (e.g., 'test_parser*')
    """
    
    if coverage_enabled:
        try:
            import coverage
        except ImportError:
            print("Coverage.py not installed. Install with: pip install coverage")
            print("Running tests without coverage...")
            coverage_enabled = False
    
    # Start coverage if enabled
    if coverage_enabled:
        cov = coverage.Coverage(source=['src/xtk'])
        cov.start()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    test_pattern = pattern or 'test*.py'
    suite = loader.discover('tests', pattern=test_pattern)
    
    # Configure runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast
    )
    
    # Run tests
    print(f"Running tests matching pattern: {test_pattern}")
    print("=" * 70)
    result = runner.run(suite)
    
    # Generate coverage report if enabled
    if coverage_enabled:
        cov.stop()
        print("\n" + "=" * 70)
        print("Coverage Report:")
        print("=" * 70)
        cov.report()
        
        # Generate HTML report
        html_dir = Path(__file__).parent / 'htmlcov'
        cov.html_report(directory=str(html_dir))
        print(f"\nDetailed HTML coverage report generated in: {html_dir}")
        print(f"Open {html_dir}/index.html in a browser to view.")
    
    # Return success/failure
    return result.wasSuccessful()


def run_specific_test(test_name):
    """
    Run a specific test or test class.
    
    Args:
        test_name: Test to run (e.g., 'test_parser.TestParseSexpr')
    """
    loader = unittest.TestLoader()
    
    try:
        # Try to load the specific test
        suite = loader.loadTestsFromName(test_name, module=None)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error loading test '{test_name}': {e}")
        return False


def list_tests():
    """List all available test modules and classes."""
    print("Available test modules:")
    print("=" * 40)
    
    test_dir = Path(__file__).parent / 'tests'
    test_files = sorted(test_dir.glob('test*.py'))
    
    for test_file in test_files:
        module_name = test_file.stem
        print(f"\n{module_name}:")
        
        # Try to load and list test classes
        try:
            loader = unittest.TestLoader()
            module = loader.loadTestsFromName(f'tests.{module_name}')
            
            # Extract test class names
            for test_group in module:
                if hasattr(test_group, '__iter__'):
                    for test in test_group:
                        if hasattr(test, '__class__'):
                            class_name = test.__class__.__name__
                            if class_name != 'ModuleImportFailure':
                                print(f"  - {class_name}")
                                
        except Exception:
            print(f"  (Unable to load)")


def run_performance_tests():
    """Run performance/benchmark tests."""
    print("Running performance tests...")
    print("=" * 70)
    
    import time
    from xtk import Expression, simplifier, parse_sexpr
    from xtk.rules.algebra_rules import simplify_rules
    
    # Test 1: Deep nesting
    print("\n1. Deep nesting performance:")
    expr = "x"
    for i in range(100):
        expr = ["+", expr, i]
    
    start = time.time()
    e = Expression(expr)
    result = e.to_string()
    elapsed = time.time() - start
    print(f"   100-level nested expression: {elapsed:.4f}s")
    
    # Test 2: Many terms
    print("\n2. Many terms performance:")
    terms = list(range(500))
    expr = Expression(["+"] + terms)
    
    start = time.time()
    result = expr.to_string()
    elapsed = time.time() - start
    print(f"   500-term expression: {elapsed:.4f}s")
    
    # Test 3: Rule application
    print("\n3. Rule application performance:")
    expr = Expression(["+", ["*", "x", 1], ["*", 0, "y"], ["+", "z", 0]])
    
    start = time.time()
    result = expr.with_rules(simplify_rules).simplify()
    elapsed = time.time() - start
    print(f"   Simplification with {len(simplify_rules)} rules: {elapsed:.4f}s")
    
    # Test 4: Parsing
    print("\n4. Parsing performance:")
    complex_sexpr = "(" * 50 + "x" + ")" * 50
    
    start = time.time()
    parsed = parse_sexpr(complex_sexpr)
    elapsed = time.time() - start
    print(f"   50-level nested S-expression parsing: {elapsed:.4f}s")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run xtk tests')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Enable coverage reporting')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose test output')
    parser.add_argument('--failfast', '-f', action='store_true',
                       help='Stop on first failure')
    parser.add_argument('--pattern', '-p', type=str,
                       help='Pattern for test discovery (e.g., "test_parser*")')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available tests')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests')
    parser.add_argument('--test', '-t', type=str,
                       help='Run specific test (e.g., "test_parser.TestParseSexpr")')
    
    args = parser.parse_args()
    
    # List tests if requested
    if args.list:
        list_tests()
        return 0
    
    # Run performance tests if requested
    if args.performance:
        run_performance_tests()
        return 0
    
    # Run specific test if requested
    if args.test:
        success = run_specific_test(f'tests.{args.test}')
        return 0 if success else 1
    
    # Run all tests
    success = run_tests(
        coverage_enabled=args.coverage,
        verbose=args.verbose,
        failfast=args.failfast,
        pattern=args.pattern
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())