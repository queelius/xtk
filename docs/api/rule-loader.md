# Rule Loader API Reference

The `rule_loader` module (`xtk.rule_loader`) provides functions for loading, saving, and managing rewrite rules from various sources.

## Main Functions

### load_rules

```python
def load_rules(
    source: Union[str, Path, List]
) -> List[RuleType]
```

Load rules from various sources.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | `Union[str, Path, List]` | File path, rule list, or rule string |

**Supported Formats:**

- Python files (`.py`)
- JSON files (`.json`)
- Lisp/S-expression files (`.lisp`, `.lsp`, `.sexpr`)
- Inline rule strings

**Returns:**

List of `[pattern, skeleton]` rules.

**Examples:**

```python
from xtk.rule_loader import load_rules

# Load from Python file
rules = load_rules('src/xtk/rules/deriv_rules.py')

# Load from JSON file
rules = load_rules('my_rules.json')

# Load from Lisp file
rules = load_rules('rules.lisp')

# Pass rules directly (returns unchanged)
rules = load_rules([[['+', ['?', 'x'], 0], [':', 'x']]])

# Parse inline string
rules = load_rules('((+ (? x) 0) (: x))')
```

---

### load_python_rules

```python
def load_python_rules(path: Path) -> List[RuleType]
```

Load rules from a Python file by importing it.

The Python file should export rules as lists:

```python
# my_rules.py
my_rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
]

other_rules = [
    [['^', ['?', 'x'], 0], 1],
]
```

All list variables that look like rule sets are collected.

---

### save_rules

```python
def save_rules(
    rules: List[RuleType],
    filepath: Union[str, Path],
    format: str = None
) -> None
```

Save rules to a file.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `rules` | `List[RuleType]` | Rules to save |
| `filepath` | `Union[str, Path]` | Output file path |
| `format` | `str` | `'json'` or `'lisp'` (auto-detected if `None`) |

**Example:**

```python
from xtk.rule_loader import save_rules

rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
]

# Save as JSON
save_rules(rules, 'rules.json')

# Save as Lisp
save_rules(rules, 'rules.lisp')

# Explicit format
save_rules(rules, 'rules.txt', format='json')
```

---

### merge_rules

```python
def merge_rules(*rule_sets) -> List[RuleType]
```

Merge multiple rule sets, removing duplicates.

**Example:**

```python
from xtk.rule_loader import load_rules, merge_rules

deriv = load_rules('deriv_rules.py')
algebra = load_rules('algebra_rules.py')
trig = load_rules('trig_rules.py')

# Merge all, removing duplicates
all_rules = merge_rules(deriv, algebra, trig)
```

## Parsing Functions

### parse_rules

```python
def parse_rules(content: str) -> List[RuleType]
```

Parse rules from a string, auto-detecting format.

**Supported Formats:**

- JSON arrays
- S-expressions
- Comments with `;` or `//`

**Example:**

```python
from xtk.rule_loader import parse_rules

# JSON format
rules = parse_rules('[[["+", ["?", "x"], 0], [":", "x"]]]')

# S-expression format
rules = parse_rules('((+ (? x) 0) (: x))')

# With comments
rules = parse_rules('''
; Additive identity
((+ (? x) 0) (: x))

; Multiplicative identity
((* (? x) 1) (: x))
''')
```

---

### extract_sexprs

```python
def extract_sexprs(text: str) -> List[str]
```

Extract all complete S-expressions from text.

```python
from xtk.rule_loader import extract_sexprs

sexprs = extract_sexprs('(+ 1 2) (- 3 4)')
# Returns: ['(+ 1 2)', '(- 3 4)']
```

---

### is_rule_format

```python
def is_rule_format(expr) -> bool
```

Check if expression is a complete rule.

```python
from xtk.rule_loader import is_rule_format

is_rule_format([['+', ['?', 'x'], 0], [':', 'x']])  # True
is_rule_format(['+', 1, 2])  # False
```

## Formatting Functions

### format_rules_as_lisp

```python
def format_rules_as_lisp(rules: List[RuleType]) -> str
```

Format rules as readable Lisp expressions.

```python
from xtk.rule_loader import format_rules_as_lisp

rules = [[['+', ['?', 'x'], 0], [':', 'x']]]
lisp_str = format_rules_as_lisp(rules)
# Returns: ';;;; Rules for xtk\n((+ (? x) 0) (: x))'
```

## Rule File Formats

### Python Format

```python
# rules.py
identity_rules = [
    [['+', ['?', 'x'], 0], [':', 'x']],
    [['*', ['?', 'x'], 1], [':', 'x']],
]

power_rules = [
    [['^', ['?', 'x'], 0], 1],
    [['^', ['?', 'x'], 1], [':', 'x']],
]
```

### JSON Format

```json
[
  [["+", ["?", "x"], 0], [":", "x"]],
  [["*", ["?", "x"], 1], [":", "x"]],
  [["^", ["?", "x"], 0], 1]
]
```

### Lisp/S-expression Format

```lisp
;;;; Rules for algebra

; Additive identity
((+ (? x) 0) (: x))

; Multiplicative identity
((* (? x) 1) (: x))

; Power of zero
((^ (? x) 0) 1)
```

## Rich Rule Format

Rules can include metadata:

```python
from xtk.rule_utils import RichRule

rich_rule = RichRule(
    pattern=['+', ['?', 'x'], 0],
    skeleton=[':', 'x'],
    name="additive_identity",
    description="Adding zero yields the original value",
    category="simplification"
)
```

JSON format with metadata:

```json
{
  "pattern": ["+", ["?", "x"], 0],
  "skeleton": [":", "x"],
  "name": "additive_identity",
  "description": "Adding zero yields the original value"
}
```

## Usage Patterns

### Loading Multiple Rule Sets

```python
from xtk.rule_loader import load_rules, merge_rules
from xtk import rewriter

# Load individual rule sets
deriv = load_rules('src/xtk/rules/deriv_rules.py')
algebra = load_rules('src/xtk/rules/algebra_rules.py')

# Merge them
all_rules = merge_rules(deriv, algebra)

# Create simplifier
simplify = rewriter(all_rules)
```

### Creating Custom Rule Files

```python
from xtk.rule_loader import save_rules

my_rules = [
    # Custom domain rules
    [['foo', ['?', 'x']], ['bar', [':', 'x']]],
]

save_rules(my_rules, 'my_domain_rules.json')
```

### Runtime Rule Loading

```python
from xtk.rule_loader import load_rules
from xtk import rewriter

def create_simplifier(rule_files):
    """Create a simplifier from multiple rule files."""
    all_rules = []
    for file in rule_files:
        all_rules.extend(load_rules(file))
    return rewriter(all_rules)

simplify = create_simplifier([
    'algebra_rules.py',
    'trig_rules.py',
    'custom_rules.json'
])
```

## Error Handling

```python
from xtk.rule_loader import load_rules

try:
    rules = load_rules('nonexistent.py')
except FileNotFoundError:
    print("Rule file not found")

try:
    rules = load_rules({'invalid': 'format'})
except ValueError as e:
    print(f"Invalid source: {e}")
```

## See Also

- [Rewriter API](rewriter.md)
- [Custom Rules Guide](../advanced/custom-rules.md)
- [Rewrite Rules Guide](../user-guide/rules.md)
