"""Step logger for tracking expression rewriting transformations."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

ExprType = Union[int, float, str, List[Any]]


class StepLogger:
    """Logs expression rewriting steps to a file for visualization."""
    
    def __init__(self, output_path: Optional[Union[str, Path]] = None):
        """Initialize the step logger.
        
        Args:
            output_path: Path to output file. If None, logs to 'rewrite_steps.json'
        """
        self.output_path = Path(output_path) if output_path else Path('rewrite_steps.json')
        self.steps: List[Dict[str, Any]] = []
        self.session_id = datetime.now().isoformat()
        self.step_count = 0
    
    def log_initial(self, expression: ExprType, metadata: Optional[Dict[str, Any]] = None):
        """Log the initial expression.
        
        Args:
            expression: The starting expression
            metadata: Optional metadata about the expression
        """
        self.steps.append({
            'step': self.step_count,
            'type': 'initial',
            'expression': expression,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })
        self.step_count += 1
    
    def log_rewrite(self, 
                    before: ExprType,
                    after: ExprType,
                    rule_pattern: ExprType,
                    rule_skeleton: ExprType,
                    bindings: Optional[Dict[str, Any]] = None,
                    metadata: Optional[Dict[str, Any]] = None):
        """Log a rewriting step.
        
        Args:
            before: Expression before rewriting
            after: Expression after rewriting
            rule_pattern: Pattern that matched
            rule_skeleton: Skeleton that was instantiated
            bindings: Variable bindings from pattern matching
            metadata: Optional metadata about the rewrite
        """
        self.steps.append({
            'step': self.step_count,
            'type': 'rewrite',
            'before': before,
            'after': after,
            'rule': {
                'pattern': rule_pattern,
                'skeleton': rule_skeleton
            },
            'bindings': bindings or {},
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })
        self.step_count += 1
    
    def log_simplification(self,
                          before: ExprType,
                          after: ExprType,
                          operation: str,
                          metadata: Optional[Dict[str, Any]] = None):
        """Log a simplification step.
        
        Args:
            before: Expression before simplification
            after: Expression after simplification
            operation: Type of simplification (e.g., 'arithmetic', 'algebraic')
            metadata: Optional metadata
        """
        self.steps.append({
            'step': self.step_count,
            'type': 'simplification',
            'before': before,
            'after': after,
            'operation': operation,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })
        self.step_count += 1
    
    def log_final(self, expression: ExprType, metadata: Optional[Dict[str, Any]] = None):
        """Log the final result.
        
        Args:
            expression: The final expression
            metadata: Optional metadata
        """
        self.steps.append({
            'step': self.step_count,
            'type': 'final',
            'expression': expression,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })
        self.step_count += 1
    
    def save(self, output_path: Optional[Union[str, Path]] = None):
        """Save the logged steps to a file.
        
        Args:
            output_path: Optional alternative output path
        """
        path = Path(output_path) if output_path else self.output_path
        
        output = {
            'session_id': self.session_id,
            'total_steps': self.step_count,
            'steps': self.steps
        }
        
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)
    
    def clear(self):
        """Clear all logged steps."""
        self.steps = []
        self.step_count = 0
        self.session_id = datetime.now().isoformat()
    
    def get_steps(self) -> List[Dict[str, Any]]:
        """Get all logged steps.
        
        Returns:
            List of step dictionaries
        """
        return self.steps.copy()