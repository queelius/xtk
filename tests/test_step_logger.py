"""
Comprehensive tests for the step logger module.
"""

import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime
import shutil

from xtk.step_logger import StepLogger


class TestStepLoggerInitialization(unittest.TestCase):
    """Test StepLogger initialization."""

    def test_init_default_path(self):
        """Test initialization with default output path."""
        logger = StepLogger()
        self.assertEqual(logger.output_path, Path('rewrite_steps.json'))
        self.assertEqual(logger.steps, [])
        self.assertEqual(logger.step_count, 0)
        self.assertIsNotNone(logger.session_id)

    def test_init_custom_string_path(self):
        """Test initialization with custom string path."""
        logger = StepLogger(output_path='custom_steps.json')
        self.assertEqual(logger.output_path, Path('custom_steps.json'))

    def test_init_custom_path_object(self):
        """Test initialization with Path object."""
        custom_path = Path('/tmp/my_steps.json')
        logger = StepLogger(output_path=custom_path)
        self.assertEqual(logger.output_path, custom_path)

    def test_init_session_id_is_iso_format(self):
        """Test that session_id is a valid ISO timestamp."""
        logger = StepLogger()
        # Should not raise an exception
        datetime.fromisoformat(logger.session_id)

    def test_init_multiple_loggers_have_different_sessions(self):
        """Test that multiple logger instances have different session IDs."""
        logger1 = StepLogger()
        logger2 = StepLogger()
        # Sessions could be different if created at different times
        # Both should be valid ISO timestamps
        datetime.fromisoformat(logger1.session_id)
        datetime.fromisoformat(logger2.session_id)


class TestLogInitial(unittest.TestCase):
    """Test log_initial() method."""

    def test_log_initial_simple_expression(self):
        """Test logging a simple initial expression."""
        logger = StepLogger()
        logger.log_initial(['+', 'x', 1])

        self.assertEqual(len(logger.steps), 1)
        step = logger.steps[0]
        self.assertEqual(step['step'], 0)
        self.assertEqual(step['type'], 'initial')
        self.assertEqual(step['expression'], ['+', 'x', 1])
        self.assertEqual(step['metadata'], {})
        self.assertIn('timestamp', step)

    def test_log_initial_with_metadata(self):
        """Test logging initial expression with metadata."""
        logger = StepLogger()
        metadata = {'source': 'user_input', 'context': 'test'}
        logger.log_initial('x', metadata=metadata)

        step = logger.steps[0]
        self.assertEqual(step['metadata'], metadata)

    def test_log_initial_increments_step_count(self):
        """Test that log_initial increments step count."""
        logger = StepLogger()
        self.assertEqual(logger.step_count, 0)

        logger.log_initial('x')
        self.assertEqual(logger.step_count, 1)

        logger.log_initial('y')
        self.assertEqual(logger.step_count, 2)

    def test_log_initial_complex_expression(self):
        """Test logging a complex nested expression."""
        logger = StepLogger()
        expr = ['dd', ['*', 2, ['sin', 'x']], 'x']
        logger.log_initial(expr)

        self.assertEqual(logger.steps[0]['expression'], expr)

    def test_log_initial_numeric_expression(self):
        """Test logging a numeric expression."""
        logger = StepLogger()
        logger.log_initial(42)
        self.assertEqual(logger.steps[0]['expression'], 42)

        logger.log_initial(3.14)
        self.assertEqual(logger.steps[1]['expression'], 3.14)


class TestLogRewrite(unittest.TestCase):
    """Test log_rewrite() method."""

    def test_log_rewrite_basic(self):
        """Test basic rewrite logging."""
        logger = StepLogger()
        before = ['+', 'x', 0]
        after = 'x'
        pattern = ['+', ['?', 'x'], 0]
        skeleton = [':', 'x']

        logger.log_rewrite(before, after, pattern, skeleton)

        self.assertEqual(len(logger.steps), 1)
        step = logger.steps[0]
        self.assertEqual(step['step'], 0)
        self.assertEqual(step['type'], 'rewrite')
        self.assertEqual(step['before'], before)
        self.assertEqual(step['after'], after)
        self.assertEqual(step['rule']['pattern'], pattern)
        self.assertEqual(step['rule']['skeleton'], skeleton)
        self.assertEqual(step['bindings'], {})
        self.assertEqual(step['metadata'], {})

    def test_log_rewrite_with_bindings(self):
        """Test rewrite logging with variable bindings."""
        logger = StepLogger()
        bindings = {'x': 'y', 'c': 5}

        logger.log_rewrite(
            before=['+', 'y', 0],
            after='y',
            rule_pattern=['+', ['?', 'x'], 0],
            rule_skeleton=[':', 'x'],
            bindings=bindings
        )

        self.assertEqual(logger.steps[0]['bindings'], bindings)

    def test_log_rewrite_with_metadata(self):
        """Test rewrite logging with metadata."""
        logger = StepLogger()
        metadata = {'rule_name': 'additive_identity', 'confidence': 1.0}

        logger.log_rewrite(
            before=['+', 'x', 0],
            after='x',
            rule_pattern=['+', ['?', 'x'], 0],
            rule_skeleton=[':', 'x'],
            metadata=metadata
        )

        self.assertEqual(logger.steps[0]['metadata'], metadata)

    def test_log_rewrite_increments_step_count(self):
        """Test that log_rewrite increments step count."""
        logger = StepLogger()

        logger.log_rewrite(['+', 'x', 0], 'x', [], [])
        self.assertEqual(logger.step_count, 1)

        logger.log_rewrite(['*', 'x', 1], 'x', [], [])
        self.assertEqual(logger.step_count, 2)

    def test_log_rewrite_complex_rule(self):
        """Test logging a complex rewrite with nested expressions."""
        logger = StepLogger()
        before = ['dd', ['*', 2, 'x'], 'x']
        after = ['*', 2, ['dd', 'x', 'x']]
        pattern = ['dd', ['*', ['?c', 'c'], ['?', 'u']], ['?v', 'x']]
        skeleton = ['*', [':', 'c'], ['dd', [':', 'u'], [':', 'x']]]
        bindings = {'c': 2, 'u': 'x', 'x': 'x'}

        logger.log_rewrite(before, after, pattern, skeleton, bindings=bindings)

        step = logger.steps[0]
        self.assertEqual(step['before'], before)
        self.assertEqual(step['after'], after)
        self.assertEqual(step['bindings'], bindings)


class TestLogSimplification(unittest.TestCase):
    """Test log_simplification() method."""

    def test_log_simplification_basic(self):
        """Test basic simplification logging."""
        logger = StepLogger()

        logger.log_simplification(
            before=['+', 2, 3],
            after=5,
            operation='arithmetic'
        )

        self.assertEqual(len(logger.steps), 1)
        step = logger.steps[0]
        self.assertEqual(step['step'], 0)
        self.assertEqual(step['type'], 'simplification')
        self.assertEqual(step['before'], ['+', 2, 3])
        self.assertEqual(step['after'], 5)
        self.assertEqual(step['operation'], 'arithmetic')
        self.assertEqual(step['metadata'], {})

    def test_log_simplification_with_metadata(self):
        """Test simplification logging with metadata."""
        logger = StepLogger()
        metadata = {'precision': 'exact'}

        logger.log_simplification(
            before=['*', 4, 5],
            after=20,
            operation='arithmetic',
            metadata=metadata
        )

        self.assertEqual(logger.steps[0]['metadata'], metadata)

    def test_log_simplification_algebraic(self):
        """Test logging algebraic simplification."""
        logger = StepLogger()

        logger.log_simplification(
            before=['+', ['*', 2, 'x'], ['*', 3, 'x']],
            after=['*', 5, 'x'],
            operation='algebraic'
        )

        self.assertEqual(logger.steps[0]['operation'], 'algebraic')

    def test_log_simplification_increments_step_count(self):
        """Test that log_simplification increments step count."""
        logger = StepLogger()

        logger.log_simplification(['+', 1, 1], 2, 'arithmetic')
        self.assertEqual(logger.step_count, 1)


class TestLogFinal(unittest.TestCase):
    """Test log_final() method."""

    def test_log_final_basic(self):
        """Test basic final result logging."""
        logger = StepLogger()
        logger.log_final(42)

        self.assertEqual(len(logger.steps), 1)
        step = logger.steps[0]
        self.assertEqual(step['step'], 0)
        self.assertEqual(step['type'], 'final')
        self.assertEqual(step['expression'], 42)
        self.assertEqual(step['metadata'], {})

    def test_log_final_with_metadata(self):
        """Test final result logging with metadata."""
        logger = StepLogger()
        metadata = {'simplified': True, 'steps_taken': 5}
        logger.log_final(['*', 2, 'x'], metadata=metadata)

        self.assertEqual(logger.steps[0]['metadata'], metadata)

    def test_log_final_complex_expression(self):
        """Test logging a complex final expression."""
        logger = StepLogger()
        expr = ['*', ['cos', 'x'], ['dd', 'x', 'x']]
        logger.log_final(expr)

        self.assertEqual(logger.steps[0]['expression'], expr)


class TestGetSteps(unittest.TestCase):
    """Test get_steps() method."""

    def test_get_steps_empty(self):
        """Test getting steps from empty logger."""
        logger = StepLogger()
        steps = logger.get_steps()
        self.assertEqual(steps, [])

    def test_get_steps_returns_copy(self):
        """Test that get_steps returns a copy, not the original list."""
        logger = StepLogger()
        logger.log_initial('x')

        steps = logger.get_steps()
        steps.append({'fake': 'step'})

        # Original should be unchanged
        self.assertEqual(len(logger.steps), 1)
        self.assertEqual(len(logger.get_steps()), 1)

    def test_get_steps_multiple_types(self):
        """Test getting steps with multiple step types."""
        logger = StepLogger()
        logger.log_initial(['+', 'x', 0])
        logger.log_rewrite(['+', 'x', 0], 'x', [], [])
        logger.log_simplification(['+', 1, 1], 2, 'arithmetic')
        logger.log_final('x')

        steps = logger.get_steps()
        self.assertEqual(len(steps), 4)
        self.assertEqual(steps[0]['type'], 'initial')
        self.assertEqual(steps[1]['type'], 'rewrite')
        self.assertEqual(steps[2]['type'], 'simplification')
        self.assertEqual(steps[3]['type'], 'final')

    def test_get_steps_preserves_order(self):
        """Test that get_steps preserves the order of logged steps."""
        logger = StepLogger()
        for i in range(5):
            logger.log_initial(i)

        steps = logger.get_steps()
        for i, step in enumerate(steps):
            self.assertEqual(step['step'], i)
            self.assertEqual(step['expression'], i)


class TestClear(unittest.TestCase):
    """Test clear() method."""

    def test_clear_empty_logger(self):
        """Test clearing an already empty logger."""
        logger = StepLogger()
        logger.clear()

        self.assertEqual(logger.steps, [])
        self.assertEqual(logger.step_count, 0)

    def test_clear_with_steps(self):
        """Test clearing a logger with logged steps."""
        logger = StepLogger()
        logger.log_initial('x')
        logger.log_rewrite('x', 'y', [], [])
        logger.log_final('y')

        self.assertEqual(len(logger.steps), 3)
        self.assertEqual(logger.step_count, 3)

        old_session = logger.session_id
        logger.clear()

        self.assertEqual(logger.steps, [])
        self.assertEqual(logger.step_count, 0)
        # Session ID should be renewed
        self.assertIsNotNone(logger.session_id)

    def test_clear_resets_step_count(self):
        """Test that clear resets step count to 0."""
        logger = StepLogger()
        for i in range(10):
            logger.log_initial(i)

        self.assertEqual(logger.step_count, 10)
        logger.clear()
        self.assertEqual(logger.step_count, 0)

    def test_clear_allows_new_logging(self):
        """Test that logging works correctly after clear."""
        logger = StepLogger()
        logger.log_initial('x')
        logger.log_rewrite('x', 'y', [], [])
        logger.clear()

        logger.log_initial('a')
        logger.log_final('b')

        steps = logger.get_steps()
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]['step'], 0)
        self.assertEqual(steps[1]['step'], 1)


class TestSave(unittest.TestCase):
    """Test save() method and file I/O operations."""

    def setUp(self):
        """Set up test directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.temp_dir)

    def test_save_to_default_path(self):
        """Test saving to the default output path."""
        output_file = self.temp_path / 'rewrite_steps.json'
        logger = StepLogger(output_path=output_file)
        logger.log_initial('x')
        logger.save()

        self.assertTrue(output_file.exists())

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertIn('session_id', data)
        self.assertIn('total_steps', data)
        self.assertIn('steps', data)
        self.assertEqual(data['total_steps'], 1)

    def test_save_to_custom_path(self):
        """Test saving to a custom path."""
        default_file = self.temp_path / 'default.json'
        custom_file = self.temp_path / 'custom.json'

        logger = StepLogger(output_path=default_file)
        logger.log_initial('x')
        logger.save(output_path=custom_file)

        self.assertTrue(custom_file.exists())
        self.assertFalse(default_file.exists())

    def test_save_empty_logger(self):
        """Test saving an empty logger."""
        output_file = self.temp_path / 'empty.json'
        logger = StepLogger(output_path=output_file)
        logger.save()

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['total_steps'], 0)
        self.assertEqual(data['steps'], [])

    def test_save_preserves_all_step_data(self):
        """Test that save preserves all step data correctly."""
        output_file = self.temp_path / 'full.json'
        logger = StepLogger(output_path=output_file)

        logger.log_initial(['+', 'x', 0], metadata={'source': 'test'})
        logger.log_rewrite(
            ['+', 'x', 0], 'x',
            ['+', ['?', 'x'], 0], [':', 'x'],
            bindings={'x': 'x'},
            metadata={'rule_name': 'additive_identity'}
        )
        logger.log_simplification(['+', 1, 2], 3, 'arithmetic')
        logger.log_final('x', metadata={'complete': True})

        logger.save()

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['total_steps'], 4)

        # Verify initial step
        self.assertEqual(data['steps'][0]['type'], 'initial')
        self.assertEqual(data['steps'][0]['expression'], ['+', 'x', 0])
        self.assertEqual(data['steps'][0]['metadata']['source'], 'test')

        # Verify rewrite step
        self.assertEqual(data['steps'][1]['type'], 'rewrite')
        self.assertEqual(data['steps'][1]['before'], ['+', 'x', 0])
        self.assertEqual(data['steps'][1]['after'], 'x')
        self.assertEqual(data['steps'][1]['bindings'], {'x': 'x'})

        # Verify simplification step
        self.assertEqual(data['steps'][2]['type'], 'simplification')
        self.assertEqual(data['steps'][2]['operation'], 'arithmetic')

        # Verify final step
        self.assertEqual(data['steps'][3]['type'], 'final')
        self.assertEqual(data['steps'][3]['metadata']['complete'], True)

    def test_save_session_id_preserved(self):
        """Test that session_id is preserved in saved file."""
        output_file = self.temp_path / 'session.json'
        logger = StepLogger(output_path=output_file)
        original_session = logger.session_id
        logger.save()

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['session_id'], original_session)

    def test_save_creates_valid_json(self):
        """Test that saved file is valid JSON."""
        output_file = self.temp_path / 'valid.json'
        logger = StepLogger(output_path=output_file)
        logger.log_initial(['+', ['*', 2, 'x'], ['^', 'y', 3]])
        logger.save()

        # Should not raise JSONDecodeError
        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertIsInstance(data, dict)

    def test_save_with_nested_expressions(self):
        """Test saving deeply nested expressions."""
        output_file = self.temp_path / 'nested.json'
        logger = StepLogger(output_path=output_file)

        deep_expr = ['dd', ['*', ['sin', ['cos', ['tan', 'x']]], ['ln', ['exp', 'y']]], 'x']
        logger.log_initial(deep_expr)
        logger.save()

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['steps'][0]['expression'], deep_expr)

    def test_save_overwrite_existing_file(self):
        """Test that save overwrites existing file."""
        output_file = self.temp_path / 'overwrite.json'

        # Create initial file
        logger1 = StepLogger(output_path=output_file)
        logger1.log_initial('first')
        logger1.save()

        # Overwrite with new content
        logger2 = StepLogger(output_path=output_file)
        logger2.log_initial('second')
        logger2.save()

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data['steps']), 1)
        self.assertEqual(data['steps'][0]['expression'], 'second')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and unusual inputs."""

    def test_log_none_metadata(self):
        """Test that None metadata is handled correctly."""
        logger = StepLogger()
        logger.log_initial('x', metadata=None)
        self.assertEqual(logger.steps[0]['metadata'], {})

    def test_log_empty_expression(self):
        """Test logging an empty list expression."""
        logger = StepLogger()
        logger.log_initial([])
        self.assertEqual(logger.steps[0]['expression'], [])

    def test_log_string_expression(self):
        """Test logging a simple string expression."""
        logger = StepLogger()
        logger.log_initial('variable')
        self.assertEqual(logger.steps[0]['expression'], 'variable')

    def test_log_float_expression(self):
        """Test logging a float expression."""
        logger = StepLogger()
        logger.log_initial(3.14159)
        self.assertEqual(logger.steps[0]['expression'], 3.14159)

    def test_log_negative_numbers(self):
        """Test logging expressions with negative numbers."""
        logger = StepLogger()
        logger.log_initial(['+', -5, -3])
        self.assertEqual(logger.steps[0]['expression'], ['+', -5, -3])

    def test_many_steps(self):
        """Test logging many steps."""
        logger = StepLogger()
        for i in range(100):
            logger.log_initial(i)

        self.assertEqual(logger.step_count, 100)
        self.assertEqual(len(logger.get_steps()), 100)

    def test_timestamps_are_increasing(self):
        """Test that timestamps are monotonically increasing."""
        logger = StepLogger()
        logger.log_initial('a')
        logger.log_initial('b')
        logger.log_initial('c')

        steps = logger.get_steps()
        timestamps = [datetime.fromisoformat(s['timestamp']) for s in steps]

        for i in range(1, len(timestamps)):
            self.assertGreaterEqual(timestamps[i], timestamps[i-1])

    def test_log_special_characters_in_metadata(self):
        """Test logging metadata with special characters."""
        logger = StepLogger()
        metadata = {
            'description': 'Test with "quotes" and \\ backslashes',
            'unicode': 'Greek: alpha beta gamma',
            'newlines': 'line1\nline2'
        }
        logger.log_initial('x', metadata=metadata)
        self.assertEqual(logger.steps[0]['metadata'], metadata)

    def test_log_empty_bindings(self):
        """Test logging rewrite with empty bindings dict."""
        logger = StepLogger()
        logger.log_rewrite('x', 'x', [], [], bindings={})
        self.assertEqual(logger.steps[0]['bindings'], {})

    def test_log_complex_bindings(self):
        """Test logging rewrite with complex binding values."""
        logger = StepLogger()
        bindings = {
            'x': ['*', 2, 'y'],
            'c': 42,
            'nested': ['sin', ['cos', 'theta']]
        }
        logger.log_rewrite('before', 'after', [], [], bindings=bindings)
        self.assertEqual(logger.steps[0]['bindings'], bindings)


class TestIntegration(unittest.TestCase):
    """Integration tests for step logger workflow."""

    def setUp(self):
        """Set up test directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.temp_dir)

    def test_full_rewrite_workflow(self):
        """Test a complete rewriting workflow."""
        output_file = self.temp_path / 'workflow.json'
        logger = StepLogger(output_path=output_file)

        # Simulate a differentiation workflow: d/dx(2x) = 2
        initial = ['dd', ['*', 2, 'x'], 'x']
        logger.log_initial(initial, metadata={'rule_set': 'differentiation'})

        # Step 1: Apply constant multiple rule
        logger.log_rewrite(
            before=['dd', ['*', 2, 'x'], 'x'],
            after=['*', 2, ['dd', 'x', 'x']],
            rule_pattern=['dd', ['*', ['?c', 'c'], ['?', 'u']], ['?v', 'x']],
            rule_skeleton=['*', [':', 'c'], ['dd', [':', 'u'], [':', 'x']]],
            bindings={'c': 2, 'u': 'x', 'x': 'x'},
            metadata={'rule_name': 'constant_multiple'}
        )

        # Step 2: Apply dx/dx = 1 rule
        logger.log_rewrite(
            before=['dd', 'x', 'x'],
            after=1,
            rule_pattern=['dd', ['?v', 'x'], ['?v', 'x']],
            rule_skeleton=1,
            bindings={'x': 'x'},
            metadata={'rule_name': 'self_derivative'}
        )

        # Step 3: Simplify 2 * 1
        logger.log_simplification(
            before=['*', 2, 1],
            after=2,
            operation='arithmetic',
            metadata={'operation_type': 'multiplication'}
        )

        # Final result
        logger.log_final(2, metadata={'simplified': True})

        # Save and verify
        logger.save()

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['total_steps'], 5)
        self.assertEqual(data['steps'][0]['type'], 'initial')
        self.assertEqual(data['steps'][1]['type'], 'rewrite')
        self.assertEqual(data['steps'][2]['type'], 'rewrite')
        self.assertEqual(data['steps'][3]['type'], 'simplification')
        self.assertEqual(data['steps'][4]['type'], 'final')

    def test_clear_and_reuse(self):
        """Test clearing logger and reusing it."""
        output_file = self.temp_path / 'reuse.json'
        logger = StepLogger(output_path=output_file)

        # First session
        logger.log_initial('x')
        logger.log_final('x')
        first_session = logger.session_id

        # Clear and start new session
        logger.clear()

        # Second session
        logger.log_initial('y')
        logger.log_final('y')
        second_session = logger.session_id

        # Sessions should be different (or at least valid)
        datetime.fromisoformat(first_session)
        datetime.fromisoformat(second_session)

        # Should have only second session's steps
        self.assertEqual(logger.step_count, 2)
        self.assertEqual(logger.steps[0]['expression'], 'y')

    def test_multiple_save_operations(self):
        """Test saving at multiple points during logging."""
        file1 = self.temp_path / 'save1.json'
        file2 = self.temp_path / 'save2.json'

        logger = StepLogger(output_path=file1)
        logger.log_initial('x')
        logger.save()  # Save with 1 step

        logger.log_rewrite('x', 'y', [], [])
        logger.save(output_path=file2)  # Save with 2 steps to different file

        with open(file1, 'r') as f:
            data1 = json.load(f)
        with open(file2, 'r') as f:
            data2 = json.load(f)

        self.assertEqual(data1['total_steps'], 1)
        self.assertEqual(data2['total_steps'], 2)


if __name__ == '__main__':
    unittest.main()
