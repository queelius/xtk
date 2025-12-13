# Search Algorithms API Reference

XTK provides tree search algorithms for exploring expression spaces. These are useful for theorem proving, finding transformation paths, and discovering simplifications.

## Module Structure

Search algorithms are located in `xtk.search`:

```
xtk/search/
    bfs.py          # Breadth-first search
    dfs.py          # Depth-first search
    iddfs.py        # Iterative deepening DFS
    best_first.py   # Best-first search
    astar.py        # A* search
    mcts.py         # Monte Carlo tree search
```

## Common Interface

All search functions share a similar signature:

```python
def search(
    initial: ExprType,
    rules: List[RuleType],
    goal_test: Callable[[ExprType], bool],
    **kwargs
) -> Optional[List[ExprType]]
```

**Common Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `initial` | `ExprType` | Starting expression |
| `rules` | `List[RuleType]` | Rewrite rules to apply |
| `goal_test` | `Callable` | Function returning `True` when goal reached |

**Returns:**

List of expressions from initial to goal (the path), or `None` if no path found.

## Breadth-First Search

### bfs_search

```python
from xtk.search.bfs import bfs_search

def bfs_search(
    initial: ExprType,
    rules: List[RuleType],
    goal_test: Callable[[ExprType], bool],
    max_depth: int = 100,
    max_nodes: int = 10000
) -> Optional[List[ExprType]]
```

Explores all nodes at current depth before going deeper. Guarantees shortest path.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_depth` | `int` | 100 | Maximum search depth |
| `max_nodes` | `int` | 10000 | Maximum nodes to explore |

**Example:**

```python
from xtk.search.bfs import bfs_search

rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
]

def goal(expr):
    return expr == 'x'

path = bfs_search(['+', ['*', 'x', 1], 0], rules, goal)
# Returns: [['+', ['*', 'x', 1], 0], ['+', 'x', 0], 'x']
```

## Depth-First Search

### dfs_search

```python
from xtk.search.dfs import dfs_search

def dfs_search(
    initial: ExprType,
    rules: List[RuleType],
    goal_test: Callable[[ExprType], bool],
    max_depth: int = 100
) -> Optional[List[ExprType]]
```

Explores as deep as possible before backtracking. Memory efficient but may not find shortest path.

**Example:**

```python
from xtk.search.dfs import dfs_search

path = dfs_search(initial, rules, goal, max_depth=50)
```

## Iterative Deepening DFS

### iddfs_search

```python
from xtk.search.iddfs import iddfs_search

def iddfs_search(
    initial: ExprType,
    rules: List[RuleType],
    goal_test: Callable[[ExprType], bool],
    max_depth: int = 100
) -> Optional[List[ExprType]]
```

Combines DFS memory efficiency with BFS completeness. Finds shortest path with DFS memory usage.

**Example:**

```python
from xtk.search.iddfs import iddfs_search

path = iddfs_search(initial, rules, goal)
```

## Best-First Search

### best_first_search

```python
from xtk.search.best_first import best_first_search

def best_first_search(
    initial: ExprType,
    rules: List[RuleType],
    goal_test: Callable[[ExprType], bool],
    heuristic: Callable[[ExprType], float],
    max_nodes: int = 10000
) -> Optional[List[ExprType]]
```

Uses a heuristic to prioritize exploration. Good for goal-directed search.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `heuristic` | `Callable` | Function estimating distance to goal (higher = better) |

**Example:**

```python
from xtk.search.best_first import best_first_search

def heuristic(expr):
    """Prefer smaller expressions."""
    def size(e):
        if isinstance(e, list):
            return 1 + sum(size(x) for x in e)
        return 1
    return -size(expr)  # Negative because we maximize

path = best_first_search(initial, rules, goal, heuristic)
```

## A* Search

### astar_search

```python
from xtk.search.astar import astar_search

def astar_search(
    initial: ExprType,
    rules: List[RuleType],
    goal_test: Callable[[ExprType], bool],
    heuristic: Callable[[ExprType], float],
    cost_fn: Callable[[ExprType, ExprType], float] = lambda a, b: 1,
    max_nodes: int = 10000
) -> Optional[List[ExprType]]
```

Optimal pathfinding combining path cost and heuristic.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `heuristic` | `Callable` | Estimated cost to goal (must be admissible) |
| `cost_fn` | `Callable` | Cost of transition between states |

**Example:**

```python
from xtk.search.astar import astar_search

def heuristic(expr):
    """Estimate distance to goal."""
    return expression_difference(expr, target)

def cost(from_expr, to_expr):
    """Cost of applying a rule."""
    return 1  # Uniform cost

path = astar_search(initial, rules, goal, heuristic, cost)
```

## Monte Carlo Tree Search

### mcts_search

```python
from xtk.search.mcts import mcts_search

def mcts_search(
    initial: ExprType,
    rules: List[RuleType],
    goal_test: Callable[[ExprType], bool],
    iterations: int = 1000,
    exploration_weight: float = 1.414
) -> Optional[List[ExprType]]
```

Uses random sampling for large search spaces.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `iterations` | `int` | Number of MCTS iterations |
| `exploration_weight` | `float` | UCB exploration parameter |

**Example:**

```python
from xtk.search.mcts import mcts_search

path = mcts_search(initial, rules, goal, iterations=5000)
```

## Helper Functions

### apply_all_rules

```python
def apply_all_rules(
    expr: ExprType,
    rules: List[RuleType]
) -> List[ExprType]
```

Generate all expressions reachable by applying one rule.

**Example:**

```python
from xtk.search.utils import apply_all_rules

successors = apply_all_rules(expr, rules)
```

### expression_hash

```python
def expression_hash(expr: ExprType) -> str
```

Create a hashable string representation of an expression.

```python
from xtk.search.utils import expression_hash

key = expression_hash(['+', 'x', 0])  # "['+'.'x'.0]"
```

## Heuristic Design

### Size-Based Heuristic

```python
def size_heuristic(expr):
    """Prefer smaller expressions."""
    def size(e):
        if isinstance(e, list):
            return 1 + sum(size(x) for x in e)
        return 1
    return -size(expr)
```

### Similarity Heuristic

```python
def similarity_heuristic(target):
    """Create heuristic based on similarity to target."""
    def flatten(e):
        if isinstance(e, list):
            return [e[0]] + sum([flatten(x) for x in e[1:]], [])
        return [e]

    target_elems = set(flatten(target))

    def heuristic(expr):
        expr_elems = set(flatten(expr))
        return len(expr_elems & target_elems)

    return heuristic
```

### Composite Heuristic

```python
def combined_heuristic(expr, target):
    """Combine multiple heuristics."""
    size_score = -expression_size(expr)
    similarity_score = expression_similarity(expr, target)
    return 0.3 * size_score + 0.7 * similarity_score
```

## Performance Comparison

| Algorithm | Time | Space | Optimal | Complete |
|-----------|------|-------|---------|----------|
| BFS | O(b^d) | O(b^d) | Yes | Yes |
| DFS | O(b^m) | O(m) | No | No |
| IDDFS | O(b^d) | O(d) | Yes | Yes |
| Best-First | O(b^m) | O(b^m) | No | No |
| A* | O(b^d) | O(b^d) | Yes* | Yes |
| MCTS | Varies | O(n) | No | No |

Where: b = branching factor, d = solution depth, m = maximum depth

*A* is optimal with admissible heuristic

## See Also

- [Search Algorithms Guide](../advanced/search-algorithms.md)
- [Theorem Proving](../advanced/theorem-proving.md)
- [Rewriter API](rewriter.md)
