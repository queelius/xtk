#!/usr/bin/env python3
"""
Advanced examples using the Lisp-like DSL in xtk.

These examples demonstrate sophisticated symbolic computation including:
- Complex pattern matching and rewriting
- Symbolic differentiation and integration
- Theorem proving
- Abstract algebra
- Functional programming constructs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtk import Expression, parse_sexpr, simplifier, match, instantiate, empty_dictionary


def example_automatic_differentiation():
    """Advanced automatic differentiation with chain rule."""
    print("\n" + "="*60)
    print("AUTOMATIC DIFFERENTIATION WITH CHAIN RULE")
    print("="*60)
    
    # Define sophisticated differentiation rules using Lisp DSL
    diff_rules_lisp = [
        # Product rule: d(f*g) = f'*g + f*g'
        "(dd (* (? f) (? g)) (?v x))",
        "(+ (* (dd (: f) (: x)) (: g)) (* (: f) (dd (: g) (: x))))",
        
        # Quotient rule: d(f/g) = (f'*g - f*g')/g²
        "(dd (/ (? f) (? g)) (?v x))",
        "(/ (- (* (dd (: f) (: x)) (: g)) (* (: f) (dd (: g) (: x)))) (^ (: g) 2))",
        
        # Chain rule for composite functions: d(f(g(x))) = f'(g(x)) * g'(x)
        "(dd (compose (? f) (? g)) (?v x))",
        "(* (dd (: f) (: g)) (dd (: g) (: x)))",
        
        # Exponential function with chain rule
        "(dd (exp (? u)) (?v x))",
        "(* (exp (: u)) (dd (: u) (: x)))",
        
        # Logarithm with chain rule
        "(dd (log (? u)) (?v x))",
        "(* (/ 1 (: u)) (dd (: u) (: x)))",
        
        # Power rule with chain rule: d(u^n)/dx = n*u^(n-1)*u'
        "(dd (^ (? u) (?c n)) (?v x))",
        "(* (* (: n) (^ (: u) (- (: n) 1))) (dd (: u) (: x)))",
    ]
    
    # Convert rules to nested list format
    rules = []
    for i in range(0, len(diff_rules_lisp), 2):
        pattern = parse_sexpr(diff_rules_lisp[i])
        skeleton = parse_sexpr(diff_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    # Example: differentiate e^(x²+3x)
    expr = parse_sexpr("(dd (exp (+ (^ x 2) (* 3 x))) x)")
    print(f"Expression: {Expression(expr).to_string()}")
    
    # Apply differentiation rules
    simplify = simplifier(rules)
    result = simplify(expr)
    print(f"Derivative: {Expression(result).to_string()}")


def example_theorem_proving():
    """Prove mathematical theorems using rewrite rules."""
    print("\n" + "="*60)
    print("THEOREM PROVING WITH REWRITE RULES")
    print("="*60)
    
    # Define algebraic identities for theorem proving
    algebra_rules_lisp = [
        # Distributivity
        "(* (? a) (+ (? b) (? c)))",
        "(+ (* (: a) (: b)) (* (: a) (: c)))",
        
        # Associativity of addition
        "(+ (+ (? a) (? b)) (? c))",
        "(+ (: a) (+ (: b) (: c)))",
        
        # Commutativity
        "(+ (? a) (? b))",
        "(+ (: b) (: a))",
        
        # Identity elements
        "(+ (? x) 0)", "(: x)",
        "(* (? x) 1)", "(: x)",
        "(* (? x) 0)", "0",
        
        # Inverse elements
        "(+ (? x) (- 0 (? x)))", "0",
        "(* (? x) (/ 1 (? x)))", "1",
        
        # Exponent laws
        "(* (^ (? x) (? a)) (^ (? x) (? b)))",
        "(^ (: x) (+ (: a) (: b)))",
        
        "(^ (^ (? x) (? a)) (? b))",
        "(^ (: x) (* (: a) (: b)))",
        
        # Special identities
        "(- (^ (? a) 2) (^ (? b) 2))",
        "(* (+ (: a) (: b)) (- (: a) (: b)))",
    ]
    
    rules = []
    for i in range(0, len(algebra_rules_lisp), 2):
        pattern = parse_sexpr(algebra_rules_lisp[i])
        skeleton = parse_sexpr(algebra_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    # Prove: (a+b)² = a² + 2ab + b²
    print("\nTheorem: (a+b)² = a² + 2ab + b²")
    
    lhs = parse_sexpr("(^ (+ a b) 2)")
    print(f"LHS: {Expression(lhs).to_string()}")
    
    # Add expansion rule for (a+b)²
    expansion_rule = [
        parse_sexpr("(^ (+ (? a) (? b)) 2)"),
        parse_sexpr("(+ (+ (^ (: a) 2) (* 2 (* (: a) (: b)))) (^ (: b) 2))")
    ]
    
    simplify = simplifier([expansion_rule])
    rhs = simplify(lhs)
    print(f"RHS: {Expression(rhs).to_string()}")
    print(f"Theorem {'proved' if rhs != lhs else 'not proved'}!")


def example_lambda_calculus():
    """Lambda calculus and functional programming constructs."""
    print("\n" + "="*60)
    print("LAMBDA CALCULUS AND HIGHER-ORDER FUNCTIONS")
    print("="*60)
    
    # Define lambda calculus reduction rules
    lambda_rules_lisp = [
        # Beta reduction: ((λx.e) a) → e[x:=a]
        "(apply (lambda (?v x) (? body)) (? arg))",
        "(substitute (: body) (: x) (: arg))",
        
        # Eta reduction: (λx.(f x)) → f (if x not free in f)
        "(lambda (?v x) (apply (? f) (?v x)))",
        "(: f)",
        
        # Map function
        "(map (? f) (cons (? head) (? tail)))",
        "(cons (apply (: f) (: head)) (map (: f) (: tail)))",
        
        "(map (? f) nil)", "nil",
        
        # Fold/Reduce function
        "(fold (? f) (? init) nil)", "(: init)",
        
        "(fold (? f) (? init) (cons (? head) (? tail)))",
        "(apply (apply (: f) (: init)) (fold (: f) (: head) (: tail)))",
        
        # Filter function
        "(filter (? pred) (cons (? head) (? tail)))",
        "(if (apply (: pred) (: head)) (cons (: head) (filter (: pred) (: tail))) (filter (: pred) (: tail)))",
        
        "(filter (? pred) nil)", "nil",
        
        # Composition
        "(compose (? f) (? g))",
        "(lambda x (apply (: f) (apply (: g) x)))",
        
        # Currying
        "(curry (? f))",
        "(lambda x (lambda y (apply (apply (: f) x) y)))",
    ]
    
    rules = []
    for i in range(0, len(lambda_rules_lisp), 2):
        pattern = parse_sexpr(lambda_rules_lisp[i])
        skeleton = parse_sexpr(lambda_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    # Example: Map a function over a list
    expr = parse_sexpr("(map (lambda x (^ x 2)) (cons 1 (cons 2 (cons 3 nil))))")
    print(f"Map squares: {Expression(expr).to_string()}")
    
    # Example: Function composition
    compose_expr = parse_sexpr("(apply (compose (lambda x (+ x 1)) (lambda y (* y 2))) 3)")
    print(f"Compose (+1) and (*2) applied to 3: {Expression(compose_expr).to_string()}")


def example_group_theory():
    """Abstract algebra - Group theory operations."""
    print("\n" + "="*60)
    print("GROUP THEORY AND ABSTRACT ALGEBRA")
    print("="*60)
    
    # Define group axioms and operations
    group_rules_lisp = [
        # Group identity: e*g = g*e = g
        "(op e (? g))", "(: g)",
        "(op (? g) e)", "(: g)",
        
        # Group inverse: g*g⁻¹ = g⁻¹*g = e
        "(op (? g) (inv (? g)))", "e",
        "(op (inv (? g)) (? g))", "e",
        
        # Inverse of inverse
        "(inv (inv (? g)))", "(: g)",
        
        # Inverse of identity
        "(inv e)", "e",
        
        # Inverse of product: (ab)⁻¹ = b⁻¹a⁻¹
        "(inv (op (? a) (? b)))",
        "(op (inv (: b)) (inv (: a)))",
        
        # Power rules
        "(pow (? g) 0)", "e",
        "(pow (? g) 1)", "(: g)",
        "(pow (? g) (?c n))",
        "(op (: g) (pow (: g) (- (: n) 1)))",
        
        # Commutator [a,b] = aba⁻¹b⁻¹
        "(commutator (? a) (? b))",
        "(op (op (: a) (: b)) (op (inv (: a)) (inv (: b))))",
        
        # Conjugation: a·g·a⁻¹
        "(conjugate (? a) (? g))",
        "(op (op (: a) (: g)) (inv (: a)))",
    ]
    
    rules = []
    for i in range(0, len(group_rules_lisp), 2):
        pattern = parse_sexpr(group_rules_lisp[i])
        skeleton = parse_sexpr(group_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    # Example: Simplify group expressions
    expr1 = parse_sexpr("(op g (op (inv g) h))")
    print(f"Expression: g·g⁻¹·h = {Expression(expr1).to_string()}")
    
    expr2 = parse_sexpr("(inv (op a (op b (inv a))))")
    print(f"Expression: (a·b·a⁻¹)⁻¹ = {Expression(expr2).to_string()}")
    
    # Prove: (aba⁻¹)⁻¹ = ab⁻¹a⁻¹
    lhs = parse_sexpr("(inv (op (op a b) (inv a)))")
    print(f"\nProving: (a·b·a⁻¹)⁻¹ = a·b⁻¹·a⁻¹")
    print(f"LHS: {Expression(lhs).to_string()}")


def example_type_theory():
    """Type theory and dependent types."""
    print("\n" + "="*60)
    print("TYPE THEORY AND DEPENDENT TYPES")
    print("="*60)
    
    # Define type inference rules
    type_rules_lisp = [
        # Type of constants
        "(typeof 0 (?ctx Γ))", "Nat",
        "(typeof true (?ctx Γ))", "Bool",
        "(typeof false (?ctx Γ))", "Bool",
        
        # Function type
        "(typeof (lambda (?v x) (? body)) (?ctx Γ))",
        "(→ (typeof (: x) (: Γ)) (typeof (: body) (extend (: Γ) (: x))))",
        
        # Application
        "(typeof (apply (? f) (? x)) (?ctx Γ))",
        "(codomain (typeof (: f) (: Γ)))",
        
        # Product type (pairs)
        "(typeof (pair (? a) (? b)) (?ctx Γ))",
        "(× (typeof (: a) (: Γ)) (typeof (: b) (: Γ)))",
        
        # Sum type (either)
        "(typeof (left (? x)) (?ctx Γ))",
        "(+ (typeof (: x) (: Γ)) _)",
        
        "(typeof (right (? x)) (?ctx Γ))",
        "(+ _ (typeof (: x) (: Γ)))",
        
        # Dependent types
        "(typeof (Π (?v x) (? A) (? B)) (?ctx Γ))",
        "Type",
        
        "(typeof (Σ (?v x) (? A) (? B)) (?ctx Γ))",
        "Type",
        
        # Identity type
        "(typeof (≡ (? A) (? x) (? y)) (?ctx Γ))",
        "Type",
        
        # Type universe
        "(typeof Type (?ctx Γ))", "Type₁",
    ]
    
    rules = []
    for i in range(0, len(type_rules_lisp), 2):
        pattern = parse_sexpr(type_rules_lisp[i])
        skeleton = parse_sexpr(type_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    # Example type checking
    expr = parse_sexpr("(typeof (lambda x (+ x 1)) empty)")
    print(f"Type of (λx. x+1): {Expression(expr).to_string()}")
    
    expr2 = parse_sexpr("(typeof (pair 3 true) empty)")
    print(f"Type of (3, true): {Expression(expr2).to_string()}")


def example_category_theory():
    """Category theory constructs."""
    print("\n" + "="*60)
    print("CATEGORY THEORY")
    print("="*60)
    
    # Define category theory operations
    category_rules_lisp = [
        # Identity morphism
        "(∘ (id (? A)) (? f))", "(: f)",
        "(∘ (? f) (id (? B)))", "(: f)",
        
        # Composition associativity
        "(∘ (∘ (? f) (? g)) (? h))",
        "(∘ (: f) (∘ (: g) (: h)))",
        
        # Functor laws
        "(fmap (? F) (id (? A)))",
        "(id (apply (: F) (: A)))",
        
        "(fmap (? F) (∘ (? f) (? g)))",
        "(∘ (fmap (: F) (: f)) (fmap (: F) (: g)))",
        
        # Natural transformation
        "(nat-trans (? η) (∘ (? F) (? f)))",
        "(∘ (apply (? η) (cod (: f))) (fmap (: F) (: f)))",
        
        # Monad laws
        "(>>= (return (? x)) (? f))",
        "(apply (: f) (: x))",
        
        "(>>= (? m) return)",
        "(: m)",
        
        "(>>= (>>= (? m) (? f)) (? g))",
        "(>>= (: m) (lambda x (>>= (apply (: f) x) (: g))))",
        
        # Adjunction
        "(adj (? F) (? G))",
        "(≅ (hom (apply (: F) (? A)) (? B)) (hom (? A) (apply (: G) (? B))))",
    ]
    
    rules = []
    for i in range(0, len(category_rules_lisp), 2):
        pattern = parse_sexpr(category_rules_lisp[i])
        skeleton = parse_sexpr(category_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    print("Category theory morphisms and functors:")
    
    # Example: Functor composition
    expr = parse_sexpr("(fmap List (∘ f g))")
    print(f"List functor: fmap(f∘g) = {Expression(expr).to_string()}")
    
    # Example: Monad bind
    expr2 = parse_sexpr("(>>= (return 5) (lambda x (return (+ x 1))))")
    print(f"Monad: return 5 >>= (λx. return (x+1)) = {Expression(expr2).to_string()}")


def example_logic_programming():
    """Logic programming and unification."""
    print("\n" + "="*60)
    print("LOGIC PROGRAMMING AND UNIFICATION")
    print("="*60)
    
    # Define logic programming rules
    logic_rules_lisp = [
        # Conjunction
        "(∧ true (? p))", "(: p)",
        "(∧ (? p) true)", "(: p)",
        "(∧ false (? p))", "false",
        "(∧ (? p) false)", "false",
        
        # Disjunction
        "(∨ true (? p))", "true",
        "(∨ (? p) true)", "true",
        "(∨ false (? p))", "(: p)",
        "(∨ (? p) false)", "(: p)",
        
        # Implication
        "(→ false (? p))", "true",
        "(→ true (? p))", "(: p)",
        "(→ (? p) true)", "true",
        
        # Negation
        "(¬ true)", "false",
        "(¬ false)", "true",
        "(¬ (¬ (? p)))", "(: p)",
        
        # De Morgan's laws
        "(¬ (∧ (? p) (? q)))",
        "(∨ (¬ (: p)) (¬ (: q)))",
        
        "(¬ (∨ (? p) (? q)))",
        "(∧ (¬ (: p)) (¬ (: q)))",
        
        # Quantifiers
        "(∀ (?v x) true)", "true",
        "(∃ (?v x) false)", "false",
        
        # Unification
        "(unify (? X) (? X))", "success",
        "(unify (?var X) (? term))", "(bind (: X) (: term))",
        
        # Resolution
        "(resolve (clause (? p)) (clause (¬ (? p))))",
        "□",  # Empty clause (contradiction)
    ]
    
    rules = []
    for i in range(0, len(logic_rules_lisp), 2):
        pattern = parse_sexpr(logic_rules_lisp[i])
        skeleton = parse_sexpr(logic_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    # Example: Prove De Morgan's law
    expr = parse_sexpr("(¬ (∧ p q))")
    print(f"De Morgan: ¬(p∧q) = {Expression(expr).to_string()}")
    
    # Example: Logical inference
    expr2 = parse_sexpr("(→ (→ p q) (→ (¬ q) (¬ p)))")
    print(f"Contrapositive: (p→q) → (¬q→¬p) = {Expression(expr2).to_string()}")


def example_quantum_computing():
    """Quantum computing operations and transformations."""
    print("\n" + "="*60)
    print("QUANTUM COMPUTING OPERATIONS")
    print("="*60)
    
    # Define quantum computing rules
    quantum_rules_lisp = [
        # Pauli matrices
        "(σx |0⟩)", "|1⟩",
        "(σx |1⟩)", "|0⟩",
        "(σy |0⟩)", "(i |1⟩)",
        "(σy |1⟩)", "(- (i |0⟩))",
        "(σz |0⟩)", "|0⟩",
        "(σz |1⟩)", "(- |1⟩)",
        
        # Hadamard gate
        "(H |0⟩)", "(/ (+ |0⟩ |1⟩) (sqrt 2))",
        "(H |1⟩)", "(/ (- |0⟩ |1⟩) (sqrt 2))",
        
        # CNOT gate
        "(CNOT (⊗ |0⟩ (? target)))", "(⊗ |0⟩ (: target))",
        "(CNOT (⊗ |1⟩ |0⟩))", "(⊗ |1⟩ |1⟩)",
        "(CNOT (⊗ |1⟩ |1⟩))", "(⊗ |1⟩ |0⟩)",
        
        # Measurement
        "(measure (+ (? α |0⟩) (? β |1⟩)))",
        "(prob |0⟩ (norm² (: α)) |1⟩ (norm² (: β)))",
        
        # Entanglement
        "(entangle |00⟩)",
        "(/ (+ |00⟩ |11⟩) (sqrt 2))",
        
        # Quantum teleportation
        "(teleport (? ψ) EPR)",
        "(transmit classical-bits (reconstruct (: ψ)))",
    ]
    
    rules = []
    for i in range(0, len(quantum_rules_lisp), 2):
        pattern = parse_sexpr(quantum_rules_lisp[i])
        skeleton = parse_sexpr(quantum_rules_lisp[i+1])
        rules.append([pattern, skeleton])
    
    print("Quantum operations:")
    
    # Example: Hadamard on |0⟩
    expr = parse_sexpr("(H |0⟩)")
    print(f"H|0⟩ = {Expression(expr).to_string()}")
    
    # Example: Bell state
    expr2 = parse_sexpr("(entangle |00⟩)")
    print(f"Bell state: {Expression(expr2).to_string()}")


def main():
    """Run all advanced examples."""
    print("="*60)
    print("ADVANCED LISP DSL EXAMPLES FOR XTK")
    print("="*60)
    print("\nThese examples demonstrate sophisticated symbolic")
    print("computation using the Lisp-like DSL in xtk.")
    
    example_automatic_differentiation()
    example_theorem_proving()
    example_lambda_calculus()
    example_group_theory()
    example_type_theory()
    example_category_theory()
    example_logic_programming()
    example_quantum_computing()
    
    print("\n" + "="*60)
    print("These examples show the expressive power of the DSL")
    print("for various mathematical and computational domains.")
    print("="*60)


if __name__ == "__main__":
    main()