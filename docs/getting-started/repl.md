# Interactive REPL Guide

The XTK REPL (Read-Eval-Print Loop) provides an interactive environment for exploring symbolic expressions with rich visualizations and step-by-step transformation tracking.

## Starting the REPL

Launch the REPL from the command line:

```bash
python -m xtk.cli
```

Or if you installed XTK globally:

```bash
xtk
```

You'll see the prompt:

```
xtk>
```

## Basic Usage

### Entering Expressions

Expressions can be entered in S-expression or infix notation:

=== "S-expression"
    ```
    xtk> (+ 2 3)
    Expression: ['+', 2, 3]
    ```

=== "Infix"
    ```
    xtk> 2 + 3
    Expression: ['+', 2, 3]
    ```

### Rewriting Expressions

Use `/rewrite` or `/rw` to apply loaded rules:

```
xtk> (+ x 0)
Expression: ['+', 'x', 0]

xtk> /rewrite
Rewritten: x
```

### Tree Visualization

Display expressions as trees with `/tree`:

```
xtk> (* (+ x 2) (- y 1))
Expression: ['*', ['+', 'x', 2], ['-', 'y', 1]]

xtk> /tree
*
├── +
│   ├── x
│   └── 2
└── -
    ├── y
    └── 1
```

## REPL Commands

### Expression Management

| Command | Alias | Description |
|---------|-------|-------------|
| `/expr` | `/e` | Show current expression |
| `/tree` | `/t` | Display expression tree |
| `/clear` | `/c` | Clear current expression |

### Transformation

| Command | Alias | Description |
|---------|-------|-------------|
| `/rewrite` | `/rw` | Apply rewrite rules |
| `/simplify` | `/s` | Simplify expression |
| `/eval` | | Evaluate expression |
| `/step` | | Show step-by-step transformation |

### Rule Management

| Command | Example | Description |
|---------|---------|-------------|
| `/rules load <file>` | `/rules load deriv_rules.py` | Load rules from file |
| `/rules list` | | List loaded rules |
| `/rules clear` | | Clear all rules |
| `/rules show <n>` | `/rules show 5` | Show specific rule |

### Display Options

| Command | Description |
|---------|-------------|
| `/format s-expr` | Use S-expression format |
| `/format infix` | Use infix format |
| `/format tree` | Always show tree view |
| `/trace on` | Enable step-by-step tracing |
| `/trace off` | Disable tracing |

### Utility

| Command | Description |
|---------|-------------|
| `/help` | Show help message |
| `/exit` | Exit the REPL |
| `/history` | Show command history |
| `/save <file>` | Save session to file |

## Working with Rules

### Loading Predefined Rules

XTK includes many predefined rule sets:

```
xtk> /rules load src/xtk/rules/deriv_rules.py
Loaded 15 derivative rules

xtk> /rules load src/xtk/rules/algebra_rules.py
Loaded 23 algebra rules
```

### Viewing Loaded Rules

```
xtk> /rules list
1. dd (?c c) (?v x) => 0
2. dd (?v x) (?v x) => 1
3. dd (+ (? f) (? g)) (?v x) => (+ (dd (: f) (: x)) (dd (: g) (: x)))
...
```

### Viewing Specific Rules

```
xtk> /rules show 3
Rule 3: Sum Rule
Pattern: ['dd', ['+', ['?', 'f'], ['?', 'g']], ['?v', 'x']]
Replacement: ['+', ['dd', [':', 'f'], [':', 'x']], ['dd', [':', 'g'], [':', 'x']]]
Description: d(f+g)/dx = df/dx + dg/dx
```

## Example Sessions

### Symbolic Differentiation

```
xtk> /rules load src/xtk/rules/deriv_rules.py
Loaded 15 derivative rules

xtk> (dd (^ x 2) x)
Expression: ['dd', ['^', 'x', 2], 'x']

xtk> /rewrite
Rewritten: ['*', 2, ['^', 'x', 1]]

xtk> /rewrite
Rewritten: ['*', 2, 'x']
```

### Algebraic Simplification

```
xtk> /rules load src/xtk/rules/algebra_rules.py

xtk> (* (+ x 0) 1)
Expression: ['*', ['+', 'x', 0], 1]

xtk> /simplify
Simplified: x
```

### Step-by-Step Transformation

```
xtk> /trace on

xtk> (dd (* x x) x)
Expression: ['dd', ['*', 'x', 'x'], 'x']

xtk> /step
Step 1: Applied "Product Rule"
  Pattern: ['dd', ['*', ['?', 'f'], ['?', 'g']], ['?v', 'x']]
  Result: ['+', ['*', ['dd', 'x', 'x'], 'x'], ['*', 'x', ['dd', 'x', 'x']]]

xtk> /step
Step 2: Applied "Variable Derivative"
  Pattern: ['dd', ['?v', 'x'], ['?v', 'x']]
  Result: ['+', ['*', 1, 'x'], ['*', 'x', 1]]

xtk> /step
Step 3: Applied "Multiplication Identity"
  Pattern: ['*', 1, ['?', 'x']]
  Result: ['+', 'x', 'x']
```

## Advanced Features

### Expression History

Navigate through previous expressions:

```
xtk> (+ 2 3)
xtk> (* 4 5)
xtk> /history
1. ['+', 2, 3]
2. ['*', 4, 5]

xtk> !1
Expression: ['+', 2, 3]
```

### Saving Sessions

Save your work to replay later:

```
xtk> /save my_session.xtk
Session saved to my_session.xtk

# Later...
xtk> /load my_session.xtk
Session loaded
```

### Custom Bindings

Define custom functions and variables:

```
xtk> /bind f (lambda x (+ x 1))
xtk> /bind a 42

xtk> (f a)
Expression: ['f', 42]

xtk> /eval
Result: 43
```

## Configuration

### Customizing the REPL

Create a `.xtkrc` file in your home directory:

```python
# ~/.xtkrc
{
    "auto_simplify": true,
    "format": "infix",
    "trace": false,
    "prompt": "xtk> ",
    "theme": "monokai"
}
```

### Color Themes

Available themes:
- `monokai` (default)
- `solarized-light`
- `solarized-dark`
- `github`
- `nord`

Set with:

```
xtk> /theme nord
Theme changed to nord
```

## Tips and Tricks

### 1. Auto-completion

Use Tab to auto-complete:

```
xtk> /ru<TAB>
/rules

xtk> /rules lo<TAB>
/rules load
```

### 2. Quick Evaluation

Add `!` to evaluate immediately:

```
xtk> (+ 2 3)!
Result: 5
```

### 3. Pipe to External Tools

Export expressions to external tools:

```
xtk> (^ x 2) | /export latex
Output: x^{2}

xtk> (^ x 2) | /export python
Output: x**2
```

### 4. Multi-line Input

Use `\` for multi-line expressions:

```
xtk> (+ \
...    x \
...    y \
...    z)
Expression: ['+', 'x', 'y', 'z']
```

### 5. Batch Processing

Process multiple expressions:

```bash
cat expressions.txt | python -m xtk.cli --batch
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+C | Cancel current input |
| Ctrl+D | Exit REPL |
| Up/Down | Navigate history |
| Tab | Auto-complete |
| Ctrl+R | Reverse search history |
| Ctrl+L | Clear screen |

## Troubleshooting

### Expression Not Simplifying

If an expression isn't simplifying:

1. Check that appropriate rules are loaded: `/rules list`
2. Enable tracing to see what's happening: `/trace on`
3. Try simplifying sub-expressions first
4. Verify rule patterns match your expression

### Rules Not Loading

If rules fail to load:

1. Check the file path is correct
2. Ensure the file contains valid Python
3. Look for syntax errors in rule definitions
4. Check permissions on the file

### Performance Issues

For large expressions:

1. Disable tracing: `/trace off`
2. Disable auto-simplification in config
3. Use more specific rules
4. Consider breaking into smaller sub-problems

## Next Steps

- Explore [Pattern Matching](../user-guide/pattern-matching.md) in depth
- Learn about [Custom Rules](../advanced/custom-rules.md)
- See [Examples](../examples/differentiation.md) for real-world use cases
