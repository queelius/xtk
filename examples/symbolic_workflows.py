#!/usr/bin/env python3
"""
Practical symbolic computation workflows using XTK.

This file demonstrates real-world applications of symbolic computation
for scientific computing, engineering, and mathematics education.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtk import Expression, parse_sexpr, simplifier, E
import json


def physics_kinematics():
    """Derive kinematic equations symbolically."""
    print("\n" + "="*60)
    print("PHYSICS: KINEMATIC EQUATIONS")
    print("="*60)
    
    # Define the rules for physics
    physics_rules = [
        # Definition of velocity: v = dx/dt
        [parse_sexpr("(dd x t)"), parse_sexpr("v")],
        
        # Definition of acceleration: a = dv/dt
        [parse_sexpr("(dd v t)"), parse_sexpr("a")],
        
        # Constant acceleration
        [parse_sexpr("(dd a t)"), parse_sexpr("0")],
        
        # Integration rules for kinematics
        [parse_sexpr("(integrate a t)"), parse_sexpr("(+ (* a t) v_0)")],
        [parse_sexpr("(integrate v t)"), parse_sexpr("(+ (* v t) x_0)")],
    ]
    
    print("\nDeriving kinematic equations from first principles:")
    
    # Start with acceleration
    print("Given: a = constant")
    
    # Derive velocity
    v_expr = parse_sexpr("(integrate a t)")
    print(f"v(t) = ∫a dt = {Expression(v_expr).to_string()}")
    
    # Derive position
    x_expr = parse_sexpr("(integrate (+ (* a t) v_0) t)")
    expanded = parse_sexpr("(+ (+ (* (/ 1 2) a (^ t 2)) (* v_0 t)) x_0)")
    print(f"x(t) = ∫v dt = {Expression(expanded).to_string()}")
    
    # Derive v² = v₀² + 2a(x - x₀)
    print("\nDeriving v² = v₀² + 2a(x - x₀):")
    
    # Energy approach
    energy_expr = parse_sexpr("(= (- (/ (* m (^ v 2)) 2) (/ (* m (^ v_0 2)) 2)) (* m a (- x x_0)))")
    print(f"Work-energy theorem: {Expression(energy_expr).to_string()}")
    
    simplified = parse_sexpr("(= (^ v 2) (+ (^ v_0 2) (* 2 a (- x x_0))))")
    print(f"Simplified: {Expression(simplified).to_string()}")


def engineering_control_systems():
    """Symbolic analysis of control systems."""
    print("\n" + "="*60)
    print("ENGINEERING: CONTROL SYSTEM ANALYSIS")
    print("="*60)
    
    # Define Laplace transform rules
    laplace_rules = [
        # Basic transforms
        [parse_sexpr("(L 1 s)"), parse_sexpr("(/ 1 s)")],
        [parse_sexpr("(L t s)"), parse_sexpr("(/ 1 (^ s 2))")],
        [parse_sexpr("(L (exp (* a t)) s)"), parse_sexpr("(/ 1 (- s a))")],
        [parse_sexpr("(L (sin (* ω t)) s)"), parse_sexpr("(/ ω (+ (^ s 2) (^ ω 2)))")],
        [parse_sexpr("(L (cos (* ω t)) s)"), parse_sexpr("(/ s (+ (^ s 2) (^ ω 2)))")],
        
        # Derivative property
        [parse_sexpr("(L (dd f t) s)"), parse_sexpr("(- (* s (L f s)) (f 0))")],
        
        # Integration property
        [parse_sexpr("(L (integrate f t) s)"), parse_sexpr("(/ (L f s) s)")],
    ]
    
    print("\nPID Controller Analysis:")
    
    # PID controller transfer function
    pid = parse_sexpr("(+ K_p (+ (/ K_i s) (* K_d s)))")
    print(f"PID(s) = {Expression(pid).to_string()}")
    
    # Combine terms
    combined = parse_sexpr("(/ (+ (* K_d (^ s 2)) (* K_p s) K_i) s)")
    print(f"PID(s) = {Expression(combined).to_string()}")
    
    # Closed-loop transfer function with unity feedback
    print("\nClosed-loop transfer function:")
    
    # G(s) = Plant, C(s) = Controller
    plant = parse_sexpr("(/ 1 (* s (+ s 1)))")
    print(f"Plant G(s) = {Expression(plant).to_string()}")
    
    # Closed-loop: T(s) = C(s)G(s) / (1 + C(s)G(s))
    open_loop = parse_sexpr("(* PID G)")
    closed_loop = parse_sexpr("(/ (* PID G) (+ 1 (* PID G)))")
    print(f"T(s) = {Expression(closed_loop).to_string()}")
    
    # Stability analysis using Routh-Hurwitz
    char_eq = parse_sexpr("(+ (^ s 3) (+ (* 2 (^ s 2)) (* 3 s) 1))")
    print(f"\nCharacteristic equation: {Expression(char_eq).to_string()}")


def quantum_mechanics():
    """Symbolic quantum mechanics computations."""
    print("\n" + "="*60)
    print("QUANTUM MECHANICS: OPERATOR ALGEBRA")
    print("="*60)
    
    # Define quantum operator rules
    quantum_rules = [
        # Commutation relations
        [parse_sexpr("(commutator x p)"), parse_sexpr("(* i ℏ)")],
        [parse_sexpr("(commutator L_x L_y)"), parse_sexpr("(* i ℏ L_z)")],
        [parse_sexpr("(commutator L_y L_z)"), parse_sexpr("(* i ℏ L_x)")],
        [parse_sexpr("(commutator L_z L_x)"), parse_sexpr("(* i ℏ L_y)")],
        
        # Ladder operators
        [parse_sexpr("(a† |n⟩)"), parse_sexpr("(* (sqrt (+ n 1)) |n+1⟩)")],
        [parse_sexpr("(a |n⟩)"), parse_sexpr("(* (sqrt n) |n-1⟩)")],
        [parse_sexpr("(a |0⟩)"), parse_sexpr("0")],
        
        # Number operator
        [parse_sexpr("(N |n⟩)"), parse_sexpr("(* n |n⟩)")],
        
        # Hamiltonian for harmonic oscillator
        [parse_sexpr("H"), parse_sexpr("(* ℏ ω (+ N (/ 1 2)))")],
    ]
    
    print("\nHarmonic Oscillator Energy Levels:")
    
    # Energy eigenvalues
    energy = parse_sexpr("(* ℏ ω (+ n (/ 1 2)))")
    print(f"E_n = {Expression(energy).to_string()}")
    
    # Ground state energy
    ground = parse_sexpr("(* ℏ ω (/ 1 2))")
    print(f"E_0 = {Expression(ground).to_string()}")
    
    print("\nOperator Algebra:")
    
    # Position and momentum in terms of ladder operators
    x_op = parse_sexpr("(* (sqrt (/ ℏ (* 2 m ω))) (+ a a†))")
    p_op = parse_sexpr("(* i (sqrt (/ (* m ℏ ω) 2)) (- a† a))")
    
    print(f"x̂ = {Expression(x_op).to_string()}")
    print(f"p̂ = {Expression(p_op).to_string()}")
    
    # Uncertainty relation
    uncertainty = parse_sexpr("(≥ (* Δx Δp) (/ ℏ 2))")
    print(f"\nUncertainty: {Expression(uncertainty).to_string()}")


def financial_mathematics():
    """Symbolic financial mathematics."""
    print("\n" + "="*60)
    print("FINANCIAL MATHEMATICS: OPTIONS PRICING")
    print("="*60)
    
    # Black-Scholes formula components
    print("\nBlack-Scholes Formula Derivation:")
    
    # Define the PDE
    bs_pde = parse_sexpr("""
        (= (+ (∂V/∂t) 
              (+ (* (/ 1 2) (^ σ 2) (^ S 2) (∂²V/∂S²))
                 (* r S (∂V/∂S))))
           (* r V))
    """.replace('\n', ' '))
    
    print(f"PDE: {Expression(bs_pde).to_string()}")
    
    # Solution for European call
    d1 = parse_sexpr("(/ (+ (log (/ S K)) (* (+ r (/ (^ σ 2) 2)) T)) (* σ (sqrt T)))")
    d2 = parse_sexpr("(- d_1 (* σ (sqrt T)))")
    
    call_price = parse_sexpr("(- (* S (Φ d_1)) (* K (exp (* (- r) T)) (Φ d_2)))")
    
    print(f"\nd₁ = {Expression(d1).to_string()}")
    print(f"d₂ = {Expression(d2).to_string()}")
    print(f"\nCall Price: C = {Expression(call_price).to_string()}")
    
    # Greeks (sensitivities)
    print("\nOption Greeks:")
    
    delta = parse_sexpr("(∂C/∂S)")
    gamma = parse_sexpr("(∂²C/∂S²)")
    theta = parse_sexpr("(∂C/∂t)")
    vega = parse_sexpr("(∂C/∂σ)")
    rho = parse_sexpr("(∂C/∂r)")
    
    print(f"Δ (Delta) = {Expression(delta).to_string()} = Φ(d₁)")
    print(f"Γ (Gamma) = {Expression(gamma).to_string()} = φ(d₁)/(S·σ·√T)")
    print(f"Θ (Theta) = {Expression(theta).to_string()}")
    print(f"ν (Vega) = {Expression(vega).to_string()} = S·φ(d₁)·√T")
    print(f"ρ (Rho) = {Expression(rho).to_string()} = K·T·e^(-rT)·Φ(d₂)")


def machine_learning_gradients():
    """Symbolic computation for machine learning."""
    print("\n" + "="*60)
    print("MACHINE LEARNING: GRADIENT COMPUTATION")
    print("="*60)
    
    print("\nNeural Network Backpropagation:")
    
    # Define a simple neural network
    # Layer 1: z₁ = W₁x + b₁, a₁ = σ(z₁)
    # Layer 2: z₂ = W₂a₁ + b₂, a₂ = σ(z₂)
    # Loss: L = (1/2)||y - a₂||²
    
    # Forward pass
    z1 = parse_sexpr("(+ (* W_1 x) b_1)")
    a1 = parse_sexpr("(σ z_1)")
    z2 = parse_sexpr("(+ (* W_2 a_1) b_2)")
    a2 = parse_sexpr("(σ z_2)")
    loss = parse_sexpr("(* (/ 1 2) (norm² (- y a_2)))")
    
    print(f"z₁ = {Expression(z1).to_string()}")
    print(f"a₁ = {Expression(a1).to_string()}")
    print(f"z₂ = {Expression(z2).to_string()}")
    print(f"a₂ = {Expression(a2).to_string()}")
    print(f"L = {Expression(loss).to_string()}")
    
    # Backward pass (gradient computation)
    print("\nGradients:")
    
    dL_da2 = parse_sexpr("(- a_2 y)")
    da2_dz2 = parse_sexpr("(σ' z_2)")
    dL_dz2 = parse_sexpr("(⊙ (- a_2 y) (σ' z_2))")
    
    dL_dW2 = parse_sexpr("(⊗ δ_2 a_1)")
    dL_db2 = parse_sexpr("δ_2")
    
    dL_da1 = parse_sexpr("(* (transpose W_2) δ_2)")
    dL_dz1 = parse_sexpr("(⊙ (* (transpose W_2) δ_2) (σ' z_1))")
    
    dL_dW1 = parse_sexpr("(⊗ δ_1 x)")
    dL_db1 = parse_sexpr("δ_1")
    
    print(f"∂L/∂a₂ = {Expression(dL_da2).to_string()}")
    print(f"δ₂ = ∂L/∂z₂ = {Expression(dL_dz2).to_string()}")
    print(f"∂L/∂W₂ = {Expression(dL_dW2).to_string()}")
    print(f"∂L/∂b₂ = {Expression(dL_db2).to_string()}")
    
    # Update rules
    print("\nGradient Descent Updates:")
    
    W2_update = parse_sexpr("(- W_2 (* α (∂L/∂W_2)))")
    b2_update = parse_sexpr("(- b_2 (* α (∂L/∂b_2)))")
    
    print(f"W₂ ← {Expression(W2_update).to_string()}")
    print(f"b₂ ← {Expression(b2_update).to_string()}")
    
    # Adam optimizer
    print("\nAdam Optimizer:")
    
    m_t = parse_sexpr("(+ (* β_1 m_{t-1}) (* (- 1 β_1) g_t))")
    v_t = parse_sexpr("(+ (* β_2 v_{t-1}) (* (- 1 β_2) (^ g_t 2)))")
    m_hat = parse_sexpr("(/ m_t (- 1 (^ β_1 t)))")
    v_hat = parse_sexpr("(/ v_t (- 1 (^ β_2 t)))")
    theta_update = parse_sexpr("(- θ_{t-1} (* α (/ m̂_t (+ (sqrt v̂_t) ε))))")
    
    print(f"m_t = {Expression(m_t).to_string()}")
    print(f"v_t = {Expression(v_t).to_string()}")
    print(f"θ_t = {Expression(theta_update).to_string()}")


def cryptography_algebra():
    """Symbolic computation for cryptography."""
    print("\n" + "="*60)
    print("CRYPTOGRAPHY: ALGEBRAIC STRUCTURES")
    print("="*60)
    
    print("\nElliptic Curve Operations:")
    
    # Elliptic curve: y² = x³ + ax + b
    curve = parse_sexpr("(= (^ y 2) (+ (+ (^ x 3) (* a x)) b))")
    print(f"Curve: {Expression(curve).to_string()}")
    
    # Point addition formula
    print("\nPoint Addition P + Q = R:")
    
    # When P ≠ Q
    slope_add = parse_sexpr("(/ (- y_2 y_1) (- x_2 x_1))")
    x3_add = parse_sexpr("(- (- (^ λ 2) x_1) x_2)")
    y3_add = parse_sexpr("(- (* λ (- x_1 x_3)) y_1)")
    
    print(f"λ = {Expression(slope_add).to_string()}")
    print(f"x₃ = {Expression(x3_add).to_string()}")
    print(f"y₃ = {Expression(y3_add).to_string()}")
    
    # Point doubling (P = Q)
    print("\nPoint Doubling 2P:")
    
    slope_double = parse_sexpr("(/ (+ (* 3 (^ x_1 2)) a) (* 2 y_1))")
    x3_double = parse_sexpr("(- (^ λ 2) (* 2 x_1))")
    y3_double = parse_sexpr("(- (* λ (- x_1 x_3)) y_1)")
    
    print(f"λ = {Expression(slope_double).to_string()}")
    print(f"x₃ = {Expression(x3_double).to_string()}")
    print(f"y₃ = {Expression(y3_double).to_string()}")
    
    # Diffie-Hellman key exchange
    print("\nElliptic Curve Diffie-Hellman:")
    
    alice_public = parse_sexpr("(* a G)")  # a is private key, G is generator
    bob_public = parse_sexpr("(* b G)")    # b is private key
    shared_secret = parse_sexpr("(* a (* b G))")
    
    print(f"Alice public: A = {Expression(alice_public).to_string()}")
    print(f"Bob public: B = {Expression(bob_public).to_string()}")
    print(f"Shared secret: S = {Expression(shared_secret).to_string()} = a·B = b·A")
    
    # RSA components
    print("\nRSA Encryption:")
    
    n = parse_sexpr("(* p q)")
    phi = parse_sexpr("(* (- p 1) (- q 1))")
    encrypt = parse_sexpr("(mod (^ m e) n)")
    decrypt = parse_sexpr("(mod (^ c d) n)")
    
    print(f"n = {Expression(n).to_string()}")
    print(f"φ(n) = {Expression(phi).to_string()}")
    print(f"Encrypt: c = {Expression(encrypt).to_string()}")
    print(f"Decrypt: m = {Expression(decrypt).to_string()}")
    print("where e·d ≡ 1 (mod φ(n))")


def generate_latex_document():
    """Generate LaTeX document with symbolic computations."""
    print("\n" + "="*60)
    print("LATEX DOCUMENT GENERATION")
    print("="*60)
    
    # Create a LaTeX document with equations
    doc = r"""
\documentclass{article}
\usepackage{amsmath, amssymb}
\title{Symbolic Computations with XTK}
\author{Generated by XTK}
\begin{document}
\maketitle

\section{Calculus}
"""
    
    # Add derivative examples
    derivatives = [
        ("x^n", parse_sexpr("(^ x n)"), parse_sexpr("(* n (^ x (- n 1)))")),
        ("\\sin(x)", parse_sexpr("(sin x)"), parse_sexpr("(cos x)")),
        ("e^x", parse_sexpr("(exp x)"), parse_sexpr("(exp x)")),
        ("\\ln(x)", parse_sexpr("(log x)"), parse_sexpr("(/ 1 x)")),
    ]
    
    for name, expr, deriv in derivatives:
        doc += f"""
\\subsection{{Derivative of ${name}$}}
\\begin{{align}}
f(x) &= {Expression(expr).to_latex()} \\\\
f'(x) &= {Expression(deriv).to_latex()}
\\end{{align}}
"""
    
    # Add integral examples
    doc += r"""
\section{Integration}
"""
    
    integrals = [
        ("1/x", parse_sexpr("(/ 1 x)"), parse_sexpr("(log (abs x))")),
        ("x^n", parse_sexpr("(^ x n)"), parse_sexpr("(/ (^ x (+ n 1)) (+ n 1))")),
        ("\\sin(x)", parse_sexpr("(sin x)"), parse_sexpr("(- (cos x))")),
    ]
    
    for name, expr, integral in integrals:
        doc += f"""
\\subsection{{Integral of ${name}$}}
\\begin{{align}}
\\int {Expression(expr).to_latex()} \\, dx = {Expression(integral).to_latex()} + C
\\end{{align}}
"""
    
    doc += r"""
\end{document}
"""
    
    print("Generated LaTeX document:")
    print(doc[:500] + "...")
    
    # Save to file
    with open("examples/generated_math.tex", "w") as f:
        f.write(doc)
    print("\nSaved to: examples/generated_math.tex")


def main():
    """Run all symbolic workflow examples."""
    print("="*60)
    print("SYMBOLIC COMPUTATION WORKFLOWS WITH XTK")
    print("="*60)
    print("\nDemonstrating practical applications of symbolic")
    print("computation across various domains.")
    
    physics_kinematics()
    engineering_control_systems()
    quantum_mechanics()
    financial_mathematics()
    machine_learning_gradients()
    cryptography_algebra()
    generate_latex_document()
    
    print("\n" + "="*60)
    print("These workflows show how XTK can be used for")
    print("real-world symbolic computation tasks.")
    print("="*60)


if __name__ == "__main__":
    main()