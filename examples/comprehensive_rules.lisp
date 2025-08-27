;;;; Comprehensive Rule Library for XTK
;;;; ====================================
;;;; A collection of sophisticated rewrite rules for various
;;;; mathematical domains, expressed in Lisp DSL syntax.

;;; ============================================================
;;; ALGEBRAIC IDENTITIES AND TRANSFORMATIONS
;;; ============================================================

;; Binomial expansion rules
((^ (+ (? a) (? b)) 2)
 (+ (+ (^ (: a) 2) (* 2 (* (: a) (: b)))) (^ (: b) 2)))

((^ (- (? a) (? b)) 2)
 (+ (- (^ (: a) 2) (* 2 (* (: a) (: b)))) (^ (: b) 2)))

((^ (+ (? a) (? b)) 3)
 (+ (+ (+ (^ (: a) 3) (* 3 (* (^ (: a) 2) (: b))))
       (* 3 (* (: a) (^ (: b) 2))))
    (^ (: b) 3)))

;; Difference of powers
((- (^ (? a) n) (^ (? b) n))
 (* (- (: a) (: b)) 
    (sum (^ (: a) i) (^ (: b) (- n i 1)) i 0 (- n 1))))

;; Logarithm properties
((log (* (? a) (? b)))
 (+ (log (: a)) (log (: b))))

((log (/ (? a) (? b)))
 (- (log (: a)) (log (: b))))

((log (^ (? a) (? n)))
 (* (: n) (log (: a))))

((log_a (? x))
 (/ (log (: x)) (log a)))

;; Exponential properties
((exp (+ (? a) (? b)))
 (* (exp (: a)) (exp (: b))))

((exp (* (? n) (log (? x))))
 (^ (: x) (: n)))

((^ a (log_a (? x)))
 (: x))

;;; ============================================================
;;; TRIGONOMETRIC IDENTITIES
;;; ============================================================

;; Pythagorean identities
((+ (^ (sin (? θ)) 2) (^ (cos (? θ)) 2))
 1)

((+ 1 (^ (tan (? θ)) 2))
 (^ (sec (: θ)) 2))

((+ 1 (^ (cot (? θ)) 2))
 (^ (csc (: θ)) 2))

;; Double angle formulas
((sin (* 2 (? θ)))
 (* 2 (* (sin (: θ)) (cos (: θ)))))

((cos (* 2 (? θ)))
 (- (^ (cos (: θ)) 2) (^ (sin (: θ)) 2)))

((cos (* 2 (? θ)))
 (- (* 2 (^ (cos (: θ)) 2)) 1))

((cos (* 2 (? θ)))
 (- 1 (* 2 (^ (sin (: θ)) 2))))

((tan (* 2 (? θ)))
 (/ (* 2 (tan (: θ))) (- 1 (^ (tan (: θ)) 2))))

;; Half angle formulas
((sin (/ (? θ) 2))
 (* (sign (sin (: θ))) (sqrt (/ (- 1 (cos (: θ))) 2))))

((cos (/ (? θ) 2))
 (* (sign (cos (: θ))) (sqrt (/ (+ 1 (cos (: θ))) 2))))

((tan (/ (? θ) 2))
 (/ (sin (: θ)) (+ 1 (cos (: θ)))))

;; Sum and difference formulas
((sin (+ (? α) (? β)))
 (+ (* (sin (: α)) (cos (: β))) (* (cos (: α)) (sin (: β)))))

((sin (- (? α) (? β)))
 (- (* (sin (: α)) (cos (: β))) (* (cos (: α)) (sin (: β)))))

((cos (+ (? α) (? β)))
 (- (* (cos (: α)) (cos (: β))) (* (sin (: α)) (sin (: β)))))

((cos (- (? α) (? β)))
 (+ (* (cos (: α)) (cos (: β))) (* (sin (: α)) (sin (: β)))))

;; Product to sum formulas
((* (sin (? α)) (sin (? β)))
 (/ (- (cos (- (: α) (: β))) (cos (+ (: α) (: β)))) 2))

((* (cos (? α)) (cos (? β)))
 (/ (+ (cos (- (: α) (: β))) (cos (+ (: α) (: β)))) 2))

((* (sin (? α)) (cos (? β)))
 (/ (+ (sin (+ (: α) (: β))) (sin (- (: α) (: β)))) 2))

;;; ============================================================
;;; HYPERBOLIC FUNCTION IDENTITIES
;;; ============================================================

;; Basic definitions
((sinh (? x))
 (/ (- (exp (: x)) (exp (- (: x)))) 2))

((cosh (? x))
 (/ (+ (exp (: x)) (exp (- (: x)))) 2))

((tanh (? x))
 (/ (sinh (: x)) (cosh (: x))))

;; Hyperbolic Pythagorean identity
((- (^ (cosh (? x)) 2) (^ (sinh (? x)) 2))
 1)

;; Addition formulas
((sinh (+ (? x) (? y)))
 (+ (* (sinh (: x)) (cosh (: y))) (* (cosh (: x)) (sinh (: y)))))

((cosh (+ (? x) (? y)))
 (+ (* (cosh (: x)) (cosh (: y))) (* (sinh (: x)) (sinh (: y)))))

;;; ============================================================
;;; COMPLEX NUMBER OPERATIONS
;;; ============================================================

;; Euler's formula
((exp (* i (? θ)))
 (+ (cos (: θ)) (* i (sin (: θ)))))

;; De Moivre's theorem
((^ (+ (cos (? θ)) (* i (sin (? θ)))) (? n))
 (+ (cos (* (: n) (: θ))) (* i (sin (* (: n) (: θ))))))

;; Complex conjugate properties
((conj (+ (? a) (* i (? b))))
 (- (: a) (* i (: b))))

((* (? z) (conj (? z)))
 (norm² (: z)))

;; Complex division
((/ (? z1) (? z2))
 (/ (* (: z1) (conj (: z2))) (norm² (: z2))))

;;; ============================================================
;;; CALCULUS RULES
;;; ============================================================

;; Integration by parts
((integrate (* (? u) (dd (? v) x)) x)
 (- (* (: u) (: v)) (integrate (* (: v) (dd (: u) x)) x)))

;; Substitution rule
((integrate (? f (? g)) x)
 (integrate (/ (: f) (dd (: g) x)) (: g)))

;; Fundamental theorem of calculus
((dd (integrate (? f) x a x) x)
 (: f))

;; Taylor series expansions
((taylor (exp (? x)) (? x) 0 ∞)
 (sum (/ (^ (: x) n) (factorial n)) n 0 ∞))

((taylor (sin (? x)) (? x) 0 ∞)
 (sum (* (^ -1 n) (/ (^ (: x) (+ (* 2 n) 1)) 
                     (factorial (+ (* 2 n) 1)))) n 0 ∞))

((taylor (cos (? x)) (? x) 0 ∞)
 (sum (* (^ -1 n) (/ (^ (: x) (* 2 n)) 
                     (factorial (* 2 n)))) n 0 ∞))

((taylor (log (+ 1 (? x))) (? x) 0 ∞)
 (sum (* (^ -1 (+ n 1)) (/ (^ (: x) n) n)) n 1 ∞))

;; L'Hôpital's rule
((limit (/ (? f) (? g)) x a)
 (if (= (limit (: f) x a) (limit (: g) x a) 0)
     (limit (/ (dd (: f) x) (dd (: g) x)) x a)
     (/ (limit (: f) x a) (limit (: g) x a))))

;;; ============================================================
;;; LINEAR ALGEBRA RULES
;;; ============================================================

;; Matrix operations
((transpose (transpose (? A)))
 (: A))

((transpose (+ (? A) (? B)))
 (+ (transpose (: A)) (transpose (: B))))

((transpose (* (? A) (? B)))
 (* (transpose (: B)) (transpose (: A))))

((det (transpose (? A)))
 (det (: A)))

((det (* (? A) (? B)))
 (* (det (: A)) (det (: B))))

((det (^ (? A) (? n)))
 (^ (det (: A)) (: n)))

;; Inverse properties
((inverse (inverse (? A)))
 (: A))

((inverse (* (? A) (? B)))
 (* (inverse (: B)) (inverse (: A))))

((* (? A) (inverse (? A)))
 I)

;; Eigenvalue properties
((trace (? A))
 (sum λ_i i 1 n))

((det (? A))
 (product λ_i i 1 n))

;;; ============================================================
;;; DIFFERENTIAL GEOMETRY
;;; ============================================================

;; Metric tensor operations
((g^{ij} g_{jk})
 δ^i_k)

;; Covariant derivative
((∇_μ (? V^ν))
 (+ (∂_μ (: V^ν)) (* Γ^ν_{μρ} (: V^ρ))))

((∇_μ (? V_ν))
 (- (∂_μ (: V_ν)) (* Γ^ρ_{μν} (: V_ρ))))

;; Riemann tensor symmetries
((R_{ijkl})
 (- R_{jikl}))

((R_{ijkl})
 (- R_{ijlk}))

((R_{ijkl})
 R_{klij})

;; Bianchi identity
((+ (+ (∇_m R_{ijkl}) (∇_k R_{ijlm})) (∇_l R_{ijmk}))
 0)

;;; ============================================================
;;; NUMBER THEORY RULES
;;; ============================================================

;; Euler's theorem
((mod (^ (? a) (φ (? n))) (? n))
 1)  ; when gcd(a,n) = 1

;; Fermat's little theorem
((mod (^ (? a) (? p)) (? p))
 (mod (: a) (: p)))  ; when p is prime

;; Wilson's theorem
((mod (factorial (- (? p) 1)) (? p))
 (- (: p) 1))  ; when p is prime

;; Quadratic reciprocity
((legendre p q)
 (* (^ -1 (/ (* (- p 1) (- q 1)) 4)) (legendre q p)))

;;; ============================================================
;;; COMBINATORICS
;;; ============================================================

;; Binomial coefficient identities
((choose n 0)
 1)

((choose n n)
 1)

((choose n k)
 (choose n (- n k)))

((choose n k)
 (/ (factorial n) (* (factorial k) (factorial (- n k)))))

;; Pascal's identity
((choose n k)
 (+ (choose (- n 1) (- k 1)) (choose (- n 1) k)))

;; Vandermonde's identity
((choose (+ m n) r)
 (sum (* (choose m k) (choose n (- r k))) k 0 r))

;;; ============================================================
;;; SPECIAL FUNCTIONS
;;; ============================================================

;; Gamma function properties
((Γ (+ (? n) 1))
 (* (: n) (Γ (: n))))

((Γ (? n))
 (factorial (- (: n) 1)))  ; for positive integers

((Γ (/ 1 2))
 (sqrt π))

;; Beta function
((B (? x) (? y))
 (/ (* (Γ (: x)) (Γ (: y))) (Γ (+ (: x) (: y)))))

;; Riemann zeta function special values
((ζ 2)
 (/ (^ π 2) 6))

((ζ 4)
 (/ (^ π 4) 90))

((ζ -1)
 (- (/ 1 12)))

;; Bessel function recurrence
((J_{n+1} (? x))
 (- (/ (* 2 n (J_n (: x))) (: x)) (J_{n-1} (: x))))

;;; ============================================================
;;; OPTIMIZATION AND VARIATIONAL CALCULUS
;;; ============================================================

;; Euler-Lagrange equation
((δ (∫ L(x, ẋ, t) dt))
 (- (∂L/∂x) (dd (∂L/∂ẋ) t)))

;; Hamilton's equations
((ṗ)
 (- (∂H/∂q)))

((q̇)
 (∂H/∂p))

;; Lagrangian to Hamiltonian
((H)
 (- (* p q̇) L))

;;; ============================================================
;;; QUANTUM FIELD THEORY
;;; ============================================================

;; Commutation relations
(([φ(x,t), π(y,t)])
 (* i δ(- x y)))

;; Feynman propagator
((D_F(x-y))
 (∫ (/ (exp (* i p (- x y))) (- (^ p 2) (^ m 2) (* i ε))) d⁴p))

;; Wick's theorem
((T (? φ_1) (? φ_2))
 (+ (normal (: φ_1) (: φ_2)) (contraction (: φ_1) (: φ_2))))

;;; ============================================================
;;; CATEGORY THEORY AND ABSTRACT ALGEBRA
;;; ============================================================

;; Functor composition
((∘ (? F) (? G))
 (functor x (apply (: F) (apply (: G) x))))

;; Natural transformation
((η : F ⇒ G)
 (∀ f : A → B, (∘ (G f) (η_A)) = (∘ (η_B) (F f))))

;; Monad laws
((>>= (return (? x)) (? k))
 (apply (: k) (: x)))

((>>= (? m) return)
 (: m))

((>>= (>>= (? m) (? k)) (? h))
 (>>= (: m) (λ x (>>= (apply (: k) x) (: h)))))

;; Yoneda lemma
((hom(A, -))
 (functor B (hom A B)))

;;; ============================================================
;;; END OF COMPREHENSIVE RULES
;;; ============================================================