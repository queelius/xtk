# REPL Refactoring - Pure Rule-Based Design

## Date: 2025-10-08

## Motivation

The original REPL had hardcoded "magic" commands like `/diff`, `/factor`, `/expand` that automatically loaded and applied rules. This violated the core principle of XTK as a **pure rule-based term rewriting system**.

## Changes Made

### 1. Removed Special Operation Commands

**Deleted commands:**
- `/diff <var>` - Differentiation
- `/expand` - Expansion
- `/factor` - Factoring

**Rationale:** These operations should be expressed as **operators in expressions**, not as special commands. This makes the system:
- **Consistent**: Everything uses the same rewriting mechanism
- **Transparent**: Users see exactly what's happening
- **Flexible**: Can combine any rules, create custom operators

### 2. Renamed `/simplify` to `/rewrite`

**Old:** `/simplify`
**New:** `/rewrite` (with `/rw` alias)

**Rationale:**
- "Simplify" implies making expressions simpler
- Rewrite rules can expand, factor, differentiate, etc.
- "Rewrite" accurately describes the operation: apply loaded rules

### 3. Updated Documentation

Files updated:
- `src/xtk/cli.py` (601 lines) - Core REPL implementation
- `REPL_GUIDE.md` (359 lines) - Complete user guide
- `README.md` - Quick start examples
- `examples/repl_demo.py` - Demo script

### 4. New Workflow

**Before (inconsistent):**
```
xtk> (^ x 2)
xtk> /diff x          # Magic command
d/dx: (* 2 x)
```

**After (pure rule-based):**
```
xtk> /rules load src/xtk/rules/deriv_rules.py
xtk> (dd (^ x 2) x)   # dd is an operator in the expression
xtk> /rewrite         # Apply loaded rules uniformly
Rewritten: (* (* 2 (^ x 1)) 1)
```

## Benefits

### 1. Pedagogical Clarity
Users learn that operations are just expressions that get rewritten according to rules.

### 2. Transparency
```
xtk> /rules              # See exactly what rules are active
xtk> (dd (^ x 2) x)      # See the expression structure
xtk> /tree               # Visualize it
xtk> /rewrite            # Apply rules
xtk> /trace              # See step-by-step rewriting
```

### 3. Flexibility
```
xtk> /rules load deriv_rules.py
xtk> /rules load algebra_rules.py
xtk> /rules load custom_rules.json
xtk> (dd (expand (* (+ x 1) (+ x 2))) x)
xtk> /rewrite            # All rules apply uniformly
```

### 4. Consistency
- **One command** for all rewriting: `/rewrite` (or `/rw`)
- **One mechanism** for all operations: term rewriting
- **One format** for operations: expressions with operators

## Core Design Principles

### Everything is an Expression
```python
# Operations are operators in expressions
(dd (^ x 2) x)           # Derivative
(expand (* (+ a b) c))   # Expansion
(factor (+ (* x x) x))   # Factoring
(+ x 0)                  # Arithmetic
```

### Rules Define Semantics
```python
# Differentiation rule
[['dd', ['^', ['?', 'x'], ['?c', 'n']], ['?', 'x']],
 ['*', ['*', [':', 'n'], ['^', [':', 'x'], ['-', [':', 'n'], 1]]], 1]]

# Applies to: (dd (^ x 2) x) → (* (* 2 (^ x 1)) 1)
```

### Uniform Rewriting
```python
# One command applies ALL loaded rules
/rewrite  # or /rw for short
```

## Migration Guide

### Old → New

| Old Command | New Approach |
|-------------|--------------|
| `(^ x 2)` then `/diff x` | `(dd (^ x 2) x)` then `/rewrite` |
| `expr` then `/expand` | `(expand expr)` then `/rewrite` |
| `expr` then `/factor` | `(factor expr)` then `/rewrite` |
| `/simplify` | `/rewrite` or `/rw` |

### Loading Rules

```bash
# Load common rule sets
/rules load src/xtk/rules/deriv_rules.py
/rules load src/xtk/rules/algebra_rules.py

# Or create custom rules
/rules load my_custom_rules.json
```

## Technical Details

### Files Modified
- `src/xtk/cli.py`: Removed `differentiate_last()`, `expand_last()`, `factor_last()`, renamed `simplify_last()` to `rewrite_last()`
- Tab completion updated: `['rewrite', 'rw']` instead of `['simplify', 'diff', 'expand', 'factor']`
- Help text completely rewritten to emphasize rule-based approach

### Line Count Changes
- CLI: 640 lines → 601 lines (removed special methods)
- Guide: Completely rewritten (359 lines)
- Net: Simpler, more focused codebase

## Testing

All features tested and working:
```bash
✓ /rewrite and /rw aliases
✓ /help shows new command structure
✓ /tree visualization
✓ /trace for step-by-step rewriting
✓ /rules management
✓ History references ($0, $1, ans)
✓ Expression operators (dd, expand, factor)
```

## Philosophy

> "Make the implicit explicit, make the magic visible."

By removing special commands and making everything expressions + rules:
1. Users understand the system deeply
2. No hidden behavior or magic
3. Complete transparency
4. Maximum flexibility
5. Pedagogically sound for learning term rewriting

XTK is now a **pure rule-based term rewriting system** with no special cases.
