# XTK REPL Guide

## Overview

The XTK REPL provides an interactive terminal user interface for symbolic computation with rich visual feedback, tree visualization, and step-by-step transformation tracing.

## Starting the REPL

```bash
# Start REPL
python3 -m xtk.cli

# Or with xtk installed
xtk
```

## Features

### 1. Arithmetic Evaluation

XTK now includes **automatic constant folding** - arithmetic on constants is evaluated automatically:

```
xtk> (+ 2 3)
$[0] (+ 2 3)

xtk> /rewrite
Rewritten: 5

xtk> (* (+ 4 5) (^ 2 3))
$[1] (* (+ 4 5) (^ 2 3))

xtk> /rw
Rewritten: 72
```

**No rules needed!** Constant folding works automatically for `+`, `-`, `*`, `/`, and `^`.

**Toggle constant folding** - You can disable constant folding for non-standard arithmetic:

```
xtk> (+ 2 3)
$[0] (+ 2 3)

xtk> /rw
Rewritten: 5

xtk> /constant-folding
Constant folding is now disabled

xtk> (* 4 5)
$[2] (* 4 5)

xtk> /rw
Rewritten: (* 4 5)

xtk> /constant-folding
Constant folding is now enabled
```

### 2. Expression Input

**S-expressions** (Lisp-like):
```
xtk> (+ (* 2 x) 3)
$[0] (+ (* 2 x) 3)
```

**Infix notation**:
```
xtk> 2*x + 3
$[1] (+ (* 2 x) 3)
```

### 2. Tree Visualization

```
xtk> (+ (* 2 x) (^ y 3))
$[2] (+ (* 2 x) (^ y 3))

xtk> /tree
+
├── *
│   ├── 2
│   └── x
└── ^
    ├── y
    └── 3
```

View specific history item:
```
xtk> /tree $0
xtk> /tree 2
```

### 3. History References

```
xtk> (+ x 1)
$[0] (+ x 1)

xtk> ans
ans = (+ x 1)

xtk> $0
$0 = (+ x 1)

xtk> /history
          Expression History
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Ref    ┃ Expression                ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ $0     │ (+ x 1)                   │
└────────┴───────────────────────────┘
```

### 4. Variables

```
xtk> a = (^ x 2)
a = (^ x 2)

xtk> b = ans
b = (^ x 2)

xtk> /vars
     Variables
┏━━━━━━┳━━━━━━━━━┓
┃ Name ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ a    │ (^ x 2) │
│ b    │ (^ x 2) │
└──────┴─────────┘
```

### 5. Term Rewriting with Rules

XTK is a **rule-based term rewriting system**. Operations like differentiation, expansion, and factoring are expressed as operators in expressions, then rewritten using loaded rules.

**Load rules first**:
```
xtk> /rules load src/xtk/rules/deriv_rules.py
Loaded 15 rules
```

**Differentiation** - express as `(dd <expr> <var>)`:
```
xtk> (dd (^ x 3) x)
$[0] (dd (^ x 3) x)

xtk> /rewrite
Rewritten: (* (* 3 (^ x (- 3 1))) 1)
```

**Expansion** - express as `(expand <expr>)`:
```
xtk> /rules load src/xtk/rules/algebra_rules.py
Loaded 25 rules

xtk> (expand (* (+ x 1) (+ x 2)))
$[1] (expand (* (+ x 1) (+ x 2)))

xtk> /rw
Rewritten: (+ (+ (* x x) (* 3 x)) 2)
```

**Simplification** - any expression with loaded rules:
```
xtk> (+ x 0)
$[2] (+ x 0)

xtk> /rewrite
Rewritten: x
```

### 6. Evaluation

```
xtk> (+ (* 2 x) 3)
$[0] (+ (* 2 x) 3)

xtk> /eval x=5
Result: 13
```

### 7. Step-by-Step Trace

```
xtk> (+ (* 2 0) x)
$[0] (+ (* 2 0) x)

xtk> /trace
┏━━━━━━━━━━━━━━━━━━━━━┓
┃  Rewriting Trace    ┃
┗━━━━━━━━━━━━━━━━━━━━━┛
Initial: (+ (* 2 0) x)
Step 1: (+ 0 x)
  Rule: (* _ 0) → 0
Step 2: x
  Rule: (+ 0 _) → _
Final: x
```

### 8. Rules Management

**List rules**:
```
xtk> /rules
                  Loaded Rules (15)
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━━━━━━━━━━━┓
┃ Index  ┃ Pattern           ┃ →   ┃ Skeleton      ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━━━━━━━━━━━┩
│ 0      │ (dd (?v x) (?v x))│ →   │ 1             │
│ 1      │ (dd (?c c) (?v v))│ →   │ 0             │
...
```

**Load rules**:
```
xtk> /rules load src/xtk/rules/deriv_rules.py
xtk> /rules load src/xtk/rules/algebra_rules.py
xtk> /rules load my_custom_rules.json
```

**Add a rule interactively**:
```
xtk> /rules add (+ (?v x) 0) (: x)
Added rule 0:
  (+ (?v x) 0) → (: x)

xtk> /rules add (* (?v x) 1) (: x)
Added rule 1:
  (* (?v x) 1) → (: x)

xtk> (+ a 0)
$[0] (+ a 0)

xtk> /rw
Rewritten: a
```

**Show rule details**:
```
xtk> /rules show 0
           Rule 0
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Component ┃ Value         ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Pattern   │ (+ (?v x) 0)  │
│ Skeleton  │ (:x)          │
│ ...
```

**Delete a rule**:
```
xtk> /rules delete 0
Deleted rule 0:
  (+ (?v x) 0) → (:x)
```

**Save rules**:
```
xtk> /rules save my_rules.json
```

**Clear rules**:
```
xtk> /rules clear
```

### 9. Other Commands

**LaTeX output**:
```
xtk> (+ (* 2 x) 3)
xtk> /latex
╭─ LaTeX ─╮
│ 2x + 3  │
╰─────────╯
```

**Clear screen**:
```
xtk> /clear
```

**Help**:
```
xtk> /help
```

**Quit**:
```
xtk> /quit
xtk> /exit
```

## Complete Command Reference

### Term Rewriting
- `/rewrite` or `/rw` - Apply loaded rules to rewrite last expression
- `/trace` - Show step-by-step rewriting trace

### Evaluation
- `/eval [x=5 y=3]` - Evaluate with variable bindings

### Visualization
- `/tree [index]` - Show ASCII tree of expression
- `/latex` - Show expression in LaTeX format

### Rules Management
- `/rules` - List all loaded rules
- `/rules load <file>` - Load rules from file
- `/rules save <file>` - Save rules to file
- `/rules add <pattern> <skeleton>` - Add a new rule interactively
- `/rules delete <index>` - Delete a rule by index
- `/rules show <index>` - Show details of a specific rule
- `/rules clear` - Clear all rules

### History & Variables
- `/history` - Show expression history
- `/vars` - Show defined variables
- `$0`, `$1`, `$2` - Reference history items
- `ans` - Last result

### Misc
- `/clear` - Clear the screen
- `/constant-folding` - Toggle constant folding on/off (enabled by default)
- `/help` - Show help message
- `/quit`, `/exit` - Exit the REPL

## Expression Operators

Operations are represented as functions within expressions:

- `(dd <expr> <var>)` - Derivative of expr with respect to var
- `(expand <expr>)` - Expand expression
- `(factor <expr>)` - Factor expression
- `(+ x 0)` - Addition (and other arithmetic)

The key insight: **everything is an expression**, and expressions are rewritten according to loaded rules.

## Tips

1. **Load rules first**: Most operations require rules to be loaded
2. **Tab completion**: Start typing `/` and press Tab to see available commands
3. **History**: Use `ans` or `$N` to reference previous results
4. **Variables**: Store expressions for later use with `name = expression`
5. **Visualization**: Use `/tree` to understand expression structure
6. **Tracing**: Use `/trace` to see step-by-step transformations
7. **Comments**: Lines starting with `#` are ignored (useful for scripting)
8. **Operator syntax**: Remember `dd` requires two arguments: `(dd (^ x 2) x)` not `(dd (^ x 2))`

## Examples

### Example 1: Differentiation
```
xtk> /rules load src/xtk/rules/deriv_rules.py
Loaded 15 rules

xtk> (dd (* x x) x)
$[0] (dd (* x x) x)

xtk> /rewrite
Rewritten: (+ (* 1 x) (* x 1))

xtk> /tree
+
├── *
│   ├── 1
│   └── x
└── *
    ├── x
    └── 1
```

### Example 2: Algebra
```
xtk> /rules load src/xtk/rules/algebra_rules.py
Loaded 25 rules

xtk> (+ (+ x 0) (* y 1))
$[0] (+ (+ x 0) (* y 1))

xtk> /rw
Rewritten: (+ x y)

xtk> /trace
```

### Example 3: Working with history
```
xtk> (^ x 2)
$[0] (^ x 2)

xtk> (dd ans x)
$[1] (dd (^ x 2) x)

xtk> /rw
Rewritten: (* (* 2 (^ x 1)) 1)

xtk> /history
xtk> result = $2
xtk> /eval x=5
```

### Example 4: Custom rules
```
xtk> /rules load src/xtk/rules/deriv_rules.py
xtk> /rules load src/xtk/rules/algebra_rules.py
xtk> /rules
xtk> (dd (+ (* 2 x) 3) x)
xtk> /trace
```

## Command-Line Usage

Process expressions non-interactively:

```bash
# Simple evaluation
xtk "(+ 1 2)"

# With rules and rewriting (via simplify)
xtk -s -r rules.json "(+ x 0)"

# With differentiation (express as dd operator)
xtk -s -r deriv_rules.json "(dd (^ x 2) x)"

# Tree output
xtk -f tree "(+ (* 2 x) 3)"
```

## Philosophy

XTK is a **pure rule-based system**:
- Operations are **expressions**, not special commands
- `/rewrite` applies rules uniformly to any expression
- Transparency: you see exactly what rules do
- Flexibility: combine any rules, create custom transformations

This design makes XTK powerful for symbolic computation, theorem proving, and understanding term rewriting systems.
