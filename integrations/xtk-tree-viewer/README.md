# XTK Tree Viewer

A simple web-based viewer for visualizing expression rewriting steps from the XTK toolkit.

## Usage

1. Generate a rewrite steps file using XTK with step logging enabled
2. Open `viewer.html` in a web browser
3. Load the JSON file containing the rewrite steps
4. Navigate through the transformation steps using the sidebar

## Features

- Visual representation of expression trees
- Step-by-step navigation through rewrites
- Display of pattern matching rules and variable bindings
- Statistics about the rewriting process
- Color-coded nodes for operators, variables, and constants

## File Format

The viewer expects a JSON file with the following structure:

```json
{
  "session_id": "timestamp",
  "total_steps": 10,
  "steps": [
    {
      "step": 0,
      "type": "initial",
      "expression": ["+", "x", 1],
      "timestamp": "..."
    },
    {
      "step": 1,
      "type": "rewrite",
      "before": ["+", "x", 1],
      "after": ["+", 1, "x"],
      "rule": {
        "pattern": ["+", ["?", "a"], ["?c", "b"]],
        "skeleton": ["+", [":", "b"], [":", "a"]]
      },
      "bindings": [["a", "x"], ["b", 1]]
    }
  ]
}
```