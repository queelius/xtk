# LLM Rule Inference for xtk

## Overview

Optional feature that allows xtk to infer missing rewrite rules via LLM when no existing rule matches an expression. This is simpler than dreamlog's approach because xtk's term rewriting semantics are more constrained.

## Two Complementary Approaches

xtk supports two LLM integration patterns that can be used independently or together:

### 1. Inner Inference (`LLMRuleInferrer`)
- **Focused**: Only handles "missing rule" case
- **Lightweight**: Single LLM call per inference
- **Already implemented**: See `src/xtk/llm_inferrer.py`
- **Best for**: Simple rule completion, batch processing

### 2. Outer Loop Agent (`LLMRewriteAgent`)
- **Powerful**: Handles multiple error types
- **Iterative**: Can retry with corrections
- **Planned**: See Architecture section below
- **Best for**: Interactive sessions, complex debugging

```
Configuration options:
- Neither (pure rule-based)
- Just inner (simple inference)
- Just outer (full agent)
- Both (outer uses inner as a tool)
```

## Design Goals

1. **Optional** - Disabled by default, opt-in via flag or config
2. **Simple** - Much simpler than dreamlog's ~3000 line LLM subsystem
3. **Cacheable** - Don't ask the LLM twice for the same pattern
4. **Validatable** - Syntactically validate generated rules before use
5. **Explainable** - Log/show what rules were inferred and why

## Architecture

```
Expression doesn't match any rule
    ↓
LLMRuleInferrer.infer_rule(expr, existing_rules)
    ↓
Build prompt with:
  - The unmatched expression
  - Existing rules as examples (few-shot)
  - Domain context (if available)
    ↓
LLM generates rule in DSL format:
  (+ ?x 0) => :x
    ↓
Parse and validate rule:
  - Syntax valid?
  - Skeleton uses only bound variables?
  - Not a duplicate?
    ↓
Add to rule set, retry rewrite
```

## Key Components

### 1. LLMRuleInferrer

```python
class LLMRuleInferrer:
    """Infer missing rewrite rules via LLM."""

    def __init__(self,
                 provider: str = 'ollama',
                 model: str = 'phi4-mini:latest',
                 enabled: bool = False,
                 max_inferences: int = 10,
                 cache: bool = True):
        self.provider = get_provider(provider, model)
        self.enabled = enabled
        self.max_inferences = max_inferences
        self.inference_count = 0
        self.cache = {} if cache else None
        self.inferred_rules = []  # Track what was inferred

    def infer_rule(self, expr, existing_rules, context=None):
        """Attempt to infer a rule for the given expression."""
        if not self.enabled:
            return None
        if self.inference_count >= self.max_inferences:
            return None

        # Check cache
        expr_key = str(expr)
        if self.cache is not None and expr_key in self.cache:
            return self.cache[expr_key]

        # Build prompt
        prompt = self.build_prompt(expr, existing_rules, context)

        # Get response
        response = self.provider.generate(prompt)

        # Parse and validate
        rule = self.parse_rule(response)
        if rule and self.validate_rule(rule, expr):
            self.inference_count += 1
            self.inferred_rules.append((expr, rule))
            if self.cache is not None:
                self.cache[expr_key] = rule
            return rule

        return None
```

### 2. Prompt Template

```python
RULE_INFERENCE_PROMPT = '''
You are a symbolic computation expert. Given an expression that doesn't match
any existing rewrite rules, suggest a general rewrite rule that could simplify it.

## Existing Rules (for reference)
{existing_rules}

## Expression to handle
{expression}

## Response Format
Respond with ONLY a single rule in this format:
(pattern) => (skeleton)

Where:
- ?x matches any expression and binds to x
- ?c:const matches constants only
- ?v:var matches variables only
- :x in skeleton substitutes the bound value

## Example Response
(+ ?x 0) => :x
'''
```

### 3. Integration Points

**In rewriter.py:**
```python
def simplify(expr, rules, llm_inferrer=None):
    """Simplify expression, optionally inferring missing rules."""
    result = apply_rules_recursive(expr, rules)

    # If no rule matched and LLM inference is enabled
    if result == expr and llm_inferrer:
        new_rule = llm_inferrer.infer_rule(expr, rules)
        if new_rule:
            rules.append(new_rule)
            return simplify(expr, rules, llm_inferrer)

    return result
```

**In CLI:**
```python
# New command: /infer on|off
def toggle_inference(self):
    self.llm_inferrer.enabled = not self.llm_inferrer.enabled

# Show inferred rules: /inferred
def show_inferred(self):
    for expr, rule in self.llm_inferrer.inferred_rules:
        print(f"For {expr}: {format_rule(rule)}")
```

### 4. Validation

```python
def validate_rule(rule, original_expr):
    """Validate an inferred rule."""
    pattern, skeleton = rule

    # 1. Pattern must be well-formed
    if not is_valid_pattern(pattern):
        return False

    # 2. Skeleton must only use variables bound in pattern
    pattern_vars = extract_pattern_variables(pattern)
    skeleton_vars = extract_skeleton_variables(skeleton)
    if not skeleton_vars.issubset(pattern_vars):
        return False

    # 3. Pattern should match the original expression
    bindings = match(pattern, original_expr, {})
    if bindings == "failed":
        return False

    # 4. Rule shouldn't be an identity (would cause infinite loop)
    result = instantiate(skeleton, bindings)
    if result == original_expr:
        return False

    return True
```

## Configuration

```yaml
# ~/.xtk/config.yaml
llm_inference:
  enabled: false
  provider: ollama
  model: phi4-mini:latest
  max_inferences_per_session: 10
  cache_inferred_rules: true
  auto_save_inferred: false  # Save to file after session
```

## Differences from DreamLog

| Aspect | DreamLog | xtk |
|--------|----------|-----|
| Semantics | Prolog (recursive predicates) | Term rewriting (pattern→skeleton) |
| Validation | Multi-layer (structural, semantic, LLM-judge) | Single-layer (syntax + variable check) |
| Complexity | ~3000 lines | ~200 lines |
| What's inferred | Rules only (never facts) | Rewrite rules |
| Retry logic | Complex with correction | Simple retry once |
| RAG | Example retrieval with embeddings | Simple few-shot from loaded rules |

## Outer Loop Agent Architecture (Future: MCP-based)

The outer loop will be implemented as an **MCP Server**, exposing xtk's functionality as tools that any MCP-compatible agent can use.

### Planned MCP Tools

```
xtk MCP Server
├── rewrite(expr, rules) → Result | Error
├── infer_rule(expr, existing_rules) → Rule | None
├── parse(text) → AST | ParseError
├── format(expr) → string
└── validate_rule(rule) → Valid | Errors
```

### Why MCP?

1. **No agent duplication** - MCP clients (Claude, etc.) handle the loop
2. **Interoperability** - Any MCP-compatible agent can use xtk
3. **Standardized errors** - MCP has built-in error handling
4. **Composability** - xtk becomes one tool among many

### Error Types (for MCP responses)

| Error Type | Description |
|------------|-------------|
| `no_match` | No rule matched the expression |
| `unknown_op` | Unknown operator (with fuzzy suggestions) |
| `parse_error` | Syntax error in input |
| `infinite_loop` | Rewrite cycle detected |
| `validation_error` | Invalid rule structure |

The MCP client can decide how to handle each error type.

## Future Enhancements

1. **Rule quality scoring** - LLM rates confidence in generated rule
2. **Rule explanation** - LLM explains why the rule is correct
3. **Batch inference** - Infer multiple related rules at once
4. **Domain-specific prompts** - Different prompts for calculus vs algebra
5. **User approval** - Ask before adding inferred rule
6. **RAG-based retrieval** - Find similar rules from a larger corpus
7. **Learning from corrections** - Remember user corrections for future sessions
